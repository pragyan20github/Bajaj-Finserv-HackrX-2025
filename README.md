# ClarityClaim AI: LLM-Powered Intelligent Policy Analyst

## Project Overview

ClarityClaim AI is an innovative solution designed for the HackRx 6.0 competition. It is an intelligent query-retrieval system that automates the process of answering complex, natural language questions based on large, unstructured policy documents. By leveraging a Retrieval-Augmented Generation (RAG) pipeline, our system enables efficient, accurate, and transparent claims processing.

## Problem Statement

The manual review of extensive legal and insurance policy documents is a time-consuming and error-prone process. Our solution addresses this by providing an API that can instantly understand and respond to user queries, significantly reducing operational overhead and improving customer experience.

## Features

* **Document Ingestion**: Seamlessly processes unstructured PDF documents.
* **Semantic Search**: Uses vector embeddings to perform conceptual searches, finding relevant policy clauses even without exact keyword matches.
* **Contextual Reasoning**: Employs an LLM to synthesize information from retrieved clauses and generate accurate, context-bound answers.
* **API Interface**: Provides a clean and robust `POST` endpoint for easy integration into existing claims management systems.

## Tech Stack

* **Backend**: FastAPI
* **Vector Database**: Pinecone
* **Embeddings Model**: Gemini `embedding-001`
* **Generative Model**: Hugging Face Inference API (`distilbert-base-uncased-distilled-squad`)
* **Dependencies**: `requests`, `PyMuPDF`, `uvicorn`, `pydantic`, `python-dotenv`

## Setup and Installation

Follow these steps to get the project running on your local machine.

### Prerequisites

* Python 3.8+
* A Hugging Face API token
* A Google API key (for Gemini embeddings)
* A Pinecone API key and environment details

### Steps

1.  **Clone the repository**:

    ```bash
    git clone [https://github.com/your-username/Bajaj-Finserv-HackrX-2025.git](https://github.com/your-username/Bajaj-Finserv-HackrX-2025.git)
    cd Bajaj-Finserv-HackrX-2025
    ```

2.  **Set up the virtual environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate   # On Windows
    ```

3.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**:

    * Create a `.env` file in the root directory.
    * Add your API keys and other credentials:

    ```
    HACKATHON_API_KEY="your_hackathon_key"
    GOOGLE_API_KEY="your_gemini_key"
    PINECONE_API_KEY="your_pinecone_key"
    PINECONE_ENVIRONMENT="your_pinecone_environment"
    HUGGINGFACE_API_KEY="your_huggingface_token"
    ```

5.  **Run the FastAPI server**:

    ```bash
    uvicorn main:app --reload
    ```
    Your API will now be running on `http://127.0.0.1:8000`.

## API Usage

You can test the API with a tool like `curl` or Postman.

### `POST /hackrx/run`

This endpoint processes a document and answers a list of questions.

**Example Request:**

```bash
curl -X POST "[http://127.0.0.1:8000/hackrx/run](http://127.0.0.1:8000/hackrx/run)" \
-H "Authorization: Bearer <your-hackathon-key>" \
-H "Content-Type: application/json" \
-d '{
  "documents": "[https://hackrx.blob.core.windows.net/assets/hackrx_6/policies/BAJHLIP23020V012223.pdf](https://hackrx.blob.core.windows.net/assets/hackrx_6/policies/BAJHLIP23020V012223.pdf)",
  "questions": [
    "What is the waiting period for pre-existing diseases?",
    "How does the policy define 'Hospital'?"
  ]
}'

**Example Response:**

{
  "answers": [
    "The waiting period for pre-existing diseases is 36 months of continuous coverage from the date of inception of the first policy.",
    "A hospital is an institution established for in-patient care and day care treatment that meets certain criteria..."
  ]
}


Future Enhancements
Multi-document Analysis: Expand the system to analyze and cross-reference information from multiple policy documents in a single request.

Structured Output: Enhance the LLM prompt to generate a structured JSON response with citations, as initially planned.

Chat Interface: Build a user-friendly frontend interface for natural language interaction.

