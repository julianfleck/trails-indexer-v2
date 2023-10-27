from langchain.document_transformers.openai_functions import create_metadata_tagger

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from schema.prompts import Prompts as prompts
from schema.schemas import Metadata, resolve_schema_references
from langchain.schema import Document

from utils.error_handler import ErrorHandler as error_handler
from utils.config_loader import ConfigLoader as config

class SchemaTagger:
    def __init__(
            self, 
            schema=None,
            model=None,
            temperature=0.3,
            prompt=None
        ):
        if not prompt:
            self.prompt = ChatPromptTemplate.from_template(
                prompts().metadata_extraction
            )
        else:
            self.prompt = ChatPromptTemplate.from_template(
                prompt
            )

        if not schema:
            self.schema = Metadata
        else:
            self.schema = schema
        self.schema_json = resolve_schema_references(self.schema.schema())

        # TODO: use LLM to determine suitable sub-schema
        self.schema_name = self.schema.__name__
        error_handler().debug_info(f"Initialized tagger with schema [blue]{self.schema_name}[/blue].")

        if not model:
            model = config().get("METADATA_EXTRACTION_MODEL")

        # Must be an OpenAI model that supports functions
        # self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
        self.llm = ChatOpenAI(temperature=temperature, model=model)
        # self.enhanced_document = self.get_enhanced_metadata(schema=self.schema)

    def tag(self, document=None, text=None, status_message=None):
        if not document and not text:
            error_handler().value_error("Either document or text must be provided.")
        
        if not document:
            document = Document(
                page_content=text,
                metadata={}
            )

        if not status_message:
            status_message = f"Extracting [blue]{self.schema_name}[/blue]."

        document_transformer = create_metadata_tagger(metadata_schema=self.schema_json, llm=self.llm, prompt=self.prompt)
        
        enhanced_document = error_handler().track_status(
            document_transformer.transform_documents,
            [document],
            description=status_message
        )
        metadata = enhanced_document[0].metadata

        # Validate the enhanced document against the provided schema
        try:
            enhanced_schema = self.schema(**metadata)
            error_handler().success(f"Successfully extracted {self.schema_name}.")
        except Exception as e:
            error_handler().warning(f"Extracted data does not conform to schema.")
            error_handler().inspect_object(metadata)
            error_handler().inspect_object(self.schema(**metadata))
            return metadata

        return enhanced_schema
