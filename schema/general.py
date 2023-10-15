class Descriptions:
    def __init__(self) -> None:
        self.one_sentence_summary = """
            A summary of the given document or piece of information in one short sentence. 
            Don't use explanatory language like "This document is about..." or "This text describes...".
            Instead, capture the essence of the text and formulate the sentence similar to the original text.
            Just make it really short.
        """
        self.title = """
            The title of the document. If no title is found, the title is left blank.
            Wheyn analyzing a website and a source url is present, use the url of the website 
            when determinig the title.
        """
        self.author = """
            The author of the document. If no author is found, the author is left blank.
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
            
class Functions:
    def get_current_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

