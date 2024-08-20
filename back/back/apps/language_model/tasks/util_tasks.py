import os

import ray

from logging import getLogger

logger = getLogger(__name__)

@ray.remote(num_cpus=0.001)
def get_filesystem(storages_mode):
    """
    For Digital Ocean, we need to provide a custom filesystem object to write the index to the cloud storage
    """
    from pyarrow import fs
    from ray.data.datasource import _S3FileSystemWrapper

    if storages_mode == "do":
        
        endpoint_url = f'https://{os.environ.get("DO_REGION")}.digitaloceanspaces.com'
        s3fs = fs.S3FileSystem(
            access_key=os.environ.get("AWS_ACCESS_KEY_ID"),
            secret_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            endpoint_override=endpoint_url,
        )

        # This is a hack to make the S3FileSystem object serializable (https://github.com/ray-project/ray/pull/17103)
        s3fs = _S3FileSystemWrapper(s3fs)

        print("Using Digital Ocean S3 filesystem")

        return s3fs

    # If None ray data autoinfers the filesystem
    return None


@ray.remote(num_cpus=1)
def read_s3_index(index_path, storages_mode):
    """
    If the index_path is an S3 path, read the index from object storage and write it to the local storage.
    """
    fs_ref = get_filesystem.remote(storages_mode)

    from tqdm import tqdm

    def write_file(row, base_path):
        # Extract bytes and path from the row
        content, file_path = row["bytes"], row["path"]

        file_name = os.path.basename(file_path)

        # Combine the base path with the original file path
        full_path = os.path.join(base_path, file_name)

        print(f"Writing file to {full_path}")

        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write the file
        with open(full_path, "wb") as file:
            file.write(content)

    print(f"Reading index from {index_path}")

    from pyarrow.fs import FileSelector

    fs = ray.get(fs_ref)

    if fs is not None:
        # unwrap the filesystem object
        fs = fs.unwrap()

    files = fs.get_file_info(FileSelector(index_path.split('s3://')[1]))

    file_paths = [file.path for file in files]

    # print total index size in MB
    print(f"Downloading index with size: {sum(file.size for file in files) / 1e9:.3f} GB")

    # TODO: Maybe pass the Memory resource requirement with the index size so if you have not enough memory it will not download the index
    # If the index is too large, issue an error asking the user to increase the memory resources
    index = ray.data.read_parquet_bulk(file_paths, filesystem=fs)
    print(f"Downloaded {index.count()} files from S3")

    index_name = os.path.basename(index_path)
    index_path = os.path.join("back", "indexes", "colbert", "indexes", index_name)

    # if the directory exists, delete it
    if os.path.exists(index_path):
        print(f"Deleting existing index at {index_path}")
        import shutil
        shutil.rmtree(index_path)

    print(f"Writing index to {index_path}")
    for row in tqdm(index.iter_rows()):
        write_file(row, index_path)
    return index_path


@ray.remote(num_cpus=1, resources={"tasks": 1})
def test_task(argument_one):
    from logging import getLogger
    import django
    import os
    import time
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "back.config.settings")

    t1 = time.perf_counter()
    django.setup()
    print(f"Django setup complete in {time.perf_counter() - t1:.2f}s.")

    print("with arg: ", argument_one, "start")
    print("with arg: ", argument_one, "finished")

    logger2 = getLogger(__name__)

    logger.info('#'*50)
    logger.warning('>'*50)
    logger2.info('*'*50)
    logger2.warning('$'*50)

    from back.apps.language_model.models import LLMConfig
    print("Number of LLMConfig: ", LLMConfig.objects.all().count())     

    import time

    time.sleep(10)

    return LLMConfig.objects.all().count()
