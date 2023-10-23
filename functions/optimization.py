from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import json
from schema.prompts import Prompts as prompts

from utils.error_handler import ErrorHandler as error_handler
from utils.config_loader import ConfigLoader as config

class Optimizer:
    def __init__(self, model=None):
        if not model:
            model_name = config().get("OPTIMIZER_MODEL")
        self.llm = ChatOpenAI(temperature=0.0, model=model_name)

    def choose_best_option(self, original_prompt, candidates, schema=None):        
        self.prompt = PromptTemplate(
            template=prompts().choose_best_option,
            input_variables=["original_prompt"],
        )

        human_message=f"These are the candidates: {candidates}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_message)
        system_message_prompt = SystemMessagePromptTemplate(prompt=self.prompt)
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        if schema:
            self.chain = create_structured_output_chain(
                schema, 
                llm=self.llm, 
                prompt=chat_prompt
            )
        else:
            self.chain = LLMChain(
                llm=self.llm, 
                prompt=chat_prompt
            )

        try:
            output = self.chain.run(original_prompt=original_prompt)
            return output
        except Exception as e:
            error_handler().inspect_object(e)
            raise e
