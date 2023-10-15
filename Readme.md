# Text Processing v1

<aside>
💡 Only generates summaries and let’s the user adjust the zoom

</aside>

## **Text Processing Algorithm**

### **1. User Input**

- User inputs a URL.

### **2. Text Extraction and Cleanup**

- Extract text from the URL's HTML.
- Clean up the extracted text to remove any unwanted characters or formatting.

### **3. Text Chunking and Summarization**

- Chunk the text into paragraphs.
    - For each paragraph:
        - Summarize into one sentence.
- Chunk each paragraph into sentences.
    - For each sentence:
        - Summarize into its shortest form.

### **4. Storing**

- Store summarized texts.
    - If the summarized text is not present on the knowledge graph, store it as a new node.

# Functions breakdown

### **1. Text Extraction and Cleanup**

- `retrieve_web_content(URL: str) -> str`: Extracts raw text from the given URL.
- `clean_text(raw_text: str) -> str`: Cleans up the extracted text by removing unwanted characters or formatting.

### **2. Text Chunking and Summarization**

- `chunk_into_paragraphs(cleaned_text: str) -> List[str]`: Splits the cleaned text into paragraphs.
- `summarize_paragraph(paragraph: str) -> str`: Generates a one-sentence summary for the given paragraph.
- `chunk_into_sentences(paragraph: str) -> List[str]`: Splits the paragraph into individual sentences.
- `summarize_sentence(sentence: str) -> str`: Generates a shortened form of the given sentence.

### **3. Storing**

- `store_text_on_kg(text: str) -> NodeID`: Stores the summarized text on the knowledge graph and returns a unique node ID.