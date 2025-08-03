import os
import time
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from pinecone import Pinecone

# Assuming data_processor.py is in the same directory
from data_processor import get_document_text, split_text_into_chunks, generate_embeddings, index_chunks_in_pinecone

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
            return response.text.strip()
        else:
            # This handles cases where the response might be blocked for safety reasons
            return "The model's response was empty. This may be due to safety filters."
            
    except Exception as e:
        print(f"Error generating answer with Gemini: {e}")
        return "An error occurred while generating the answer with Gemini Pro."


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
        raise HTTPException(status_code=401, detail="Invalid API Key.")
    
    # 2. Process the request
    document_url = data.documents
    questions = data.questions
    
    index_name = "hackrx-policy-index"

    # Step A: Fetch, Chunk, Embed, and Index the Document
    print("\n--- Starting Document Processing ---")
    document_content = get_document_text(document_url)
    if not document_content:
        raise HTTPException(status_code=500, detail="Failed to retrieve or process document content.")
        
    chunks = split_text_into_chunks(document_content)
    if not chunks:
        raise HTTPException(status_code=500, detail="Failed to split document into chunks.")

    embeddings = generate_embeddings(chunks)
    if not embeddings:
        raise HTTPException(status_code=500, detail="Failed to generate embeddings for document chunks.")
        
    index_chunks_in_pinecone(chunks, embeddings, index_name)
    print("--- Document Processing and Indexing Complete ---\n")

    # Step B: Answer each question
    print("--- Answering Questions ---")
    answers = []
    try:
        index = pc.Index(index_name)
        
        for question in questions:
            # Create embedding for the question
            question_embedding_response = genai.embed_content(
                model="models/embedding-001",
                content=question,
                task_type="retrieval_query" # Specify task_type for better query embeddings
            )
            question_embedding = question_embedding_response['embedding']
            
            # Search Pinecone for relevant context
            search_results = index.query(
                vector=question_embedding,
                top_k=5, # Increased to 5 for more context
                include_metadata=True
            )
            
            context_chunks = [match.metadata['text'] for match in search_results.matches]
            context = "\n\n".join(context_chunks)
            
            # Generate the final answer using Gemini Pro
            answer = generate_answer_with_gemini(question, context)
            answers.append(answer)

    except Exception as e:
        print(f"An error occurred during the question answering phase: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    print("--- Finished Answering Questions ---")
    return {"answers": answers}