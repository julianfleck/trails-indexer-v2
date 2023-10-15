#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functions.embeddings import Embeddings
from utils.error_handler import ErrorHandler as error_handler
from utils.config_loader import ConfigLoader as config
from datetime import datetime
import asyncio
from schema.metadata import EnhanceMetadata

from database.neo4j import Graph
from database.vectorstore import VectorStore

# # 2. Retrieve embeddings from Neo4j
# try:
#     for doc in documents:
#         embedding = vector_store.get_vector(doc['text'])
#         print(f"Retrieved embedding for '{doc['text']}': {embedding}")
# except Exception as e:
#     print(f"Error retrieving embeddings: {e}")

# # 3. Perform a k-NN search
# try:
#     query_text = "A fast dark-colored fox leaps over a lazy canine"
#     neighbors = vector_store.knn(query_text, k=2)
#     print(f"Found the following neighbors for '{query_text}': {neighbors}")
# except Exception as e:
#     print(f"Error performing k-NN search: {e}")

# # Close the database connection
# graph_db_connection.close()

def parse_html_to_text(url):
    url = "https://python.langchain.com/docs/integrations/document_transformers/openai_metadata_tagger"
    from langchain.document_loaders import AsyncHtmlLoader
    from langchain.document_transformers import Html2TextTransformer

    loader = AsyncHtmlLoader([url])
    docs = loader.load()

    html2text = Html2TextTransformer()
    docs_transformed = html2text.transform_documents(docs)
    text = docs_transformed[0].page_content
    return text


def enhance_metadata(text):
    url = "https://python.langchain.com/docs/integrations/document_transformers/openai_metadata_tagger"
    documents = embeddings.create_documents(text)
    for document in documents:
        document.metadata.update({
            "source_url": url,
            "date_indexed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "label": "Paragraph",
        })
        enhanced_document = EnhanceMetadata(document).enhanced_document
        error_handler.inspect_object(enhanced_document)


