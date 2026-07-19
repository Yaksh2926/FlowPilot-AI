import streamlit as st
import pandas as pd
import time
import math
import re
from style import card
from utils import generate_ai_response

# --- Pure Python TF-IDF Cosine Similarity Search Engine ---
def tokenize(text):
    """
    Standardizes and tokenizes text to lowercase alphanumeric words.
    """
    return re.findall(r'\b\w+\b', text.lower())

def compute_tfidf(documents):
    """
    Computes TF-IDF vectors for documents.
    documents is a list of dicts: [{'id': id, 'content': text}]
    """
    # 1. Term frequencies per document
    doc_tfs = []
    all_words = set()
    for doc in documents:
        tokens = tokenize(doc['content'])
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        doc_tfs.append(tf)
        all_words.update(tokens)
        
    # 2. Document Frequency for IDF
    df = {}
    n_docs = len(documents)
    for tf in doc_tfs:
        for word in tf.keys():
            df[word] = df.get(word, 0) + 1
            
    # 3. Compute IDF
    idf = {}
    for word, count in df.items():
        # log smoothing
        idf[word] = math.log(1.0 + (n_docs / count))
        
    # 4. Compute TF-IDF Vectors
    doc_vectors = []
    for tf in doc_tfs:
        vec = {}
        for word, count in tf.items():
            vec[word] = count * idf[word]
        # Normalize vector for cosine similarity
        length = math.sqrt(sum(v**2 for v in vec.values()))
        if length > 0:
            vec = {k: v / length for k, v in vec.items()}
        doc_vectors.append(vec)
        
    return doc_vectors, idf

def retrieve_top_chunks(query, documents, doc_vectors, idf, top_n=2):
    """
    Performs cosine similarity search using the query against doc vectors.
    """
    query_tokens = tokenize(query)
    if not query_tokens or not doc_vectors:
        return []
        
    # 1. Compute query TF-IDF vector
    query_tf = {}
    for token in query_tokens:
        query_tf[token] = query_tf.get(token, 0) + 1
        
    query_vec = {}
    for word, count in query_tf.items():
        if word in idf:
            query_vec[word] = count * idf[word]
            
    # Normalize query vector
    q_length = math.sqrt(sum(v**2 for v in query_vec.values()))
    if q_length > 0:
        query_vec = {k: v / q_length for k, v in query_vec.items()}
    else:
        # Fallback if no matching query words
        return []

    # 2. Compute Cosine Similarity
    scores = []
    for i, doc_vec in enumerate(doc_vectors):
        score = 0.0
        # Dot product
        for word, val in query_vec.items():
            if word in doc_vec:
                score += val * doc_vec[word]
        if score > 0.05: # Threshold
            scores.append((score, documents[i]))
            
    # Sort by score descending
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:top_n]

def chunk_text(text, chunk_size=350, overlap=50):
    """
    Splits text into chunks of roughly chunk_size characters with overlap.
    """
    chunks = []
    words = text.split()
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1 # +1 for space
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            # keep overlap of words
            overlap_words = current_chunk[-max(1, int(overlap/10)):]
            current_chunk = list(overlap_words)
            current_length = sum(len(w)+1 for w in current_chunk)
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

# --- Page Render Function ---
def render_rag_page():
    st.title("📚 RAG Knowledge Base")
    st.markdown("##### Upload manuals, policies, or FAQs, index them, and test instant retrieval-augmented generation queries.")
    
    # Initialize RAG session variables
    if "rag_chunks" not in st.session_state:
        # Prepopulate with dummy documents divided into chunks
        initial_chunks = []
        for doc in st.session_state.kb_documents:
            c_list = chunk_text(doc["content"])
            for idx, c in enumerate(c_list):
                initial_chunks.append({
                    "chunk_id": f"{doc['id']}-C{idx+1}",
                    "title": doc["title"],
                    "content": c,
                    "added_at": doc["added_at"]
                })
        st.session_state.rag_chunks = initial_chunks

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown("### 📥 Index Corporate Documents")
        uploaded_file = st.file_uploader("Upload Company FAQ or Documentation (.txt, .md)", type=["txt", "md"])
        doc_title = st.text_input("Document Name/Title", placeholder="Product Manual v1.2")
        
        if st.button("Process & Index Document"):
            if uploaded_file and doc_title:
                try:
                    file_contents = uploaded_file.read().decode("utf-8")
                    chunks = chunk_text(file_contents)
                    
                    # Add to session kb_documents list
                    new_doc_id = f"DOC-{len(st.session_state.kb_documents)+1}"
                    st.session_state.kb_documents.append({
                        "id": new_doc_id,
                        "title": doc_title,
                        "content": file_contents[:400] + "...",
                        "added_at": time.strftime("%Y-%m-%d")
                    })
                    
                    # Add to active RAG chunks list
                    for idx, c in enumerate(chunks):
                        st.session_state.rag_chunks.append({
                            "chunk_id": f"{new_doc_id}-C{idx+1}",
                            "title": doc_title,
                            "content": c,
                            "added_at": time.strftime("%Y-%m-%d")
                        })
                        
                    st.success(f"Successfully chunked '{doc_title}' into {len(chunks)} fragments and added to Vector Index!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing file: {e}")
            else:
                st.warning("Please upload a valid file and specify a title.")
                
        # List indexed document metrics
        st.markdown("#### Indexed Document Sources")
        docs_df = pd.DataFrame(st.session_state.kb_documents)
        if not docs_df.empty:
            st.dataframe(docs_df, use_container_width=True, hide_index=True)
        else:
            st.info("No documents indexed yet.")

    with col_r:
        st.markdown("### 🔍 Test Knowledge Base Search")
        test_query = st.text_input("Ask a question about product capabilities or policies...", placeholder="What are the starter plan pricing options?")
        
        if test_query:
            # Build Vector Space Model and query
            chunks = st.session_state.rag_chunks
            
            if chunks:
                with st.spinner("Searching vector indices..."):
                    # Format chunks for compute_tfidf: list of dicts with 'content'
                    # we pass a wrapper
                    tfidf_docs = [{"id": c["chunk_id"], "content": c["content"]} for c in chunks]
                    doc_vectors, idf = compute_tfidf(tfidf_docs)
                    
                    # Retrieve top 2 matches
                    results = retrieve_top_chunks(test_query, chunks, doc_vectors, idf, top_n=2)
                    
                if results:
                    st.markdown("#### 🤖 RAG Synthesized Answer:")
                    
                    # Construct prompt with retrieved context
                    context_str = "\n\n".join([f"Source: {res[1]['title']}\nContent: {res[1]['content']}" for res in results])
                    system_prompt = "You are FlowPilot's RAG answering engine. Answer the user's question clearly, using ONLY the facts provided in the reference context. If the context doesn't contain the answer, say 'I couldn't find the answer in the provided documents.'"
                    user_prompt = f"Context Documents:\n{context_str}\n\nQuestion: {test_query}\n\nAnswer:"
                    
                    answer = generate_ai_response(user_prompt, system_instruction=system_prompt)
                    
                    st.markdown(f'<div class="glass-card" style="border-left: 4px solid #6366f1;">{answer}</div>', unsafe_allow_html=True)
                    
                    st.markdown("#### 🔗 Retrieved Context Snippets:")
                    for score, doc_info in results:
                        st.write(f"- **{doc_info['title']}** (Relevance Score: `{score*100:.1f}%`)")
                        st.caption(f"\"{doc_info['content']}\"")
                else:
                    st.warning("No relevant matching contexts found in the indexed files. Try adjusting your query keywords.")
            else:
                st.info("The knowledge index is empty. Upload documents first.")
