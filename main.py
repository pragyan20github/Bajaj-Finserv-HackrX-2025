import os
import time
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from pinecone import Pinecone

# Assuming data_processor.py is in the same directory
# In main.py
from data_processor import (
    get_document_text, 
    split_text_into_chunks, 
    generate_embeddings, 
    index_chunks_in_pinecone,
    create_document_id # <-- IMPORT THE NEW FUNCTION
)

# --- Load environment variables ---
load_dotenv()
HACKATHON_API_KEY = os.environ.get("HACKATHON_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

# --- Initialize clients ---
genai.configure(api_key=GOOGLE_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

class DocumentData(BaseModel):
    documents: str
    questions: list[str]

app = FastAPI(
    title="ClarityClaim AI API",
    description="API for processing insurance policy documents and answering questions using AI.",
    version="1.0.0"
)

# --- New Function to Generate Answers with Gemini Pro ---
def generate_answer_with_gemini(question: str, context: str) -> str:
    """
    Generates an answer using the Gemini Pro model based on provided context.
    """
    print(f"Generating answer for question: '{question}' with Gemini Pro...")
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # This prompt is crucial for grounding the model in the provided text
    prompt = f"""
    You are an expert insurance policy analyst.
    Based ONLY on the context provided below from an insurance document, answer the user's question.
    Do not use any external knowledge or make assumptions.
    If the answer cannot be found in the provided context, state that clearly.

    CONTEXT:
    ---
    {context}
    ---

    QUESTION: {question}

    ANSWER:
    """

    try:
        response = model.generate_content(prompt)
        # Ensure there is content in the response before accessing .text
        if response.parts:
            print("Gemini Pro responded successfully.")
            return response.text.strip()
        else:
            # This handles cases where the response might be blocked for safety reasons
            print("Gemini Pro response was empty.")
            return "The model's response was empty. This may be due to safety filters."
            
    except Exception as e:
        print(f"Error generating answer with Gemini: {e}")
        return "An error occurred while generating the answer with Gemini Pro."


# In main.py

@app.post("/hackrx/run", tags=["Main Endpoint"])
async def hackrx_run(data: DocumentData, authorization: str = Header(None)):
    """
    This is the main endpoint for the HackRx 6.0 submission.
    It processes a document and answers questions based on it using Gemini and Pinecone.
    """
    # 1. API Key Authentication
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid.")
    
    token = authorization.split(" ")[1]
    if token != HACKATHON_API_KEY:
        print(f"Authentication failed. Received token: {token}") # Helpful for debugging
        raise HTTPException(status_code=401, detail="Invalid API Key.")
    
    document_url = data.documents
    questions = data.questions
    index_name = "hackrx-policy-index"

    # Create a unique, stable ID for the document to use as a namespace
    doc_id_namespace = create_document_id(document_url)
    print(f"Request received. Document URL: {document_url}")
    print(f"Using Pinecone Namespace: {doc_id_namespace}")

    try:
        index = pc.Index(index_name)

        # Step A: Check if document is already processed and indexed
        # We can do this by checking the vector count in the namespace.
        stats = index.describe_index_stats()
        namespace_exists = doc_id_namespace in stats.get('namespaces', {})
        
        if not namespace_exists:
            print(f"Namespace '{doc_id_namespace}' not found. Starting full processing pipeline...")
            # --- Full processing pipeline for a new document ---
            document_content = get_document_text(document_url)
            if not document_content:
                raise HTTPException(status_code=500, detail="Failed to retrieve or process document content.")
            
            chunks = split_text_into_chunks(document_content)
            if not chunks:
                raise HTTPException(status_code=500, detail="Failed to split document into chunks.")
            
            embeddings = generate_embeddings(chunks)
            if not embeddings:
                raise HTTPException(status_code=500, detail="Failed to generate embeddings for document chunks.")
            
            # Index using the specific namespace
            index_chunks_in_pinecone(chunks, embeddings, index_name, namespace=doc_id_namespace)
            print("--- New Document Processing and Indexing Complete ---")
        else:
            print(f"Document already indexed in namespace '{doc_id_namespace}'. Skipping to question answering.")

        # Step B: Answer each question using the indexed document
        print("--- Answering Questions ---")
        answers = []
        for question in questions:
            print(f"Processing question: '{question}'")
            
            # 1. Embed the question
            question_embedding_response = genai.embed_content(
                model="models/embedding-001",
                content=question,
                task_type="retrieval_query"
            )
            question_embedding = question_embedding_response['embedding']
            
            # 2. Query Pinecone in the correct namespace
            search_results = index.query(
                vector=question_embedding,
                top_k=5,
                include_metadata=True,
                namespace=doc_id_namespace # <-- QUERY THE CORRECT NAMESPACE
            )
            
            # 3. Generate the answer
            context_chunks = [match.metadata['text'] for match in search_results.matches]
            context = "\n\n".join(context_chunks)
            
            answer = generate_answer_with_gemini(question, context)
            answers.append(answer)

        print("--- Finished Answering Questions ---")
        return {"answers": answers}

    except Exception as e:
        print(f"An error occurred during the main process: {e}")
        # Be careful not to expose too much detail in production errors
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")