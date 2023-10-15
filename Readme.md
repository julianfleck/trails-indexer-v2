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
git clone https://github.com/trails-org/indexer-v2.git
```

2. Navigate to the project directory and install the required packages:

```bash
cd indexer-v2
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

### 2. Saving and Linking Nodes

When working with textual data, we often want to store and organize it hierarchically. For instance, a document can be divided into paragraphs, and each paragraph can further be split into sentences. Our system provides utilities to save the embeddings of the textual data to a vectore store and simultanously link them appropriately in the graph.

Here's an example of how to embed and link nodes using the provided functions:

```python
from database.neo4j import GraphDatabase, save_and_link_sequentially
from utils.nlp import chunk_paragraphs, chunk_sentences

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

`text`: The full content of the document.
`node_label`: The label for the node, in this case, "Document".
`chunker`: Any function to chunk the provided text. Used here to split into paragraphs or sentences.
`relationship_name`: The name of the relationship between the document and its paragraphs.
`sequence_relationship_name`: The name of the relationship between sequential paragraphs.

Running the above script on a text will save the embeddings to a Neo4j vector index for each node label and produce a linked graph similar to this:

<img width="880" alt="node-structure" src="https://github.com/trails-org/indexer-v2/assets/50588193/7e3c1948-bea1-483b-a18b-8f335d139efe">


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

