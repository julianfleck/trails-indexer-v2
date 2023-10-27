class Descriptions:
    def __init__(self) -> None:
        self.summaries = """
            A list of summaries of the given document or piece of information.
            The summaries are ordered from short to long.
        """.strip()
        self.summary_short = """
            A very short summary of the given document or piece of information in one short sentence. 
            The summary should be 1-2 sentences maximum and 
            different from the medium and long summaries.
        """.strip()
        self.summary_medium = """
            A medium length summary of the given document or piece of information in one short sentence. 
            The summary should be roughly 1/3 of the length of the original text and 
            different from the medium and long summaries.
        """.strip()
        self.summary_long = """
            A long summary of the given document or piece of information in one short sentence.
            The summary should may be roughly 2/3 of the length of the original text, 
            but should exclude any redundant formulations. It should be different from the medium and long summaries.
        """.strip()
        self.title = """
            The title of the document. If no title is found, the title is left blank.
            When analyzing a website and a source url is present, use the url of the website 
            when determinig the title.
        """.strip()
        self.last_indexed = """
            The date when the document was last indexed.
        """.strip()
        self.content_type = """
            The type of content that the document contains.
            Valid content types are defined in the definitions below.
            Note that the author should also be taken into account when 
            determining the content type, e.g. if the document's author is
            a newspaper, the content type is most likely a news article.
        """.strip()
        self.file_type = """
            The file type of the document. Examples are text, markdown, rich text, python, html, etc.
            If no file type is found, the file type is declared as `unknown`.
        """.strip()
        self.author = """
            The author of the document. If no author is found, the author is left blank.
            If the author is a company or a publisher and the name of an individual person who 
            wrote the article is present, use person in the author field and populate 
            the `publisher` field with the name of the company or publisher. 
        """.strip()
        self.publisher = """
            The publisher of the document. If no publisher is found, the publisher is left blank.
            Publishers are always companies or organizations, not individuals.
            Invididuals should be assigned to the `author` field.
        """.strip()
        self.hypernyms = """
            A list of hypernyms describing the category that the text belongs to.
            Hypernyms are words that describe a higher-level category.
            An example of a hypernym for a text talking about a dog is "animals".
            When choosing hypernyms, try to imagine what the text is about and reflect on 
            possible categories. Limit the list of hypernyms to 5-7 items, 
            and make sure that they are really relevant.
            Be as specific as possible.
        """.strip()
        self.hyponyms = """
            A list of hyponyms describing the category that the text belongs to.
            Hyponyms are words that describe a lower-level category.
            An example of a hyponym for a text talking about a dog is "poodles".
            When choosing hyponyms, make sure to include only the ones that are actually
            relevant to the given text. Limit the list of hypernyms to 5-7 items, 
            and make sure that they are really relevant.
            Be as specific as possible.
        """.strip()
        self.topics = """
            A list of topics that the text is about.
            They are chosen from both the list of hypernyms and hyponyms and
            can contain any word that is relevant to the text.
        """.strip()
        self.image = """
            An image. It might be composed of different layers. 
            If different layers are present, each layer is described individually.
        """.strip()
        self.image_layer = """
            A layer of an image. Describe the layer of the image in detail. 
            If there is text present in the image, extract the text.
        """.strip()
        self.section = """
            A section of a document. Note that these sections _could_ be paragraphs, 
            but they don't need to be. It's more important that the sections capture 
            semantically coherent units of the document. Each chunk should be summarizable in a way
            that is different to the previous and next chunk.

            Long documents might have longer sections, while short documents should be
            broken down into shorter sections. A good rule of thumb is that a section should
            be somewhere between 3 and 5 sentences long.

            For documents with less than 400 characters, there should be roughly 4 sections.
            For documents with less than 800 characters, there should be roughly 8 sections.
            
            Don't get influenced by how newlines currently are placed in the document. 
            There might be a better way to organize the sections of the document.
            
            If the document has headlines, factor those in when breaking down the document 
            and structure it accordingly.
        """.strip()


