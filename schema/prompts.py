from langchain.prompts import ChatPromptTemplate

class Prompts:
    def __init__(self) -> None:
        self.metadata_extraction = ChatPromptTemplate.from_template(
            """
            Your task is extracting relevant meta-data from a text.
            When working on the task, keep the descriptions of the properties in mind and carefully stick to them.
            Keep in mind that some of the values are mandatory, while others are optional.
            Now go to work. This is the input:

            {input}
        """
        )
        self.section_extraction = ChatPromptTemplate.from_template(
            """
            Your task is to analyze the provided document and provide insights. 
            The first task is to break the document down into different sections. 
            
            Note that these sections _could_ be paragraphs, but they don't need to be. 
            It's more important that the sections capture rather rough, but very 
            semantically very coherent units of the document. 
            
            Don't get influenced by how newlines are placed in the document right now. 
            There might be a better way to organize it.
            
            If the document has headlines, factor those in when breaking down the document 
            and structure it accordingly.
            
            After breaking down the document into sections, your second task is to write 
            a short summary and title for each section. Try to keep the summary brief, 
            but include all relevant information. Write the summary in a way that it sill
            appears to be the same text, only shorter. Don't write it from a third person
            perspective. 
            
            Return the document in this notation:

            Document(
                Section(
                    'title': <section title>,
                    'summary': <section description>
                ),
                Section(...),
                ...
            )

            Now go to work. This is the input:

            {input}
        """
        )