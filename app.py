import streamlit as st
from preprocess import load_documents
from sentence_transformers import SentenceTransformer
import faiss
from transformers import pipeline
import numpy as np

st.title("📄 PDF Document Chatbot")

# Caching document loading
@st.cache_data
def get_documents():
    return load_documents()

# Caching model loading
@st.cache_resource
def load_models():
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    qa_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    return embedding_model, qa_model

# Caching embeddings generation
@st.cache_resource
def get_embeddings(_model, docs):
    embeddings = _model.encode(docs)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index

with st.spinner("Initializing AI Engine..."):
    docs = get_documents()
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if len(docs) > 0:
    # Load models silently (cache handles speed)
    embedding_model, qa_model = load_models()
    index = get_embeddings(embedding_model, docs)
    
    with st.sidebar:
        st.success(f"Processed {len(docs)} chunks of text.")
        with st.expander("Debugging & Stats"):
            st.write(f"Total chunks: {len(docs)}")
            if len(docs) > 0:
                st.write(f"Sample: {docs[0][:100]}...")

    if prompt := st.chat_input("Ask a question about your PDF..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("Thinking..."):
                try:
                    q_vector = embedding_model.encode([prompt])
                    D, I = index.search(np.array(q_vector), k=3)
                    
                    retrieved_chunks = [docs[i] for i in I[0]]
                    context = " ".join(retrieved_chunks)
                    
                    answer = qa_model(question=prompt, context=context)
                    
                    response_text = answer['answer']
                    confidence = answer['score']

                    if confidence < 0.05:
                        full_response = f"⚠️ *Low confidence ({confidence:.2f})*\n\n{response_text}\n\n_I'm not sure if this is correct based on the document context._"
                    elif not response_text:
                        full_response = "I couldn't find a specific answer in the document."
                    else:
                        full_response = f"{response_text}\n\n*(Confidence: {confidence:.2f})*"
                    
                    # Optional: Show context in a collapsible section locally
                    with st.expander("View Source Context"):
                        for i, chunk in enumerate(retrieved_chunks):
                            st.caption(f"Context {i+1} (Match score: {D[0][i]:.2f})")
                            st.text(chunk)
                            
                except Exception as e:
                    full_response = f"Error processing your request: {e}"

            message_placeholder.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})

else:
    st.error("No text found. Please check your docs/ folder.")

with st.sidebar:
    st.divider()
    st.header("💡 Tips")
    st.markdown("""
    - Be specific.
    - Ask about facts in the document.
    - "Who", "What", "When", "Where".
    """)
