import spacy
nlp = spacy.load("en_core_web_sm")

def chunk_paragraphs(text):
    return [paragraph.strip() for paragraph in text.split('\n\n') if paragraph.strip()]

def chunk_sentences(text):
    doc = nlp(text)
    return [sentence.text for sentence in doc.sents if sentence.text.strip() != ""]

