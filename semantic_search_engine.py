import os
import streamlit as st
from openai import OpenAI
import PyPDF2
import io
import csv

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_csv(csv_file):
    """Extract text from a CSV file."""
    content = csv_file.getvalue().decode('utf-8')
    csv_reader = csv.reader(io.StringIO(content))
    text = ""
    for row in csv_reader:
        text += " ".join(row) + "\n"
    return text

def process_file(uploaded_file):
    """Process the uploaded file and extract text."""
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "text/plain":
        return uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.type == "text/csv":
        return extract_text_from_csv(uploaded_file)
    else:
        return "Unsupported file format"

def answer_question(query, document_texts):
    """Use GPT-4o to answer the query based on the document texts."""
    # Combine all document texts into a single context
    # Limit context size to avoid token limits
    combined_text = "\n\n---\n\n".join(document_texts)
    
    # If context is too long, you might need to truncate it
    if len(combined_text) > 32000:  # Approximate token limit for GPT-4o
        combined_text = combined_text[:32000]
    
    # Create the prompt for GPT-4o
    prompt = f"""
    Answer the following question based only on the provided documents. If the answer is not in the documents, say "I don't have enough information to answer this question."
    
    Documents:
    {combined_text}
    
    Question: {query}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based only on the provided documents."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    
    return response.choices[0].message.content

# Streamlit UI
def main():
    st.title("Simple Document Q&A")
    
    # API Key input
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    # File upload
    uploaded_files = st.file_uploader("Upload documents (PDF, TXT, CSV)", type=["pdf", "txt", "csv"], accept_multiple_files=True)
    
    if uploaded_files:
        document_texts = []
        for uploaded_file in uploaded_files:
            st.write(f"Processing: {uploaded_file.name}")
            document_text = process_file(uploaded_file)
            document_texts.append(document_text)
            
        # Query input
        query = st.text_input("Ask a question about your documents:")
        
        if query and st.button("Get Answer"):
            with st.spinner("Analyzing documents and generating answer..."):
                answer = answer_question(query, document_texts)
                st.subheader("Answer:")
                st.write(answer)

if __name__ == "__main__":
    main()