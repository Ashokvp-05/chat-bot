# PDF Chatbot

This is a Streamlit application that allows you to chat with your PDF documents.

## Setup

1.  Make sure you have Python installed.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the environment:
    - Windows: `venv\Scripts\activate`
    - Mac/Linux: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt`

## Running the App

### Option 1: Using the provided script (Windows only)
Double-click `run_app.bat`.

### Option 2: Using the terminal
1.  Activate the virtual environment.
2.  Run the app: `streamlit run app.py`

### Option 3: Using VS Code
1.  Open the folder in VS Code.
2.  Go to the "Run and Debug" side bar.
3.  Select "Run Streamlit App" and click the green play button.

## Notes
- The first time you run the app, handle the embedding model will require downloading (approx. 100MB+ for `all-MiniLM-L6-v2` and `distilbert-base-cased-distilled-squad`).
- Place your PDF files inside the `docs/` folder before running.
