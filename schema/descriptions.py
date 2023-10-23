class Descriptions:
    def __init__(self) -> None:
        self.summary = """
            A summary of the given document or piece of information in one short sentence. 
            Don't use explanatory language like "This document is about..." or "This text describes...".
            Instead, capture the essence of the text. Write the summary in a way that it sill
            appears to be the same text, only shorter. Don't write it from a third person
            perspective. The summary should be roughly 1/3 of the length of the original text.
        """
        self.title = """
            The title of the document. If no title is found, the title is left blank.
            When analyzing a website and a source url is present, use the url of the website 
            when determinig the title.
        """
        self.last_indexed = """
            The date when the document was last indexed.
        """
        self.content_type = """
            The type of content that the document contains.
            Valid content types are defined in the definitions below.
            Note that the author should also be taken into account when 
            determining the content type, e.g. if the document's author is
            a newspaper, the content type is most likely a news article.
        """
        self.file_type = """
            The file type of the document. Examples are text, markdown, rich text, python, html, etc.
            If no file type is found, the file type is left blank.
        """
        self.author = """
            The author of the document. If no author is found, the author is left blank.
            If the author is a company or a publisher and the name of an individual person who 
            wrote the article is present, use person in the author field and populate 
            the `publisher` field with the name of the company or publisher. 
        """
        self.publisher = """
            The publisher of the document. If no publisher is found, the publisher is left blank.
            Publishers are always companies or organizations, not individuals.
            Invididuals should be assigned to the `author` field.
        """
        self.hypernyms = """
            A list of hypernyms describing the category that the text belongs to.
            Hypernyms are words that describe a higher-level category.
            An example of a hypernym for a text talking about a dog is "animal".
            When choosing hypernyms, try to imagine what the text is about and reflect on 
            possible categories. 
            Be as specific as possible.
        """
        self.hyponyms = """
            A list of hyponyms describing the category that the text belongs to.
            Hyponyms are words that describe a lower-level category.
            An example of a hyponym for a text talking about a dog is "poodle".
            When choosing hyponyms, make sure to include only the ones that are actually
            relevant to the given text.
            Be as specific as possible.
        """
        self.topics = """
            A list of topics that the text is about.
            They are chosen from both the list of hypernyms and hyponyms and
            can contain any word that is relevant to the text.
        """
        self.image = """
            An image. It might be composed of different layers. 
            If different layers are present, each layer is described individually.
        """
        self.image_layer = """
            A layer of an image. Describe the layer of the image in detail. 
            If there is text present in the image, extract the text.
        """
        self.section = """
            A section of a document. Note that these sections _could_ be paragraphs, 
            but they don't need to be. It's more important that the sections capture 
            semantically coherent units of the document. Each chunk should be summarizable in a way
            that is different to the previous and next chunk.

            Long documents might have longer sections, while short documents should be
            broken down into shorter sections.
            
            Don't get influenced by how newlines currently are placed in the document. 
            There might be a better way to organize the sections of the document.
            
            If the document has headlines, factor those in when breaking down the document 
            and structure it accordingly.
        """


