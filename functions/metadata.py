# https://python.langchain.com/docs/integrations/document_transformers/openai_metadata_tagger

from functions.llm import SchemaTagger
from schema.prompts import Prompts as prompts
from schema.schemas import Metadata, TrailsDocument, resolve_schema_references

from utils.error_handler import ErrorHandler as error_handler
from utils.config_loader import ConfigLoader as config

class MetadataEnhancer:
    def __init__(
            self, 
            schema=None,
            model=None,
            temperature=0.3
        ):
        if schema:
            error_handler().debug_info(f"Initialized tagger with schema {schema}")
            # error_handler().inspect_object(self.schema)
        else:
            self.schema = Metadata
        if not model:
            model = config().get("METADATA_EXTRACTION_MODEL")

        # Must be an OpenAI model that supports functions
        # self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
        self.llm = ChatOpenAI(temperature=temperature, model=model)
        # self.enhanced_document = self.get_enhanced_metadata(schema=self.schema)

    def get_metadata(self, document):
        document_transformer = create_metadata_tagger(metadata_schema=self.schema, llm=self.llm, prompt=self.prompt)
        enhanced_document = document_transformer.transform_documents([document])

        return enhanced_document[0].metadata
