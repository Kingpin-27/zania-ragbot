from llama_parse import LlamaParse
from llama_index.core import (
    VectorStoreIndex,
    Document,
    Settings,
    StorageContext,
)
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.kdbai import KDBAIVectorStore
from llama_index.postprocessor.cohere_rerank import CohereRerank
from slack_sdk import WebClient
from constants import (
    OPENAI_API_KEY,
    COHERE_API_KEY,
    LLAMA_CLOUD_API_KEY,
    KDBAI_API_KEY,
    KDBAI_ENDPOINT,
    KDBAI_TABLE_NAME,
    GENERATION_MODEL,
    SLACK_CLIENT_SECRET,
    EMBEDDING_MODEL,
)
from typing import List
import kdbai_client as kdbai
import os
import nest_asyncio

nest_asyncio.apply()

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["COHERE_API_KEY"] = COHERE_API_KEY
os.environ["LLAMA_CLOUD_API_KEY"] = LLAMA_CLOUD_API_KEY


def initialize_vector_store_and_storage_context() -> StorageContext:
    session = kdbai.Session(api_key=KDBAI_API_KEY, endpoint=KDBAI_ENDPOINT)

    schema = dict(
        columns=[
            dict(name="document_id", pytype="bytes"),
            dict(name="text", pytype="bytes"),
            dict(
                name="embedding",
                vectorIndex=dict(type="flat", metric="L2", dims=1536),
            ),
        ]
    )

    # First ensure the table does not already exist
    if KDBAI_TABLE_NAME in session.list():
        session.table(KDBAI_TABLE_NAME).drop()

    # Create the table
    table = session.create_table(KDBAI_TABLE_NAME, schema)
    vector_store = KDBAIVectorStore(table)
    return StorageContext.from_defaults(vector_store=vector_store)


def get_parsed_documents(current_file_path: str) -> List[Document]:
    parsing_instructions = """This document contains many tables and graphs. Answer questions using the information in this article and be precise."""
    return LlamaParse(
        result_type="markdown", parsing_instructions=parsing_instructions
    ).load_data(current_file_path)


def get_rag_query_engine(current_file_path: str) -> BaseQueryEngine:
    llm = OpenAI(model=GENERATION_MODEL)
    embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL)

    Settings.llm = llm
    Settings.embed_model = embed_model

    documents = get_parsed_documents(current_file_path)

    # Parse the documents using MarkdownElementNodeParser
    node_parser = MarkdownElementNodeParser(llm=llm, num_workers=8).from_defaults()

    # Retrieve nodes (text) and objects (table)
    nodes = node_parser.get_nodes_from_documents(documents)

    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

    storage_context = initialize_vector_store_and_storage_context()
    # Create the index, inserts base_nodes and objects into KDB.AI
    recursive_index = VectorStoreIndex(
        nodes=base_nodes + objects, storage_context=storage_context
    )

    ### Define reranker
    cohere_rerank = CohereRerank(top_n=10)

    ### Create the query_engine to execute RAG pipeline using LlamaIndex, KDB.AI, and Cohere reranker
    query_engine = recursive_index.as_query_engine(
        similarity_top_k=15, node_postprocessors=[cohere_rerank]
    )

    return query_engine


def query_doc(queries: List[str], file_path: str, post_in_slack: bool):
    query_engine = get_rag_query_engine(file_path)
    final_response_list = []
    for query in queries:
        modified_query = f"{query}. If you can't answer using provided context information, reply with 'Data Not Available'"
        answer = query_engine.query(modified_query)
        final_response_list.append({"query": query, "answer": answer.response})

        if post_in_slack:
            client = WebClient(token=SLACK_CLIENT_SECRET)
            message = f"*User Query:* {query}\n*AI Response:* {answer.response}"
            # Send a message
            client.chat_postMessage(
                channel="testing", text=message, username="Zania Rag Bot"
            )

    return final_response_list
