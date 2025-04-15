from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_mistralai import MistralAIEmbeddings
from langchain_core.documents import Document
from langchain_core.runnables import chain

from dotenv import load_dotenv
import os
from typing import List

# --------------------------- Load Environment Variables -----------------------------
load_dotenv()

# (Optional) HuggingFace token to avoid tokenizer warning
# You can add this to your .env file as: HF_TOKEN=your_token_here
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token

# --------------------------- Main Script --------------------------------------------
if __name__ == "__main__":
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_api_key:
        raise EnvironmentError("MISTRAL API KEY not found in environment variables.")
    print("Mistral API Key loaded successfully.")

    # Load and Read PDF File
    pdf_url = "https://s1.q4cdn.com/806093406/files/doc_downloads/2023/414759-1-_5_Nike-NPS-Combo_Form-10-K_WR.pdf"
    pdf_reader = PyPDFLoader(pdf_url)
    documents = pdf_reader.load()

    #Text Chunking
    chunker = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = chunker.split_documents(documents)

    # Generate Embeddings
    embedding_model = MistralAIEmbeddings(model="mistral-embed", api_key=mistral_api_key)

    # Optional vector shape check
    sample_vector_1 = embedding_model.embed_query(chunks[0].page_content)
    sample_vector_2 = embedding_model.embed_query(chunks[1].page_content)

    assert len(sample_vector_1) == len(sample_vector_2), "Embedding sizes do not match"
    print(f"Vector size: {len(sample_vector_1)}")

    #  Create Vector Store
    vector_db = InMemoryVectorStore(embedding_model)
    doc_ids = vector_db.add_documents(documents=chunks)

    # Query Example
    query_text = "How many distribution centers does Nike have in the US?"
    matched_docs = vector_db.similarity_search(query_text)

    print("\nTop matched content:\n", matched_docs[0].page_content)

    # Batch Retrieval Chain
    @chain
    def search_documents(user_query: str) -> List[Document]:
        return vector_db.similarity_search(user_query, k=1)

    batch_queries = [
        "How many distribution centers does Nike have in the US?",
        "When was Nike incorporated?"
    ]

    results = search_documents.batch(batch_queries)
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:\n{result[0].page_content}")