if __name__ == "__main__":
    graph = Graph()
    error_handler = error_handler()

    # Define some sample documents

    text = """
This is a simple sample document. It contains a few paragraphs of text. Each paragraph has a few sentences.

This is the second paragraph. It also contains a few sentences. This is the third sentence in the second paragraph.

This is the third paragraph. You guessed it, it also contains a few sentences. This is the third sentence in the third paragraph.

"""

    text = """
# Text Zooming

## Introduction: Spatial Hypernym Zooming

Spatial hypernym zooming is a new interaction paradigm that aims to enhance user experience and improve the usability of digital interfaces. It involves the dynamic manipulation of the spatial relationships between objects, allowing users to navigate and interact with information in a more intuitive and efficient manner.

# Navigational axis

Spatial hypernym zooming extends the current 2D spatial paradigm used in desktop applications to a 3D paradigm. It uses the horizontal, vertical, and forward/backward axes, to traverse and explore different levels of abstraction within a digital interface. By dynamically exploring the spatial relationships between objects, users can navigate and interact with information in a more intuitive and efficient manner, gaining a deeper understanding of the content. 

The table below provides an overview of how each axis corresponds to a specific navigation pattern:

| Axis | Spatial Movement | Action | Response |
| --- | --- | --- | --- |
| x | Horizontal – 
Left and right | Panning/
Swiping/
Flicking | Lateral traversal: 
Navigate through content at the same lateral level and granularity |
| y | Vertical – 
Up and down | Scrolling/
Swiping | Temporal traversal: 
Linearly navigate a timeline or narrative structure |
| z | Depth – 
In and out | Zooming/
Pinching | Zoom in or out: 
Change the granularity to reveal underlying concepts (hyponym → hypernym) |

By zooming in or out along these axes, users can access more detailed or broader information.

With spatial hypernym zooming, not only can users navigate through hypernym and hyponym relationships, but they can also apply this interaction paradigm to long texts. By zooming in along the vertical axis, users can delve deeper into the text and explore more specific details. Conversely, by zooming out, users can obtain a higher-level overview of the text, enabling them to grasp the broader themes and concepts.

By zooming in along the vertical axis, the paragraph can be summarized into its key ideas or main topics. Users can then choose to zoom in further on a specific topic, revealing more detailed information or supporting evidence. This process can be repeated until the user reaches a level where only the core concepts and themes of the text are exposed, allowing for a more efficient and focused reading experience.

Spatial hypernym zooming involves zooming in to reveal more specific details or hyponyms, and zooming out to obtain a higher-level overview or hypernyms.

Let's reconsider the zoom levels accordingly:

Original Text:
"NASA's Perseverance Rover successfully landed on Mars today. This marks a major milestone in space exploration. The rover will now begin its mission to search for signs of ancient life and collect samples for future return to Earth."

Zoom Level 1 (Vertical Axis - Zoom Out):
"Space Exploration: Perseverance Rover mission to Mars for ancient life search and sample collection, with a goal of returning samples to Earth."

Zoom Level 2 (Vertical Axis - Zoom Out):
"Perseverance Rover. Mars. Ancient life. Sample collection. Earth return."

Zoom Level 3 (Vertical Axis - Zoom Out):
"Perseverance Rover landed on Mars. Search for signs of ancient life. Collect samples for return to Earth."

Zoom Level 4 (Vertical Axis - Zoom In):
"Perseverance Rover landed on Mars. Mission: search for signs of ancient life and collect samples for return to Earth."

After zooming out to the "Space Exploration" concept, the user can traverse horizontally to explore similar bits about space exploration. This includes missions to other celestial bodies, advancements in space technology, astronaut training, and breakthrough discoveries in space science. By traversing horizontally, the user can navigate through related content at the same level of granularity, gaining a broader understanding of various aspects of space exploration.


"""
    # import spacy
    # nlp = spacy.load("en_core_web_sm")
    # doc = nlp(incoming_document)
    # text = " ".join([token.text for token in doc])

    # def chunk_paragraphs(text):
    #     # use spacy to split text into paragraphs
    #     doc = nlp(text)
    #     paragraphs = [paragraph.text for paragraph in doc.sents]
    #     return paragraphs
    
    # def chunk_sentences(text):
    #     # use spacy to split text into paragraphs
    #     doc = nlp(text)
    #     sentences = [sentence.text for sentence in doc.sents]
    #     return sentences
    

    # # save document to database
    # vector_store = VectorStore(index_name="Document", graph=graph)
    # document_id = vector_store.add_documents_from_text(
    #     text,
    #     node_label="Document",
    # )

    # # Retrieve node from graph
    # try:
    #     document_node = graph.find_nodes_by_properties(
    #         {
    #             "text": text,
    #         },
    #         label="Document",
    #     )[0]
    #     document_id = document_node.id
    #     error_handler.success(f"Found node in database: {document_id}")
    # except IndexError:
    #     error_handler.error(f"Node not found in database")
    #     document_node = None

    # if document_node:
    #     document_id = document_node.id


    # if document_id:
    #     # Continue with processing only if document was successfully saved to database

    #     # Save paragraphs to database
    #     paragraphs = chunk_paragraphs(text)
    #     vector_store = VectorStore(index_name="Paragraph", graph=graph)
    #     paragraph_document_ids = (
    #         vector_store.add_documents_from_text(
    #             paragraphs,
    #             node_label="Paragraph",
    #         )
    #     )

    #     if not paragraph_document_ids:
    #         paragraph_document_ids = []
    #         # Retrieve nodes from graph
    #         for paragraph in paragraphs:
    #             try:
    #                 paragraph_document_node = graph.find_nodes_by_properties(
    #                     {
    #                         "text": paragraph,
    #                     },
    #                     label="Paragraph",
    #                 )[0]
    #                 error_handler.success(f"Found paragraph node in database: {paragraph_document_node.id}")
    #             except IndexError:
    #                 error_handler.generic_error(f"Paragraph node not found in database")
    #                 paragraph_document_node = None
    #             if paragraph_document_node:
    #                 paragraph_document_ids.append(paragraph_document_node.id)

    #     if paragraph_document_ids:
    #         error_handler.success(f"Found {len(paragraph_document_ids)} paragraph nodes in database")
    #         error_handler.debug_info(f"Linking paragraphs to document {document_id}")
    #         # Link paragraphs to document
    #         graph.link_nodes(
    #             origin=document_id,
    #             targets=paragraph_document_ids,
    #             relationship_name="CONTAINS",
    #         )

    #         # Link paragraphs sequentially to each other
    #         graph.link_nodes_sequentially(
    #             targets=paragraph_document_ids,
    #             relationship_name="NEXT",
    #         )


