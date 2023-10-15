from langchain.document_loaders import WikipediaLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Neo4jVector
from langchain.embeddings.openai import OpenAIEmbeddings

# Define chunking strategy
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000, chunk_overlap=20
)

texts = [
    "A fast tan fox leaps over the sluggish dogs",
    "A speedy brown fox vaults over the lazy foxes",
    "The rapid brown fox hurdles over the idle banana",
    "The brisk brown fox jumps past the lethargic hound",
    "The agile brown fox springs over the inactive mountains",
    "Lorem ipsum dolor sit, while conducting the act of adorning"
]


# Chunk the document
documents = text_splitter.create_documents(texts)

# print(documents)

neo4j_db = Neo4jVector.from_documents(
    documents,
    OpenAIEmbeddings(),
    url="bolt+s://dev.metasphere.xyz:21001",
    username='neo4j',
    password='KWU_phr.qyk*wre9yhf',
    database="neo4j",  # neo4j by default
    index_name="Spans",  # vector by default
    node_label="Span",  # Chunk by default
    text_node_property="text",  # text by default
    embedding_node_property="vector",  # embedding by default
    create_id_index=True,  # True by default
)