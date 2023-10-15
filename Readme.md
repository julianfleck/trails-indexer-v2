# Trails indexer v2

The Trails Indexer is a Python project designed to process and store textual content into a Neo4j graph database. It allows for the ingestion of text, breaking it down into documents, paragraphs, and sentences, and then saving these as nodes in the graph. Relationships between these nodes can also be established, providing a hierarchical and sequential representation of the text.

## Features
- Chunking of Text: Uses spaCy to chunk texts into sentences or paragraphs.
- Vector Storage: Stores chunks of text and their embeddings in a Neo4j graph database.
- Node Linking: Automatically establishes relationships between parent and child nodes as well as sequential relationships between sibling nodes.

# Files

```
.
├── config
│   └── configuration.toml                  # Configuration file
├── database
│   ├── neo4j.py                            # Neo4j graph database utilities
│   └── vectorstore.py                      # Vector storage utilities
│   └── embeddings.py                       # Embedding generation utilities
├── main.py                                 # Main execution script
├── requirements.txt                        # Required packages
├── schema
│   ├── general.py                          # General schema definitions
│   ├── metadata.py                         # Metadata schema definitions
│   └── prompts.py                          # Prompt schema definitions
├── tests
│   ├── test_config_loader.py               # Tests for configuration loader
│   ├── test_database_connection.py         # Tests for database connection
│   └── test_error_handler.py               # Tests for error handler
└── utils
    ├── config_loader.py                    # Configuration loader utilities
    └── error_handler.py                    # Error handling utilities

```

# Setup & Installation

1. Clone this repository:

```bash
git clone https://github.com/trails-org/trails-indexer.git
```

2. Navigate to the project directory and install the required packages:

```bash
cd trails-ingest
pip install -r requirements.txt
```

3. Update the config.py file with your Neo4j database credentials.

## Usage

### 1. Chunking Text:

```python
from utils.nlp import chunk_sentences, chunk_paragraphs

sentences = chunk_sentences(your_text)
paragraphs = chunk_paragraphs(your_text)
```

### 2. Saving and Linking Nodes:
Here's an example of how to save and link nodes using the provided functions:

```python
from database.neo4j import GraphDatabase, save_and_link_sequentially

graph = GraphDatabase()

document_id = save_and_link_sequentially(
    graph, 
    text=text, 
    node_label="Document"
)

paragraph_ids = save_and_link_sequentially(
    graph,
    node_label="Paragraph",
    parent_ids=document_id,
    chunker=chunk_paragraphs,
    relationship_name="CONTAINS",
    sequence_relationship_name="NEXT"
)

sentence_ids = save_and_link_sequentially(
    graph,
    node_label="Sentence",
    parent_ids=paragraph_ids,
    chunker=chunk_sentences,
    relationship_name="CONTAINS",
    sequence_relationship_name="NEXT"
)
```

### 3. Finding and Linking Similar Paragraphs

Our indexer provides feature that allow you to find similar nodes based on text embeddings and link them together. This is useful for establishing relationships between nodes based on the similarity of their content. These functions are a powerful tool to enrich your graph database by establishing relationships based on textual content similarity.

```python
# Find a paragraph by text, then find and link similar paragraphs.

paragraph_id = graph.find_node_by_text(
    text="This is a paragraph.",
    node_label="Paragraph",
    similarity_threshold=0.9,
    max_nodes=1,
)

graph.find_and_link_similar_nodes_by_id(
    paragraph_id,
    index_name="Paragraph",
    bidirectional=False,
    similarity_threshold=0.9,
    max_nodes=3,
)
```

`paragraph_id`: The ID of the paragraph node you are starting from.
`index_name`: The type or label of the node, in this case, "Paragraph".
`bidirectional`: Determines if the linking should be bidirectional.
`similarity_threshold`: Only nodes with similarity above this threshold will be linked.
`max_nodes`: The maximum number of similar nodes to link.

