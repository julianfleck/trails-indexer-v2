# https://python.langchain.com/docs/integrations/document_transformers/openai_metadata_tagger

from langchain.chat_models import ChatOpenAI
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.output_parsers import PydanticOutputParser, RetryWithErrorOutputParser
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from pydantic import ValidationError

from schema.prompts import Prompts as prompts
from schema.schemas import Metadata, TrailsDocument

from utils.error_handler import ErrorHandler as error_handler
from utils.config_loader import ConfigLoader as config


class MetadataEnhancer:
    def __init__(self, schema=None, temperature=1.6):
        if not schema:
            self.schema = Metadata
        self.schema = schema
        model_name = config().get("METADATA_EXTRACTION_MODEL")
        # model_name = "gpt-4"
        self.llm = ChatOpenAI(temperature=temperature, model=model_name)
        self.parser = PydanticOutputParser(pydantic_object=self.schema)
        format_instructions = self.parser.get_format_instructions()

        self.prompt = PromptTemplate(
            template=prompts().metadata_extraction,
            input_variables=[],
            partial_variables={"format_instructions": format_instructions},
        )

    def get_metadata(self, text):

        human_message=f"This is the text: {text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_message)
        system_message_prompt = SystemMessagePromptTemplate(prompt=self.prompt)
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        self.chain = create_structured_output_chain(self.schema, self.llm, chat_prompt)

        metadata = None

        try:
            metadata = self.chain.run(input=text)
        except Exception as e:
            if isinstance(e, ValidationError):
                error_handler().debug_info(f"Validation error. Retrying.")
                try:
                    metadata = self.get_metadata(text=text, temperature=1.6)
                except Exception as e:
                    error_handler().exception(e)

                
        if metadata:
            # Check if metadata conforms with schema
            if not isinstance(metadata, Metadata):
                # Try again
                error_handler().debug_info(f"Metadata does not conform with schema. Trying again...")
                metadata = self.get_metadata(text=text, temperature=1.6)
                if not isinstance(metadata, Metadata):
                    error_handler().generic_error("Metadata extraction failed.")
            else:
                error_handler().debug_info(f"Metadata extraction successful.")
                return metadata
        else:
            error_handler().generic_error("Metadata extraction failed.")
            return None

    def enhance_document(self, document, schema=None):
        if schema:
            self.schema = schema
        else:
            self.schema = Metadata

        try:
            metadata = self.get_metadata(text=document)
        except Exception as e:
            error_handler().inspect_object(e)
            raise e
        if metadata:
            # Check if document is of class `schema`,
            # otherwise create an instance of the schema.
            if not isinstance(document, self.schema):
                error_handler().debug_info(f"Creating document...")
                document = TrailsDocument(
                    page_content=document,
                    metadata=metadata
                )
            else:
                document.metadata = self.get_metadata(text=document.page_content)
            return document
        else:
            error_handler().generic_error("Metadata extraction failed.")
            return None
    

# class EnhanceMetadata:
#     def __init__(
#             self, 
#             document, 
#             schema="arbitrary"
#         ):
#         self.prompt = prompts.Arbitrary().prompt
#         self.document = document
#         self.error_handler = ErrorHandler()
#         # TODO: use LLM to determine suitable schema
#         if schema == "movie":
#             self.schema = Movie().schema
#         else:
#             self.schema = Arbitrary().schema

#         self.error_handler.debug_info(f"Using schema {schema}")
#         self.enhanced_document = self.get_enhanced_metadata(schema=self.schema)

#     def get_enhanced_metadata(self, schema):
#         # Must be an OpenAI model that supports functions
#         # llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
#         llm_model = config().get("METADATA_EXTRACTION_MODEL")
#         llm = ChatOpenAI(temperature=0.2, model=llm_model)
#         document_transformer = create_metadata_tagger(metadata_schema=schema, llm=llm, prompt=self.prompt)
#         enhanced_document = document_transformer.transform_documents([self.document])

#         return enhanced_document
