#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functions.llm import SchemaTagger

from utils.error_handler import ErrorHandler
from schema.schemas import *
from schema.prompts import Prompts as prompts

from database.neo4j import Graph
from database.vectorstore import VectorStore

error_handler = ErrorHandler()
graph = Graph()

# read text from file: tests/documents/text1
with open("tests/documents/text1", "r") as f:
    text = f.read()


# [ ] 1. chunk below model context window
# [x] 2. save document to graph (no summaries, yet)
# [x] 3. feed chunks to llm for section extraction
# [x] 4. save sections to graph, link to document 
# [x] 5. summarize sections 
# [x] 6. extract metadata for sections
# [x] 7. feed section summaries to llm for document summary
# [x] 8. save document summary to document

metadata_extractor = SchemaTagger(
    schema=Metadata,
    model="gpt-3.5-turbo-0613",
    prompt = prompts().metadata_extraction
)

section_extractor = SchemaTagger(
    schema=Sections,
    model="gpt-3.5-turbo-0613",
    prompt = prompts().section_extraction
)

summary_extractor = SchemaTagger(
    schema=Summaries,
    model="gpt-4",
    prompt=prompts().summarization
)

section_summarizer = SchemaTagger(
    schema=Summaries,
    # model="gpt-3.5-turbo-0613",
    model="gpt-4",
    prompt=prompts().summarization
)

document = Document(
    page_content=text,
    metadata={},
)

# Check if document already exists on graph
try:
    document_node = graph.find_nodes_by_properties(
        {"text": text},
        node_label="Document"
    )[0]
    document_id = document_node.id
    error_handler.success(f"Found document on graph: [blue]{document_id}[/blue].")
except IndexError:
    error_handler.debug_info("Saving document to graph.")

    # Extract metadata
    metadata = metadata_extractor.tag(document=document)
    metadata.last_indexed = Timestamp().now
    document.metadata = metadata.dict()
    del document.metadata["required"]

    # TODO: first pass for summarization: pass document extracts to llm

    # Save document to graph
    try:
        vector_store = VectorStore(index_name="Document", graph=graph)
        document_id = vector_store.add_documents(
            documents=document,
            node_label="Document",
        )[0]
        error_handler.success(f"Added document to graph: [blue]{document_id}[/blue].")
        # Load document from graph
        try:
            document = graph.find_nodes_by_properties(
                {"id": document_id},
                node_label="Document"
            )[0]
            error_handler.success(f"Loaded document from graph: [blue]{document_id}[/blue].")
        except IndexError:
            error_handler.debug_info(f"Error loading document from graph: [blue]{document_id}[/blue].")
    except Exception as e:
        error_handler.success(f"Error adding document.")
        error_handler.handle_error(e)
        document_id = None

if document_id:
    # Check if document on graph has sections
    sections_ids = graph.find_child_nodes(
        parent_id=document_id,
        node_label="Section",
    )

if sections_ids:
    error_handler.debug_info(f"Document {document_id} already has sections.")
else:
    # Extract sections
    # TODO: use extractive summarizer instead of passing whole document to llm
    sections = section_extractor.tag(document=document)

    _section_summaries = ""

    for index, section in enumerate(sections.sections):
        # Delete summaries for now
        del section.metadata.summaries

        # Convert Section object to Document object
        section = Document(
            page_content=section.page_content,
            metadata=section.metadata.dict(),
        )
        # Store dict instead of object
        sections.sections[index] = section

    error_handler.debug_info(f"Linking sections to document {document_id}.")
    try:
        linked_nodes = graph.save_and_link_sequentially(
            graph=graph,
            documents=sections.sections,
            node_label="Section",
            relationship_name="CONTAINS",
            sequence_relationship_name="NEXT",
            parent_ids=document_id,
            parent_linking_pattern="first_only"
        )
        if linked_nodes:
            error_handler.success(f"Linked sections to document {document_id}.")
    except Exception as e:
        error_handler.handle_error(e)


# Load sections from graph
try:
    error_handler.debug_info(f"Loading sections from graph.")
    sections = graph.find_child_nodes(
        parent_id=document_id,
        node_label="Section",
        sequence_label="NEXT",
    )
    if sections:
        error_handler.success(f"Loaded sections from graph: [blue]{[section.id for section in sections]}[/blue].")
except Exception as e:
    error_handler.debug_info(f"Error loading sections from graph.")
    error_handler.handle_error(e)


document_summaries = ""

error_handler.debug_info(f"Extracting summaries for sections.")
for section in sections:
    # Extract summaries
    section_number = section["section_number"]
    section_summaries = section_summarizer.tag(
        text=section["text"],
        status_message=f"Summarizing section {section_number}."
    )
    # Save summaries for generating document summary
    document_summaries += section_summaries.summary_short + "\n"

    # Convert Section object to dict
    section_summaries = section_summaries.dict()
    del section_summaries["required"]

    # Combine document metadata with section text to avoid false classification
    # TODO: check if this really works
    metadata_context = f"""
    Title: {document_node["title"]}
    Topics: {document_node["topics"]}
    Text: {section["text"]}
    """.strip()

    error_handler.inspect_object(metadata_context)

    # Extract metadata for section
    section_metadata = metadata_extractor.tag(
        text=metadata_context,
        status_message=f"Extracting metadata for section {section_number}."
    )
    section_metadata.last_indexed = Timestamp().now

    # Convert Metadata object to dict
    section_metadata = section_metadata.dict()
    del section_metadata["required"]

    # Update section on graph
    error_handler.debug_info(f"Updating section {section.id} on graph.")
    try:
        updated_section_id = graph.update_node_properties(
            node_id=section.id,
            properties={
                **section_metadata,
                **section_summaries
            }
        )
        error_handler.success(f"Updated section {updated_section_id}.")
    except Exception as e:
        error_handler.debug_info(f"Error updating section {section.id}.")
        error_handler.handle_error(e)

document_summaries = summary_extractor.tag(text=document_summaries)

# Convert Summaries object to dict
document_summaries = document_summaries.dict()
del document_summaries["required"]

error_handler.debug_info(f"Saving document summary to document {document_id}.")
try:
    updated_document_id = graph.update_node_properties(
        node_id=document_id,
        properties={
            **document_summaries
        }
    )
    error_handler.success(f"Updated document {updated_document_id}.")
except Exception as e:
    error_handler.debug_info(f"Error updating document {document_id}.")
    error_handler.handle_error(e)


# document = TrailsDocument(
#     page_content=text,
#     metadata=document.metadata,
#     summaries=document_summaries,
#     sections=sections.sections
# )
