import sys
from langchain.vectorstores import Neo4jVector
from utils.error_handler import ErrorHandler as error_handler
from utils.config_loader import ConfigLoader as config
from langchain.schema import Document

from functions.embeddings import Embeddings

class VectorStore:
    def __init__(
            self, 
            index_name=None, 
            node_label=None,  
            graph=None
        ):
        self.graph = graph
        self.error_handler = error_handler()
        self.config = config()
        self.neo4j_config = config().get_neo4j_config()
        self.embeddings = Embeddings()
        self.embeddings_model = self.embeddings.model
        self.vector_index = self.select_vector_store(index_name=index_name, node_label=node_label)
        self.error_handler.inspect_object(self.vector_index)

    def initialize_vector_store(
            self, 
            index_name=None, 
            node_label=None
        ):
        if index_name:
            node_label = index_name
            try:
                self.vector_index = Neo4jVector.from_existing_index(
                    embedding=self.embeddings_model,
                    username=self.neo4j_config['USER'],
                    password=self.neo4j_config['PASSWORD'],
                    url=self.neo4j_config['URI'],
                    database=self.neo4j_config['DATABASE'],
                    embedding_node_property="embedding",
                    index_name=index_name,
                    node_label=node_label,
                )
                self.error_handler.success(f"Initialized vector store with index {index_name} and label {node_label}")
            except Exception as e:
                self.error_handler.warning(f"Error initializing vector store with index {index_name}")
                self.error_handler.debug_info(f"{e}")
                if "index name does not exist" in str(e):
                # Initialize emtpy vector store to make sure the index is created
                    self.error_handler.debug_info(f"Initializing empty vector store for index {index_name}")
                    try:
                        self.vector_index = Neo4jVector.from_documents(
                            documents=[
                                Document(
                                    page_content=" ",
                                )
                            ],
                            embedding=self.embeddings_model,
                            username=self.neo4j_config['USER'],
                            password=self.neo4j_config['PASSWORD'],
                            url=self.neo4j_config['URI'],
                            database=self.neo4j_config['DATABASE'],  # neo4j by default
                            embedding_node_property="embedding",  # embedding by default
                            index_name=index_name,
                            node_label=node_label,
                        )
                        return self.vector_index
                    
                    except Exception as e:
                        self.error_handler.warning(f"Error initializing empty vector store for index {index_name}: {e}")
                        self.error_handler.exception(sys.exc_info())
                        return None
        else:
            self.error_handler.debug_info(f"Initializing default vector store")
            self.vector_index = Neo4jVector.from_texts(
                texts=[],
                embedding=self.embeddings_model,
                username=self.neo4j_config['USER'],
                password=self.neo4j_config['PASSWORD'],
                url=self.neo4j_config['URI'],
                database=self.neo4j_config['DATABASE'],  # neo4j by default
                embedding_node_property="embedding",  # embedding by default
                index_name="vector",  # vector by default
            )
        return self.vector_index
    
    def select_vector_store(
            self, 
            index_name=None, 
            node_label=None
        ):

        try:
            vector_index = self.vector_index
        except AttributeError:
            vector_index = None

        if not index_name:
            if node_label:
                index_name = node_label
            else:
                index_name = "vector"

        if vector_index:
            if vector_index.index_name != index_name:
                self.error_handler.debug_info(f"Different vector store was requested.")
                self.error_handler.debug_info(f"Current vector store: {vector_index.index_name}")
                self.error_handler.debug_info(f"Loading vector store with index [green]{index_name}[/green]")
                self.vector_index = self.initialize_vector_store(index_name=index_name, node_label=node_label)
            else:
                # self.error_handler.debug_info(f"Requested vector store is already loaded: [green]{self.vector_index.index_name}[/green]")
                self.error_handler.debug_info(f"Requested vector store is already loaded: [green]{self.vector_index.index_name}[/green]")
        else:
            self.error_handler.debug_info(f"Loading vector store with index [green]{index_name}[/green]")
            try:
                self.vector_index = self.initialize_vector_store(index_name=index_name, node_label=node_label)
            except Exception as e:
                self.error_handler.warning(f"Error loading vector store with index {index_name}: {e}")
                self.error_handler.exception(sys.exc_info())
                return None
            self.error_handler.debug_info(f"Loaded vector store with index [green]{self.vector_index.index_name}[/green]")

        if self.vector_index:
            return self.vector_index
        else:
            return None

    
    def add_documents_from_text(
            self,
            text,
            node_label="Chunk",
            index_name=None,
            text_node_property="text",
            embedding_node_property="embedding",
            create_id_index=True,
            force=False
        ):

        self.error_handler.debug_info(f"--- Inside function {sys._getframe().f_code.co_name}")
        self.vector_store = self.select_vector_store(index_name=index_name, node_label=node_label)            

        if not index_name:
            index_name = node_label

        if not isinstance(text, list):
            text = [text]

        documents = Embeddings().create_documents(text)
        created_nodes = []

        for document in documents:
            node = None
            try:
                node = self.graph.find_nodes_by_properties(
                    {text_node_property: document.page_content},
                    label=node_label,
                )[0]
            except IndexError:
                pass

            if node:
                self.error_handler.debug_info(f"Node already exists")
                created_nodes.append(node.id)  # Use the ID of the existing node
            else:
                new_node_id = self.vector_index.add_documents(
                    [document],
                    embedding=self.embeddings_model,
                    username=self.neo4j_config['USER'],
                    password=self.neo4j_config['PASSWORD'],
                    url=self.neo4j_config['URI'],
                    database=self.neo4j_config['DATABASE'],
                    embedding_node_property=embedding_node_property,
                    index_name=index_name,
                    node_label=node_label,
                    text_node_property=text_node_property,
                    create_id_index=create_id_index,
                )[0]
                created_nodes.append(new_node_id)  # Use the ID of the newly added node

        if created_nodes:
            return created_nodes
        else:
            return None

    
    def find_document_by_text(
            self, 
            text,
            similarity_threshold=None,
            node_label=None,
            index_name=None,
        ):
        # Initialize the vector store for the correct label
        vector_store = self.select_vector_store(index_name=index_name, node_label=node_label)

        # Set a high similarity treshold for the origin document if none is provided
        if not similarity_threshold:
            _similarity_threshold = 0.9
        else:
            _similarity_threshold = similarity_threshold

        # Find origin document
        try:
            document, score = vector_store.similarity_search_by_text(text, similarity_threshold=_similarity_threshold)[0]
        except IndexError:
            document = None
        if document and score >= _similarity_threshold:
            return document, score
        else:
            return None, None

    def similarity_search_by_text(
            self, 
            text, 
            k=5, 
            similarity_threshold=None,
            index_name=None,
            node_label=None
        ):
        self.error_handler.debug_info(f"--- Inside function {sys._getframe().f_code.co_name}")

        # Initialize the vector store for the correct label
        vector_store = self.select_vector_store(index_name=index_name, node_label=node_label)

        if not similarity_threshold:
            similarity_threshold = self.config.get_vector_index_config()["SIMILARITY_THRESHOLD"]

        if not isinstance(text, str):
            text = str(text)
        
        self.error_handler.debug_info(f"Searching for similar documents to {text}")
        try:
            neighbors = self.vector_index.similarity_search_with_relevance_scores(query=text, k=k)
            # Determine if relevance score is above threshold
            filtered_neighbors = [(document, score) for document, score in neighbors if score > similarity_threshold]
            if filtered_neighbors:
                self.error_handler.debug_info(f"Found {len(filtered_neighbors)} neighbors")
                return filtered_neighbors
            else:
                self.error_handler.debug_info(f"No neighbors found")
                return []
        except Exception as e:
            self.error_handler.warning(f"Error performing k-NN search: {e}")
            self.error_handler.exception(sys.exc_info())

