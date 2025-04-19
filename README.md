# Semantic Document Search Engine

A desktop application that allows users to search through documents semantically using OpenAI's vector store and GPT models. Upload PDF, TXT, or CSV files and ask questions about their content.

## Features

- Clean, modern UI built with tkinter
- Document upload functionality supporting PDF, TXT, and CSV files
- Semantic search using OpenAI's vector stores
- Context-aware responses based on document content
- Simple chat-like interface for queries and responses

## Requirements

- Python 3.8+
- OpenAI API key
- Required Python packages (see `requirements.txt`)

## Installation


1. Clone the repository:
   ```
   https://github.com/nebulaw/semantic-search-engine.git

   cd semantic-document-search
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Start the application:
   ```
   python main.py
   ```

2. Upload a document using the file button (📁) in the bottom left
3. Type your query in the text field
4. Press Enter or click the send button (➤) to submit your query
5. View the response in the chat window

## Project Structure


- `app/` - Main application directory
  - `chat.py` - UI implementation with tkinter
  - `client.py` - OpenAI client and vector store operations
  - `helpers.py` - Utility functions for the application
- `.env` - Environment variables (API keys)
- `main.py` - Entry point for the application
- `requirements.txt` - requirements
- `symp.txt` - A sample document for testing

## How It Works

1. **Document Upload**: Files are uploaded to OpenAI's vector store for semantic indexing
2. **Query Processing**: User questions are matched against the document content using vector search
3. **Response Generation**: The application uses the search results as context for generating relevant answers
4. **UI Display**: Responses are displayed in a chat-like interface

## Dependencies

The application relies on:
- OpenAI's API for vector storage and retrieval
- tkinter for the user interface
- Python's standard library for file operations

