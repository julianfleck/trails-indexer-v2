from schema.descriptions import Descriptions as description

class Properties:
    def __init__(self) -> None:
        self.chunks = {
            "type": "array",
            "description": description().chunk,
            "items": {
                "chunk_num": "string",
                "description": "string",
                "text": "string",
                "index_start": "int",
                "index_end": "int"
            }
        },
        self.title = {
            "type": "string",
            "description": description().title,
        },
        self.author = {
            "type": "string",
            "description": description().author,
        },
        self.tone = {
            "type": "string", 
            "enum": [
                "positive", 
                "neutral", 
                "negative"
            ]
        },
        self.content_type = {
            "type": "string",
            "enum": [
                "article", 
                "news article", 
                "blogpost", 
                "other"
            ],
        },
        self.summary = {
            "type": "string",
            "description": description().summary,
        },
        self.hyponyms = {
            "type": "array",
            "description": description().hyponyms,
            "items": {"type": "string"}
        },
        self.hypernyms = {
            "type": "array",
            "description": description().hypernyms,
            "items": {"type": "string"}
        },
        self.topics = {
            "type": "array", 
            "description": description().topics,
            "items": {"type": "string"}
        },
        self.image = {
            "description": description().image,
            "layers": {
                "type": "array",
                "description": description().image_layer,
                "items": {
                    "layer_id": "string",
                    "layer_description": "string",
                    "text": "string",
                }
            }
        }

