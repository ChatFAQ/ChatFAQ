from ragatouille import RAGPretrainedModel
from ragatouille.utils import get_wikipedia_page
import pandas as pd


if __name__=='__main__':


    df = pd.read_csv('../chat_rag/data/with_madrid.csv')
    N = 30
    M = 40

    docs = df['content'].to_list()

    my_documents = docs[:N]
    document_ids = [str(i) for i in range(N)]

    print(len(my_documents))
    print(len(document_ids))

    new_documents = docs[N:M]
    new_document_ids = [str(i) for i in range(N, M)]
    print(len(new_documents))
    print(len(new_document_ids))

    RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0", index_root="data/")
    #my_documents = [get_wikipedia_page("Hayao_Miyazaki")]


    index_path = RAG.index(index_name="my_index", collection=my_documents, document_ids=document_ids, split_documents=False)

    print(f"Index built at {index_path}")

    RAG = RAGPretrainedModel.from_index(index_path=index_path)

    RAG.add_to_index(new_collection=new_documents, index_name="my_index", new_document_ids=new_document_ids, split_documents=False)