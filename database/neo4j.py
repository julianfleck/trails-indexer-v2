import sys
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from langchain.schema.document import Document
from utils.error_handler import ErrorHandler as error_handler
from utils.config_loader import ConfigLoader as config
from schema.general import Functions

from database.vectorstore import VectorStore

class GraphDatabaseConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._session = None
        self.error_handler = error_handler

    def close(self):
        if self._session:
            self._session.close()
        self._driver.close()

    def _get_session(self):
        if not self._session:
            self._session = self._driver.session()
        return self._session

    def read(self, query, parameters={}):
        session = self._get_session()
        try:
            result = session.run(query, parameters)
            return [record for record in result]
        except ServiceUnavailable as e:
            self.error_handler.service_unavailable(e)
            return None
        except Exception as e:
            self.error_handler.exception(sys.exc_info())
            return None
        
    def write(self, query, parameters={}):
        session = self._get_session()
        try:
            session.run(query, parameters)
        except ServiceUnavailable as e:
            self.error_handler.service_unavailable(e)
            self.error_handler.exception(sys.exc_info())
            return False
        except Exception as e:
            self.error_handler.exception(sys.exc_info())
            return False


class Graph:
    def __init__(self):
        neo4j_config = config().get_neo4j_config()
        self.config = config().get_config()
        self.error_handler = error_handler()
        self.vector_store = VectorStore(graph=self)
        self.schema_functions = Functions()
        self.graph = self
        self.graph_database = GraphDatabaseConnection(
            uri=neo4j_config['URI'],
            user=neo4j_config['USER'],
            password=neo4j_config['PASSWORD']
        )

    def find_node_by_id(self, node_id):
        self.error_handler.debug_info(f"Finding node with id {node_id}")

        # Check if node_id is integer or string
        if not isinstance(node_id, (int, str)):
            self.error_handler.generic_error(f"Invalid node ID: {node_id}")
            return None

        # If node_id is of integer type, then we assume it's Neo4j's internal ID.
        # Otherwise, we assume it's a UUID.
        if isinstance(node_id, int):
            query = "MATCH (n) WHERE id(n) = $node_id RETURN n"
        else:
            query = "MATCH (n) WHERE n.id = $node_id RETURN n"
        
        params = {"node_id": node_id}
        
        
        records = self.graph_database.read(query, params)
        try:
            if len(records) > 0:
                self.error_handler.success(f"Found {len(records)} nodes")
                return records[0]['n']
        except Exception as e:
            self.error_handler.exception(sys.exc_info())
            return None
    
    def find_nodes_by_properties(self, properties, label=None):
        """
        Find nodes based on multiple properties and an optional label.

        Args:
            properties (dict): Dictionary containing key-value pairs of properties.
            label (str, optional): Label of the nodes to search for. If not provided, all nodes will be searched.

        Returns:
            List: List of nodes that match the label (if provided) and properties.
        """
        
        conditions = [f"n.{property} = ${property}" for property in properties.keys()]
        query_condition = " AND ".join(conditions)
        
        if label:
            query = f"MATCH (n:{label})"
        else:
            query = "MATCH (n)"
        
        if query_condition:
            query += f" WHERE {query_condition}"

        query += " RETURN n"

        try:
            records = self.graph_database.read(query, properties)
            return [record['n'] for record in records]
        except Exception as e:
            self.error_handler.exception(exc_info=sys.exc_info())
            return []


    def find_parent_node_by_id(self, node_id, parent_label):
        """
        Given a node's ID, follow a specified relationship backwards to retrieve its parent node of a specific label.

        Args:
            node_id (int or str): The ID or UID of the node which's parent should be found.
            parent_label (str): The label of the parent node.

        Returns:
            Node: The parent node object if found, otherwise None.
        """
        self.error_handler.debug_info(f"--- Inside function {sys._getframe().f_code.co_name}")

        # If node_id is of integer type, then we assume it's Neo4j's internal ID.
        # Otherwise, we assume it's a UUID.
        if isinstance(node_id, int):
            query = f"""
            MATCH (parent:{parent_label})-->(chunk) 
            WHERE id(chunk) = $node_id 
            RETURN parent
            """
        else:
            query = f"""
            MATCH (parent:{parent_label})-->(chunk) 
            WHERE chunk.id = $node_id 
            RETURN parent
            """
        
        records = self.graph_database.read(query, {"node_id": node_id})

        self.error_handler.debug_info(query)
        
        if records:
            return records[0]['parent']
        else:
            return None

    def find_edge_by_id(self, edge_id):
        query = "MATCH ()-[r]-() WHERE id(r) = $edge_id RETURN r"
        params = {"edge_id": edge_id}
        records = self.graph_database.read(query, params)
        if len(records) > 0:
            return records[0]['r']
        else:
            return None
        
    def find_edges_by_property(self, property, value, origin_id=None, target_id=None):
        # Determine the type of origin_id and target_id to form the correct query condition
        if origin_id is not None:
            origin_condition = f"id(start) = {origin_id}" if isinstance(origin_id, int) else f"start.id = '{origin_id}'"
        else:
            origin_condition = ""

        if target_id is not None:
            target_condition = f"id(end) = {target_id}" if isinstance(target_id, int) else f"end.id = '{target_id}'"
        else:
            target_condition = ""

        # Construct the query based on the provided conditions
        conditions = [f"r.{property} = '{value}'"]
        if origin_condition:
            conditions.append(origin_condition)
        if target_condition:
            conditions.append(target_condition)

        query = f"MATCH (start)-[r]->(end) WHERE {' AND '.join(conditions)} RETURN r"
        
        records = self.graph_database.read(query)
        return [record['r'] for record in records]
    
    def find_edges_by_relationship(self, relationship_name, origin_id=None, target_id=None):
        """
        Find edges based on relationship type and optional origin or target node ID.

        Args:
            relationship_name (str): Type of relationship to search for.
            origin_id (int or str, optional): ID or UID of the origin node.
            target_id (int or str, optional): ID or UID of the target node.

        Returns:
            List: List of edges that match the criteria.
        """
        
        # Determine if the IDs are internal Neo4j IDs or uids
        origin_id_key = "id(start)" if isinstance(origin_id, int) else "start.id"
        target_id_key = "id(end)" if isinstance(target_id, int) else "end.id"

        if origin_id is not None and target_id is not None:
            query = f"MATCH (start)-[r:{relationship_name}]->(end) WHERE {origin_id_key} = $origin_id AND {target_id_key} = $target_id RETURN r"
        elif origin_id is not None:
            query = f"MATCH (start)-[r:{relationship_name}]->(end) WHERE {origin_id_key} = $origin_id RETURN r"
        elif target_id is not None:
            query = f"MATCH (start)-[r:{relationship_name}]->(end) WHERE {target_id_key} = $target_id RETURN r"
        else:
            query = f"MATCH (start)-[r:{relationship_name}]->(end) RETURN r"

        records = self.graph_database.read(query, {"origin_id": origin_id, "target_id": target_id})
        return [record['r'] for record in records]

    def check_if_node_exists(self, node_id):
        node = self.find_node_by_id(node_id)
        return node is not None
    
    def check_if_edge_exists(self, edge_id):
        edge = self.find_edge_by_id(edge_id)
        return edge is not None
    
    def link_nodes(
            self, 
            origins, 
            targets,
            relationship_name="LINKS_TO", 
            edge_values=None, 
            force=False, 
            bidirectional=False
        ):
        """
        Link one or more origin nodes to one or more target nodes.

        Args:
            origins (int, str, or List[int or str]): ID or UID of the origin node(s).
            targets (List[int or str]): List of IDs or UIDs of the target nodes.
            relationship_name (str, optional): Type of relationship. Defaults to "LINKS_TO".
            edge_values (dict, optional): Properties to assign to the relationship. Defaults to None.
            force (bool, optional): If True, forcefully create the relationship even if one exists. Defaults to False.
            bidirectional (bool, optional): If True, create a bidirectional relationship. Defaults to False.

        Returns:
            bool: True if links were created successfully, False otherwise.
        """
        
        if edge_values is None:
            edge_values = {
                "last_indexed": self.schema_functions.get_current_timestamp()
            }

        # Ensure origins is a list
        if not isinstance(origins, list):
            origins = [origins]

        # Exclude self-links
        targets = [target for target in targets if target not in origins]

        # Check if there are any target nodes left
        if not targets:
            self.error_handler.warning("No valid target nodes provided. Skipping.")
            return False

        for origin in origins:
            # Go through all target nodes
            for target in targets:
                # Determine if the IDs are internal Neo4j IDs or uids for each target
                origin_id_key = "id(start)" if isinstance(origin, int) else "start.id"
                target_id_key = "id(end)" if isinstance(target, int) else "end.id"

                # Check if a link already exists between the origin node and the target node
                edges_origin_to_target = self.find_edges_by_relationship(relationship_name, origin_id=origin, target_id=target)
                edges_target_to_origin = self.find_edges_by_relationship(relationship_name, origin_id=target, target_id=origin) if bidirectional else []

                if len(edges_origin_to_target) > 0 and (not bidirectional or len(edges_target_to_origin) > 0):
                    self.error_handler.warning(f"Link between {origin} and {target} already exists")
                    if not force:
                        continue  # Skip the current iteration and move to the next target
                else:
                    self.error_handler.debug_info(f"Linking {origin} and {target}")

                # Link target nodes to origin node
                query = f"""
                        MATCH (start) WHERE {origin_id_key} = $start_id
                        MATCH (end) WHERE {target_id_key} = $end_id
                        MERGE (start)-[r1:{relationship_name}]->(end)
                        SET r1 += $edge_values
                """
                
                # If bidirectional is True, link the target node to the origin node as well
                if bidirectional:
                    query += f"""
                            MERGE (start)<-[r2:{relationship_name}]-(end)
                            SET r2 += $edge_values
                    """
                
                try:
                    response = self.graph_database.write(query, {
                        "start_id": origin, 
                        "end_id": target, 
                        "edge_values": edge_values
                    })
                except Exception as e:
                    self.error_handler.generic_error(f"Error linking nodes {origin} and {target}", e)
                    return False
                
        # Returns True if all nodes were linked successfully.
        return True


    def link_nodes_sequentially(
            self,
            targets,
            origins=None,
            relationship_name="LINKS_TO", 
            edge_values=None, 
            force=False, 
            bidirectional=False,
            close_loop=False
        ):
        """
        Link each node in the list to the next node sequentially.

        Args:
            targets (List[int or str]): List of node IDs to link.
            origins (List[int or str], optional): List of IDs or UIDs of the origin nodes. If not provided, the first node in targets is used.
            relationship_name (str, optional): Type of relationship. Defaults to "LINKS_TO".
            edge_values (dict, optional): Properties to assign to the relationship. Defaults to None.
            force (bool, optional): If True, forcefully create the relationship even if one exists. Defaults to False.
            bidirectional (bool, optional): If True, create a bidirectional relationship. Defaults to False.
            close_loop (bool, optional): If True, the last node in the list links back to the origin. Defaults to False.

        Returns:
            bool: True if links were created successfully, False otherwise.
        """
        
        if not origins:
            if len(targets) < 2:
                self.error_handler.warning("At least two node IDs are required to link them sequentially.")
                return False
            origins = [targets[0]]
            targets = targets[1:]

        for origin in origins:
            for target in targets:
                success = self.link_nodes(
                    origins=[origin], 
                    targets=[target], 
                    relationship_name=relationship_name, 
                    edge_values=edge_values, 
                    force=force, 
                    bidirectional=bidirectional
                )
                
                if not success:
                    self.error_handler.warning(f"Failed to link node {origin} to node {target}.")
                origin = target

            # Close the loop if required
            if close_loop:
                success = self.link_nodes([targets[-1]], [origins[0]], relationship_name, edge_values, force, bidirectional)
                if not success:
                    self.error_handler.warning(f"Failed to close the loop between {targets[-1]} and {origins[0]}.")
                    return False

        return True
    
    def find_and_link_similar_nodes_by_id(
        self,
        origin_node_id, 
        similarity_threshold=None, 
        node_label=None, 
        index_name=None,
        max_nodes=None,
        bidirectional=False,
        force=False
    ):
        """
        Find and link nodes that are similar to the provided node based on its text content.

        Args:
            origin_node_id (str): UID of the origin node whose similar nodes are to be found and linked.
            similarity_threshold (float, optional): Threshold for similarity score. Defaults to value from configuration.
            max_nodes (int, optional): Maximum number of nodes to link. If not provided, links all nodes above the threshold.

        Returns:
            bool: True if the linking succeeds for all neighbors above the threshold, False otherwise.
        """

        # Initialize the vector store for the correct label
        self.error_handler.debug_info(f"--- Inside function {sys._getframe().f_code.co_name}")
        vector_store = VectorStore(index_name=index_name, node_label=node_label)
        
        self.error_handler.debug_info(f"Finding similar nodes for node {origin_node_id}")

        # If no similarity_threshold is passed, fetch it from the configuration
        if similarity_threshold is None:
            similarity_threshold = self.config["VECTOR_INDEX"]["SIMILARITY_THRESHOLD"]
        
        # Fetch the node
        node = self.find_node_by_id(origin_node_id)
        origin_node_label = list(node.labels)[0]

        if not node:
            self.error_handler.warning(f"Node {origin_node_id} not found.")
            return False
        
        # Overwrite the origin_node_id with the actual node id from the graph so 
        # that both origin and target nodes use the same format
        origin_node_id = node.id
        text = node["text"]
        
        # Fetch similar nodes from VectorStore based on text similarity
        self.error_handler.debug_info(f"Finding neighbors for node {origin_node_id}")
        self.error_handler.success(f"Performing similarity search for node {origin_node_id}")
        neighbors = vector_store.similarity_search_by_text(
            text, 
            similarity_threshold=similarity_threshold,
            index_name=index_name,
            node_label=node_label
        )
        
        # Sort neighbors by similarity score in descending order
        sorted_neighbors = sorted(neighbors, key=lambda x: x[1], reverse=True)
        
        # If max_nodes is provided, limit the neighbors list
        if max_nodes:
            sorted_neighbors = sorted_neighbors[:max_nodes]
        
        # Flag to track if any linking operation failed
        linking_succeeded = True
        
        for neighbor, score in sorted_neighbors:
            # Find the node on the graph
            neighbor_node = self.find_nodes_by_properties(
                {
                    "text": neighbor.page_content,
                },
                label=node_label,
            )[0]
            neighbor_node_label = list(neighbor_node.labels)[0]
            
            self.error_handler.debug_info(f"Neighbor: {neighbor_node.id} Score: {score}")
            self.error_handler.debug_info(f"Neighbor node label: {neighbor_node_label}")

            # Skip if the neighbor is the same as the origin or if similarity is >= 1
            if neighbor_node.id == origin_node_id or score >= 1:
                self.error_handler.warning(f"Skipping node {neighbor_node.id} because it is the same as the origin node")
                continue

            # Skip if relationship_name is specified and the neighbor node is not of the specified type
            self.error_handler.debug_info(f"Origin node label: {origin_node_label}")

            # Check if either the origin node or the neighbor node does not match the specified node_label
            if node_label:
                if origin_node_label != node_label or neighbor_node_label != node_label:
                    self.error_handler.warning(f"Skipping link between {origin_node_id} and {neighbor_node.id} because either node is not of type {node_label}")
                    continue

            # Link nodes if score is above threshold
            if score > similarity_threshold:
                self.error_handler.debug_info(f"Linking node {origin_node_id} to {neighbor_node.id} with score {score}")
                try:
                    self.link_nodes(
                        origins=origin_node_id, 
                        targets=[neighbor_node.id], 
                        relationship_name="SIMILAR_TO", 
                        edge_values={"similarity": score}, 
                        bidirectional=bidirectional,
                        force=force
                    )
                except Exception as e:
                    self.error_handler.debug_info(f"Error linking node {origin_node_id} to {neighbor_node.id}: {e}")
                    linking_succeeded = False

        return linking_succeeded
    
    def find_and_link_similar_nodes_by_text(
            self, 
            text,
            similarity_threshold=None,
            node_label=None,
            index_name=None,
            max_nodes=None,
            bidirectional=False,
            force=False
        ):
        # Find node by text
        try:
            origin_node = self.find_nodes_by_properties(
                {
                    "text": text,
                },
                label=node_label,
            )[0]
        except IndexError:
            origin_node = None
        
        if not origin_node:
            self.error_handler.warning(f"No nodes found for text {text}")
            return False
        
        self.find_and_link_similar_nodes_by_id(
            origin_node.id,
            index_name=index_name,
            node_label=node_label,
            similarity_threshold=similarity_threshold,
            max_nodes=max_nodes,
            bidirectional=bidirectional,
            force=force
        )

    def find_and_link_similar_nodes_by_text_fuzzy(
            self, 
            text, 
            similarity_threshold=None, 
            node_label=None, 
            index_name=None,
            max_nodes=10,
            bidirectional=False,
            force=False
        ):
        self.error_handler.debug_info(f"--- Inside function {sys._getframe().f_code.co_name}")
        # Initialize the vector store for the correct label
        vector_store = VectorStore(index_name=index_name, node_label=node_label)

        # Find origin documents
        try:
            self.error_handler.debug_info(f"Label scope: {node_label} Index name: {index_name}")
            origin_documents = vector_store.similarity_search_by_text(
                text, 
                similarity_threshold=similarity_threshold,
                k=max_nodes,
                index_name=index_name,
                node_label=node_label
            )
            self.error_handler.inspect_object(origin_documents)
        except IndexError:
            origin_documents = None

        # Find origin node on graph
        origin_nodes = None
        if origin_documents:
            for origin_document, score in origin_documents:
                try:
                    origin_nodes = self.find_nodes_by_properties(
                        {
                            "text": origin_document.page_content,
                        },
                        label=node_label,
                    )
                except IndexError:
                    self.error_handler.warning(f"No origin nodes found for text {text}")
                    return False
            
            if origin_nodes:
                for origin_node in origin_nodes:
                    self.error_handler.debug_info(f"Linking origin node {origin_node.id} to similar nodes")

                    # Link origin node to similar nodes
                    self.find_and_link_similar_nodes_by_id(
                        origin_node.id,
                        similarity_threshold=similarity_threshold,
                        node_label=node_label,
                        index_name=index_name,
                        max_nodes=max_nodes,
                        bidirectional=bidirectional,
                        force=force
                    )


    def save_and_link_sequentially(
            self,
            graph=None, 
            node_label="Chunk",
            text=None, 
            chunker=None, 
            relationship_name="LINKS_TO", 
            sequence_relationship_name=None, 
            parent_ids=None,
            parent_linking_pattern="first_only", # "first_only", "all"
        ):
        """
        Save chunks of text as nodes in the graph and link them.

        Args:
            graph: The graph object.
            node_label (str): The label for the node.
            text (str, optional): The main text to process.
            chunker (callable, optional): Function to split the main text into smaller chunks.
            relationship_name (str, optional): Name of the relationship between parents and chunks.
            sequence_relationship_name (str, optional): Name of the sequential relationship between chunks.
            parent_ids (list[int], optional): List of IDs of the parent nodes.

        Returns:
            List[int]: IDs of the created nodes.
        """
        if not graph and not isinstance(graph, Graph):
            raise ValueError("Graph object must be provided.")
        
        if not text and not parent_ids:
            raise ValueError("Either text or parent_ids must be provided.")
        
        self.vector_store = VectorStore(index_name=node_label, node_label=node_label, graph=graph)

        # If parent_ids are provided, ensure it's a list
        if parent_ids is not None and not isinstance(parent_ids, list):
            parent_ids = [parent_ids]

        if parent_ids:
            self.error_handler.debug_info(f"parent_ids length: {len(parent_ids)}, type: {type(parent_ids)}")

        # If text is not provided and parent_ids are, fetch the text from the parent node
        if not text and parent_ids:
            parent_texts = []
            for parent_id in parent_ids:
                parent_node = graph.find_node_by_id(parent_id)
                if parent_node:
                    parent_texts.append(parent_node['text'])
                    self.error_handler.debug_info(f"Found parent node with ID {parent_id}")
                    self.error_handler.debug_info(parent_node['text'])
            text = ' '.join(parent_texts)

        # Save chunks to the database
        chunks = chunker(text) if chunker else [text]
        chunk_ids = []

        for chunk in chunks:
            try:
                saved_chunks = self.vector_store.add_documents_from_text(chunk, node_label=node_label)
                for saved_chunk in saved_chunks:
                    chunk_ids.append(saved_chunk)
            except Exception as e:
                self.error_handler.generic_error(f"Error saving chunk", exception=e)

        if parent_linking_pattern == "first_only":
            # Link the first chunk to the parent nodes
            if parent_ids and chunk_ids:
                for parent_id in parent_ids:
                    graph.link_nodes(origins=[parent_id], targets=[chunk_ids[0]], relationship_name=relationship_name)
        elif parent_linking_pattern == "all":
            # Link all chunks to the parent nodes
            if parent_ids and chunk_ids:
                for parent_id in parent_ids:
                    graph.link_nodes(origins=[parent_id], targets=chunk_ids, relationship_name=relationship_name)
        
        # Link chunks sequentially
        if sequence_relationship_name and len(chunk_ids) > 1:
            graph.link_nodes_sequentially(targets=chunk_ids, relationship_name=sequence_relationship_name)
            
        self.error_handler.inspect_object(chunk_ids)

        return chunk_ids