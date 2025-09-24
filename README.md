## InsuranceDoc AI

An AI-powered application designed to process insurance policy documents and answer user questions using a Retrieval-Augmented Generation (RAG) pipeline. This project consists of a FastAPI backend and a React frontend.

-----

### Key Features

  * **Document Processing:** Takes a public PDF URL, extracts text, and processes it for AI querying.
  * **Vector Database:** Embeds document text chunks and stores them in a Pinecone vector index.
  * **Intelligent Q\&A:** Uses the Gemini AI model to answer questions based **only** on the content of the provided document.
  * **Efficient Lookups:** Utilizes a consistent document ID to check if a document has already been processed, skipping redundant work.
  * **Responsive Frontend:** A simple, clean chat interface built with React to interact with the API.

-----

### Tech Stack

**Backend:**

  * **Python:** The core language for the API.
  * **FastAPI:** A modern, fast web framework for building the API endpoints.
  * **Google Gemini API:** The Large Language Model (LLM) used for generating answers.
  * **Pinecone:** A serverless vector database used for storing document embeddings.
  * **`requests` & `fitz`:** Libraries for downloading and parsing PDF files.

**Frontend:**

  * **React:** A JavaScript library for building the user interface.
  * **Vite:** A fast build tool for setting up and running the React development server.
  * **HTML, CSS, JavaScript:** Standard web technologies.

-----

### Getting Started

These instructions will get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

  * [Python 3.9+](https://www.python.org/downloads/)
  * [Node.js 18+](https://nodejs.org/en) and npm
  * A **Google API Key** for Gemini AI
  * A **Pinecone API Key** and a Pinecone Index

### Local Setup

The project is structured with a `hackathon-project` folder for the backend and a `frontend` folder for the React app.

#### 1\. Backend Setup

1.  Navigate to the `hackathon-project` directory.
    ```bash
    cd hackathon-project
    ```
2.  Create a Python virtual environment and activate it.
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  Install the required Python packages.
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a **`.env`** file in the `hackathon-project` directory and add your API keys.
    ```
    HACKATHON_API_KEY="your-secret-api-key"
    GOOGLE_API_KEY="your-google-api-key"
    PINECONE_API_KEY="your-pinecone-api-key"
    ```
5.  Start the FastAPI server.
    ```bash
    uvicorn main:app --reload
    ```
    The backend will run on `http://127.0.0.1:8000`.

#### 2\. Frontend Setup

1.  Open a new terminal and navigate to the `frontend` directory.
    ```bash
    cd frontend
    ```
2.  Install the Node.js dependencies.
    ```bash
    npm install
    ```
3.  Create a **`.env`** file in the `frontend` directory and add the following variables, pointing to your local backend.
    ```
    VITE_REACT_APP_API_URL_ENDPOINT=http://127.0.0.1:8000/hackrx/run
    VITE_REACT_APP_HACKATHON_API_KEY="your-secret-api-key"
    ```
4.  Start the React development server.
    ```bash
    npm run dev
    ```
    The frontend will run on `http://localhost:5173`.

-----

### API Endpoint

The primary backend endpoint for interaction is:

  * **POST** `/hackrx/run`
      * **Description:** Processes a document from a URL and answers a list of questions.
      * **Request Body (JSON):**
        ```json
        {
          "documents": "string_url_to_pdf",
          "questions": ["What is the policy period?", "What is the premium?"]
        }
        ```
      * **Headers:**
          * `Authorization: Bearer YOUR_HACKATHON_API_KEY`
      * **Response (JSON):**
        ```json
        {
          "answers": ["Answer to question 1.", "Answer to question 2."]
        }
        ```

-----

### Deployment

This project is configured for deployment on **Render.com**. Both the backend and frontend are hosted as separate services.

  * **Backend:** Deployed as a **Web Service**, pointing to the `hackathon-project` root directory.
  * **Frontend:** Deployed as a **Static Site**, pointing to the `frontend` root directory with the build command `npm run build` and publish directory `dist`. Remember to configure the environment variables with your live backend URL.

### Developed By

This project has been developed by:
* **Pragyan Srivastava** (pragyan20github)
* **Vanshita Bihani** (vanshita-bihani)
* **Gracy Shivhare** (gracyshivhare)
* **Yoshita Banerjee** (YoshitaB)
* **Hemal Vadaliya** (CodeHem4444)
