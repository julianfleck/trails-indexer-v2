# https://python.langchain.com/docs/integrations/document_transformers/openai_metadata_tagger

from langchain.chat_models import ChatOpenAI
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from schema.prompts import Prompts as prompts
from schema.schemas import Summaries

from utils.error_handler import ErrorHandler as error_handler
from utils.config_loader import ConfigLoader as config

class Summarizer:
    def __init__(self, schema=None):
        model_name = config().get("SUMMARIZER_MODEL")
        self.llm = ChatOpenAI(temperature=0.0, model=model_name)

        if not schema:
            error_handler().debug_info("Using default schema: Summaries")
            self.schema = Summaries
        else:
            self.schema = schema
            
        self.parser = PydanticOutputParser(pydantic_object=self.schema)
        format_instructions = self.parser.get_format_instructions()

        error_handler().inspect_object(format_instructions)

        self.prompt = PromptTemplate(
            template=prompts().summarization,
            input_variables=[],
            partial_variables={"format_instructions": format_instructions},
        )
        error_handler().inspect_object(self.prompt)

    def summarize(self, text):
        human_message=f"This is the text: {text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_message)
        system_message_prompt = SystemMessagePromptTemplate(prompt=self.prompt)
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        self.chain = create_structured_output_chain(self.schema, self.llm, chat_prompt)

        try:
            output = self.chain.run(input=text)
            return output
        except Exception as e:
            error_handler().inspect_object(e)
            raise e