# //////

    # def save_and_link(graph, node_label, text=None, chunker=None, relationship_name="LINKS_TO", 
    #                 sequence_relationship_name=None, parent_ids=None):
    #     """
    #     Save chunks of text as nodes in the graph and link them.

    #     Args:
    #         graph: The graph object.
    #         node_label (str): The label for the node.
    #         text (str, optional): The main text to process.
    #         chunker (callable, optional): Function to split the main text into smaller chunks.
    #         relationship_name (str, optional): Name of the relationship between parents and chunks.
    #         sequence_relationship_name (str, optional): Name of the sequential relationship between chunks.
    #         parent_ids (list[int], optional): List of IDs of the parent nodes.

    #     Returns:
    #         List[int]: IDs of the created nodes.
    #     """
        
    #     print(f"Before check: parent_ids={parent_ids}, type={type(parent_ids)}")
    #     if not isinstance(parent_ids, list):
    #         parent_ids = [parent_ids] if parent_ids is not None else []
    #     print(f"After check: parent_ids={parent_ids}, type={type(parent_ids)}")
        
    #     # If text is not provided, retrieve it from the parent node(s).
    #     if not text and parent_ids:
    #         parent_texts = []
    #         for parent_id in parent_ids:
    #             parent_node = graph.find_node_by_id(parent_id)
    #             if parent_node:
    #                 parent_texts.append(parent_node['text'])
    #             else:
    #                 error_handler.generic_error(f"No node found with ID {parent_id}")
    #         text = ' '.join(parent_texts)  # Combine texts from multiple parents, if needed.
        
    #     error_handler.inspect_object(text)

    #     # Save chunks to the database
    #     chunks = chunker(text) if chunker else [text]
    #     vector_store = VectorStore(index_name=node_label, graph=graph)
    #     chunk_ids = vector_store.add_documents_from_text(chunks, node_label=node_label)

    #     # If chunks were not saved (e.g., due to some error), try to retrieve them from the graph
    #     if not chunk_ids:
    #         chunk_ids = []
    #         for chunk in chunks:
    #             try:
    #                 chunk_node = graph.find_nodes_by_properties({"text": chunk}, label=node_label)[0]
    #                 chunk_ids.append(chunk_node.element_id)
    #             except IndexError:
    #                 # Node not found
    #                 pass

    #     # Link the first chunk to the parent nodes
    #     for parent_id in parent_ids:
    #         graph.link_nodes(origins=[parent_id], targets=[chunk_ids[0]], relationship_name=relationship_name)

    #     # Link chunks sequentially
    #     if sequence_relationship_name and len(chunk_ids) > 1:
    #         graph.link_nodes_sequentially(targets=chunk_ids, relationship_name=sequence_relationship_name)

    #     return chunk_ids



    # Example usage:
    document_id = graph.save_and_link_sequentially(
        graph=graph,
        text=text, 
        node_label="Document",
    )

    error_handler.inspect_object(document_id)

    paragraph_ids = graph.save_and_link_sequentially(
        graph=graph,
        node_label="Paragraph",
        parent_ids=document_id,
        parent_linking_pattern="first_only",  # "first_only", "all", "sequential
        chunker=chunk_paragraphs,
        relationship_name="CONTAINS",
        sequence_relationship_name="NEXT",
    )

    error_handler.debug_info(f"Retrieved {len(paragraph_ids)} paragraph IDs")
    error_handler.inspect_object(paragraph_ids)

    for paragraph_id in paragraph_ids:
        sentence_ids = graph.save_and_link_sequentially(
            graph=graph,
            node_label="Sentence",
            parent_ids=paragraph_id,
            chunker=chunk_sentences,
            relationship_name="CONTAINS",
            sequence_relationship_name="NEXT",
        )
        # graph.find_and_link_similar_nodes_by_id(
        #     paragraph_id,
        #     index_name="Paragraph",
        #     bidirectional=False,
        #     similarity_threshold=0.9,
        #     max_nodes=3,
        # )

        # for sentence_id in sentence_ids:
        #     graph.find_and_link_similar_nodes_by_id(
        #         sentence_id,
        #         index_name="Sentence",
        #         bidirectional=False,
        #         similarity_threshold=0.9,
        #         max_nodes=3,
        #     )

    # vector_store = VectorStore(index_name="Sentence", graph=graph)
    # document_id = vector_store.add_documents_from_text(
    #     text,
    #     node_label="Sentence",
    # )



    # parent = graph.find_parent_node_by_id("66", "Document")
    # error_handler.inspect_object(parent)



    # If you need to save and link sentences within paragraphs, use the following:
    # paragraph_id = save_and_link(graph, paragraph_text, "Paragraph", chunk_sentences)










        # for paragraph_index, paragraph in enumerate(paragraphs):
        #     # Save sentences to database
        #     sentences = chunk_sentences(paragraph)
        #     vector_store = VectorStore(index_name="Sentence", graph=graph)
        #     sentence_document_ids = vector_store.add_documents_from_text(
        #         sentences,
        #         node_label="Sentence",
        #     )

        #     error_handler.inspect_object(sentence_document_ids)

            # # Link sentences to paragraph
            # graph.link_nodes(
            #     origin=paragraph_document_ids[paragraph_index].id,
            #     targets=sentence_document_ids,
            #     relationship_name="CONTAINS",
            # )

            # # Link sentences sequentially to each other
            # graph.link_nodes_sequentially(
            #     targets=sentence_document_ids,
            #     relationship_name="NEXT",
            # )


    #     sentences = chunk_sentences(paragraph)


    
    # vector_store = VectorStore(index_name="Animal")
    # for text in texts:
    #     vector_store.add_document_from_text(
    #         text,
    #         node_label="Animal",
    #     )

    # for text in texts2:
    #     vector_store.add_document_from_text(
    #         text,
    #         node_label="Blindtext",
    #     )

    # node_id = graph.find_nodes_by_property("text", "The quick brown fox jumps over the lazy dogs")[0].id
    # nodes = graph.find_nodes_by_property("text", "The quick brown fox jumps over the lazy dogs")

    # error_handler.debug_info(f"Finding edges for node {node_id}")
    # edges = Graph().find_edges_by_relationship(
    #     relationship_name="SIMILAR_TO",
    #     origin_id=node_id, 
    #     # target_id=target
    # )
    # error_handler.inspect_object(edges)

    # graph.find_and_link_similar_nodes_by_id(
    #     "14c888da-6574-11ee-bdcc-9e92c11e0825", 
    # )

    # graph.find_and_link_similar_nodes_by_text_fuzzy(
    #     "Lorem ipsum",
    #     # label_scope="Blindtext",
    #     index_name="Animal",
    #     bidirectional=False,
    # )
    
    # graph.find_and_link_similar_nodes_by_text_fuzzy(
    #     "the brown fox",
    #     # index_name="Blindtext",
    #     index_name="Animal",
    #     # label_scope="Blindtext",
    #     # label_scope="Animal",
    #     # label_scope=None,
    #     bidirectional=False,
    #     similarity_threshold=0.2,
    # )

    # vector_store = VectorStore(index_name="Animal")
    # vector_store.similarity_search_by_text("fox", k=5, index_name="Animal")

    
    # graph.find_and_link_similar_nodes_by_text(
    #     "The quick brown fox jumps over the lazy banana"
    # # )

    # node = graph.find_node_by_id(int(14))
    # error_handler.inspect_object(node)

    # node_uid = "14c888da-6574-11ee-bdcc-9e92c11e0825"
    # node = graph.find_node_by_id(node_uid)
    # error_handler.inspect_object(node)

    # node = graph.find_nodes_by_property("text", "The quick brown fox jumps over the lazy hund")[0]
    # error_handler.inspect_object(node)

    # document = vector_store.get_document_by_text("The quick brown fox jumps over the lazy hund")
    # error_handler.inspect_object(document)
