from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from langchain.vectorstores import Neo4jVector
from langchain.embeddings import OpenAIEmbeddings
from utils.error_handler import ErrorHandler

class GraphDatabaseConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._session = None
        self.error_handler = ErrorHandler()

    def close(self):
        if self._session:
            self._session.close()
        self._driver.close()

    def _get_session(self):
        if not self._session:
            self._session = self._driver.session()
        return self._session

    def read(self, query):
        session = self._get_session()
        try:
            result = session.run(query)
            return [record for record in result]
        except ServiceUnavailable as e:
            self.error_handler.service_unavailable(e)
            return None
        except Exception as e:
            self.error_handler.exception(sys.exc_info())
            return None


class VectorStore:
    def __init__(self, graph_db_connection):
        self.graph_db_connection = graph_db_connection
        self.embeddings_model = OpenAIEmbeddings()
        self.vector_store = Neo4jVector(self.graph_db_connection._driver, self.embeddings_model)

    def save_embeddings(self, documents):
        try:
            self.vector_store.add_documents(documents)
        except Exception as e:
            self.graph_db_connection.error_handler.exception(sys.exc_info())
