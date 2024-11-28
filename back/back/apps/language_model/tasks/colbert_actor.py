from typing import Optional
import os

import ray
from ray.util.scheduling_strategies import NodeAffinitySchedulingStrategy

from back.apps.language_model.tasks import read_s3_index, get_filesystem
from back.utils.ray_utils import ray_task


@ray_task(num_cpus=1, resources={"tasks": 1})
class ColBERTActor:
    def __init__(self, index_path: str, device: str = 'cpu', colbert_name: Optional[str] = None, storages_mode: str = None):

        import os
        
        self.index_path = index_path
        self.colbert_name = colbert_name
        self.device = device
        self.n_gpus = -1 if self.device == "cpu" else self.get_num_gpus()
        self.storages_mode = storages_mode

        self.index_root, self.index_name = os.path.split(index_path)

        if colbert_name is not None:
            self.load_pretrained()
        else:
            self.load_index()

    def __repr__(self) -> str:
        return f"ColBERTActor(index_path={self.index_path}, colbert_name={self.colbert_name})"

    def load_pretrained(self):
        """
        Load a pretrained ColBERT model without an index.
        """
        from ragatouille import RAGPretrainedModel

        self.retriever = RAGPretrainedModel.from_pretrained(
            self.colbert_name, index_root=self.index_root, n_gpu=self.n_gpus
        )
    
    def load_index(self):
        """
        Load a ColBERT model from an existing index.
        """
        from ragatouille import RAGPretrainedModel

        if 's3://' in self.index_path:    
            node_id = ray.get_runtime_context().get_node_id()
            print(f"Node ID: {node_id}")
            node_scheduling_strategy = NodeAffinitySchedulingStrategy(
                node_id=node_id, soft=False
            )
            local_index_path_ref = read_s3_index.options(scheduling_strategy=node_scheduling_strategy).remote(self.index_path, self.storages_mode)
            self.local_index_path = ray.get(local_index_path_ref)
        else:
            self.local_index_path = self.index_path

        self.retriever = RAGPretrainedModel.from_index(self.local_index_path, n_gpu=self.n_gpus)

    def get_num_gpus(self):
        try:
            import torch

            return torch.cuda.device_count()
        except:
            return -1
        
    def index(self, contents, contents_pk, bsize=32):
        """
        Index a collection of documents.
        """
        self.local_index_path = self.retriever.index(
            index_name=self.index_name,
            collection=contents,
            document_ids=contents_pk,
            split_documents=True,
            max_document_length=512,
            bsize=bsize,
        )
    
    def delete_from_index(self, k_item_ids_to_remove):
        """
        Delete items from the index.
        """

        print("Deleting items from the index")
        self.retriever.delete_from_index(
            document_ids=k_item_ids_to_remove,
            index_name=self.index_name,
        )
        print("Done!")

    def add_to_index(self, contents_to_add, contents_pk_to_add, bsize=32):
        """
        Add new items to the index.
        """
        print("Adding new items to the index")
        self.retriever.add_to_index(
            new_collection=contents_to_add,
            new_document_ids=contents_pk_to_add,
            index_name=self.index_name,
            split_documents=True,
            bsize=bsize,
        )
        print("Done!")

    def save_index(self, new_index_path: Optional[str] = None):
        """
        Save the index to the cloud storage.
        Parameters
        ----------
        new_index_path : str
            If provided, save the index to this new path, otherwise save it to the original path.
        """

        from ray.data.datasource import FilenameProvider

        class PidDocIdFilenameProvider(FilenameProvider):
            """
            Custom filename provider for the index to keep the original filenames, instead of the ray.data generated filenames.
            """
            def get_filename_for_row(self, row, task_index, block_index, row_index):
                path = row['path']

                filename = os.path.basename(path)
                filename = os.path.splitext(filename)[0] + f"_{self._dataset_uuid}_"
                file_id = f"{task_index:06}_{block_index:06}_{row_index:06}.parquet"
                filename += file_id

                return filename
            
            def get_filename_for_block(self, block, task_index: int, block_index: int) -> str:

                path = str(block['path'][0])

                filename = os.path.basename(path)
                filename = os.path.splitext(filename)[0] + "_"
                file_id = f"{task_index:06}_{block_index:06}.parquet"
                filename += file_id
                
                return filename

        try:
            print("Saving index...")

            remote_index_path = self.index_path if new_index_path is None else new_index_path

            if "s3://" in remote_index_path:
                fs_ref = get_filesystem.remote(self.storages_mode)

                print('Reading index from local storage')
                # Update the index path to use the unique index path
                ray_local_index_path = 'local://' + os.path.join(os.getcwd(), self.retriever.model.index_path)
                index = ray.data.read_binary_files(ray_local_index_path, include_paths=True)

                print(f"Writing index to object storage {remote_index_path}")
                print(f'Size of index: {index.size_bytes()/1e9:.2f} GB')

                fs = ray.get(fs_ref)
                if fs is not None:
                    # unwrap the filesystem object
                    fs = fs.unwrap()
                # Then we can write the index to the cloud storage
                index.write_parquet(remote_index_path, filesystem=fs, filename_provider=PidDocIdFilenameProvider())
                print('Index written to object storage')

            return True
        
        except Exception as e:
            print(f"Error saving index: {e}")
            return False
        
    def exit(self):
        ray.actor.exit_actor()
