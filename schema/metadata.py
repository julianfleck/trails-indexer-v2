# https://python.langchain.com/docs/integrations/document_transformers/openai_metadata_tagger

from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.document_transformers.openai_functions import create_metadata_tagger
from utils.error_handler import ErrorHandler
from langchain.prompts import ChatPromptTemplate
from schema.general import Descriptions as description
from utils.config_loader import ConfigLoader as config
from schema.prompts import Prompts as prompts

class Arbitrary:
    def __init__(self):
        # TODO: retrieve topic candidates from the vector store and pass them to the prompt
        self.prompt = prompts().metadata_extraction

        self.schema = {
            "properties": {
                "title": {
                    "type": "string",
                    "description": description().title,
                },
                "author": {"type": "string"},
                "summary": {
                    "type": "string",
                    "description": description().one_sentence_summary,
                },
                "hyponyms": {
                    "type": "array",
                    "description": description().hyponyms,
                    "items": {"type": "string"}
                },
                "hypernyms": {
                    "type": "array",
                    "description": description().hypernyms,
                    "items": {"type": "string"}
                },
                "topics": {
                    "type": "array", 
                    "description": description().topics,
                    "items": {"type": "string"}
                },
                "content_type": {
                    "type": "string",
                    "enum": ["article", "news article", "blogpost", "other"],
                },
                "tone": {"type": "string", "enum": ["positive", "negative"]},
            },
            "required": ["title", "topics", "hyponyms", "hypernyms", "summary"],
        }

class Movie:
    def __init__(self):
        self.schema = Arbitrary().schema
        self.schema.update({
            "properties": {
                "movie_title": {"type": "string"},
                "critic": {"type": "string"},
                "tone": {"type": "string", "enum": ["positive", "negative"]},
                "rating": {
                    "type": "integer",
                    "description": "The number of stars the critic rated the movie",
                },
            },
            "required": ["movie_title", "critic", "tone"],
        })


class EnhanceMetadata:
    def __init__(self, document, schema="arbitrary"):
        self.prompt = Arbitrary().prompt
        self.document = document
        self.error_handler = ErrorHandler()
        # TODO: use LLM to determine suitable schema
        if schema == "movie":
            self.schema = Movie().schema
        else:
            self.schema = Arbitrary().schema

        self.error_handler.debug_info(f"Using schema {schema}")
        self.enhanced_document = self.get_enhanced_metadata(schema=self.schema)

    def get_enhanced_metadata(self, schema):
        # Must be an OpenAI model that supports functions
        # llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
        llm_model = config().get("METADATA_EXTRACTION_MODEL")
        llm = ChatOpenAI(temperature=0.2, model=llm_model)
        document_transformer = create_metadata_tagger(metadata_schema=schema, llm=llm, prompt=self.prompt)
        enhanced_document = document_transformer.transform_documents([self.document])

        return enhanced_document

