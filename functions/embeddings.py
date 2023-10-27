
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.schema.document import Document
from utils.config_loader import ConfigLoader
from schema.schemas import Timestamp

class Embeddings:
    def __init__(self, config_file='config/configuration.toml'):
        # Load the configuration
        self.config_loader = ConfigLoader(config_file)
        openai_config = self.config_loader.get_openai_config()
        
        # TODO: test/change to LLama2 Embeddings model:
        # https://medium.com/@liusimao8/using-llama-2-models-for-text-embedding-with-langchain-79183350593d

        # Initialize OpenAIEmbeddings with values from config
        self.model = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=openai_config.get('API_KEY')  # Get API key from configuration
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            # TODO: make sure this confirms with the chunking strategy
            chunk_size = 1000,
            chunk_overlap  = 20,
            length_function = len,
            add_start_index = True,
        )


    def create_documents(self, text):
        # Load documents
        # TODO: at a later points, the text splitter should be replaced with the iterative chunker
        # documents = self.text_splitter.create_documents([documents])
        # INFO: for now, we just create a single document
        # check if text is a list
        def create_document(text):
            return Document(
                page_content=text,
                metadata={
                    "start_index": 0,
                    "end_index": len(text),
                    "last_indexed": Timestamp().now
                }
            )
        
        if isinstance(text, list):
            documents = [create_document(t) for t in text]
        else:
            documents = [create_document(text)]
        return documents
        

    def split_documents(self, documents):
        # Chunk documents into smaller pieces
        documents = self.get_documents(documents)
        chunks = self.text_splitter.split_documents(documents)
        return chunks


    def get_embeddings(self, text):
        return self.model.embed_query(text)
