
from typing import List, Optional, Union
from enum import Enum

from langchain.pydantic_v1 import BaseModel, Field, validator, root_validator
from langchain.schema import Document

from schema.properties import Properties as properties
from schema.descriptions import Descriptions as description
from schema.prompts import Prompts as prompts

from utils.error_handler import ErrorHandler
from utils.config_loader import ConfigLoader as config


class Timestamp:
    def __init__(self):
        from datetime import datetime
        self.now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ContentTypes(Enum):
    note = "A short piece of text saved as a note."
    article = "A piece of text that is published in a newspaper or magazine."
    news_article = "A piece of text that is published in a newspaper or magazine, communicating something newsworthy."
    blogpost = "A piece of text that is published on a blog, an opinion piece."
    other = "Any other type of text."


class Summaries(BaseModel):
    summary_short: str = Field(
        description=description().summary_short.strip(),
    )
    summary_medium: str = Field(
        description=description().summary_medium.strip(),
    )
    summary_long: str = Field(
        description=description().summary_long.strip(),
    )
    required = ["summary_short", "summary_medium", "summary_long"]


class Metadata(BaseModel):
    title: Optional[str] = Field(
        description=description().title.strip()
    )
    last_indexed: Optional[str] = Field(
        description=description().last_indexed.strip()
    )
    content_type: Optional[str] = Field(
        description=description().content_type.strip(),
        enum=[i.name for i in ContentTypes]
    )
    author: Optional[str] = Field(
        description=description().author.strip()
    )
    publisher: Optional[str] = Field(
        description=description().publisher.strip()
    )
    hypernyms: List[str] = Field(
        description=description().hypernyms.strip()
    )
    hyponyms: List[str] = Field(
        description=description().hyponyms.strip()
    )
    topics: List[str] = Field(
        description=description().topics.strip()
    )
    required = ["title", "content_type", "hypernyms", "hyponyms", "topics"]

    # @root_validator
    # def check_author_or_publisher(cls, values):
    #     author = values.get("author")
    #     publisher = values.get("publisher")
    #     if not author and not publisher:
    #         raise ValueError("At least one of 'author' or 'publisher' must be defined.")
    #     return values

    # Ensure that topics, hypernyms and hyponyms are lower case
    @validator("topics", "hypernyms", "hyponyms", pre=True, always=True)
    def fields_must_be_lowercase(cls, field: List[str]):
        if field:
            field = [item.lower() for item in field]
        return field

    @validator("content_type", pre=True, always=True)
    def content_type_must_be_valid(cls, field: str):
        valid_types = {ctype.name: ctype.value for ctype in ContentTypes}
        if field not in valid_types:
            ErrorHandler().debug_info(f"No content type found. Using default.")
            field = "other"
        return field
    
    # set Optional fields to None if empty string is passed
    @validator("title", "author", "publisher", pre=True, always=True)
    def set_optional_fields_to_none(cls, field: str):
        if field == "":
            field = "unknown"
        return field


class SectionMetadata(BaseModel):
    section_number: int = Field(
        description="The number of the section",
    )
    index_start: int = Field(
        description="The index of the first character of the section in the parent document",
    )
    index_end: int = Field(
        description="The index of the last character of the section in the parent document",
    )
    # summaries: Optional[List[Summaries]] = Field(
    #     description=description().summaries.strip(),
    #     exclude=True,
    # )
    summaries: Optional[object] = Field(
        description=description().summaries.strip(),
    )


class Section(BaseModel):
    page_content: str = Field(
        description="The text content of the section",
    )
    metadata: SectionMetadata = Field(
        description="Metadata about the section",
    )
    required = ["page_content", "metadata"]


class Sections(BaseModel):
    sections: List[Section] = Field(
        description=description().section.strip(),
    )
    required = ["sections"]

class SectionsWithSummaries(Sections):
    sections: List[Section] = Field(
        description=description().section.strip(),
    )
    summaries: Optional[object] = Field(
        description=description().summaries.strip(),
    )
    required = ["sections", "summaries"]

class TrailsDocument(Document):
    page_content: str = Field(
        description="The text content of the document",
    )
    metadata: Metadata = Field(
        description="Metadata about the document",
    )
    summaries: Optional[Summaries] = Field(
        description=description().summaries.strip(),
    )
    sections: List[Section] = Field(
        description=description().section.strip(),
    )
    required = ["page_content", "metadata", "summaries", "sections"]


class SectionedTrailsDocument(TrailsDocument):
    sections: Optional[List[Section]] = Field(
        description=description().section.strip(),
    )
    required = ["page_content", "metadata", "sections"]


# Helper functions

def resolve_schema_references(schema, root_schema=None):
    """
    Recursively resolve $ref references in the schema and include them inline.
    
    Args:
    - schema (dict): The schema to process.
    - root_schema (dict, optional): The root schema containing definitions. 
                                    Defaults to the provided schema if not specified.

    Returns:
    - dict: The schema with references resolved.
    """
    if root_schema is None:
        root_schema = schema

    if isinstance(schema, dict):
        if "$ref" in schema:
            # Assuming the $ref is a simple #/definitions/ reference
            ref_path = schema["$ref"].split("/")
            ref_definition = root_schema
            for path_segment in ref_path:
                if path_segment == '#':
                    continue
                ref_definition = ref_definition.get(path_segment)
            if ref_definition is None:
                raise ValueError(f"Reference {schema['$ref']} not found in schema!")
            return resolve_schema_references(ref_definition, root_schema)
        else:
            # Recursively resolve references in sub-dictionaries
            return {key: resolve_schema_references(value, root_schema) for key, value in schema.items()}
    elif isinstance(schema, list):
        # Recursively resolve references in list items
        return [resolve_schema_references(item, root_schema) for item in schema]
    else:
        # Return the schema as-is if it's not a dict or list
        return schema
