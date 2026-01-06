"""Streamlit frontend for RAG system."""

import streamlit as st
import httpx
from typing import Optional
from pathlib import Path
import tempfile

# Configure Streamlit
st.set_page_config(
    page_title="Biotech Startup RAG",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Configuration
API_URL = "http://localhost:8000"

class APIClient:
    """Client for interacting with the RAG API."""
    
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
    
    async def search(self, query: str, top_k: int = 5, doc_type: Optional[str] = None) -> dict:
        """Search documents."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/search",
                json={
                    "query": query,
                    "top_k": top_k,
                    "doc_type": doc_type,
                },
            )
            return response.json()
    
    async def upload(self, file_path: str) -> dict:
        """Upload a document."""
        async with httpx.AsyncClient(timeout=300.0) as client:
            with open(file_path, "rb") as f:
                files = {"file": (Path(file_path).name, f)}
                response = await client.post(
                    f"{self.base_url}/upload",
                    files=files,
                )
            return response.json()
    
    async def get_stats(self) -> dict:
        """Get system statistics."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/stats")
            return response.json()
    
    async def clear(self) -> dict:
        """Clear all documents."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(f"{self.base_url}/clear")
            return response.json()

# Initialize API client
api_client = APIClient()

# Sidebar
with st.sidebar:
    st.title("🧬 Biotech RAG")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Search", "Upload Documents", "Statistics", "Settings"],
        label_visibility="collapsed",
    )
    
    st.divider()
    
    # API Status
    try:
        import asyncio
        stats = asyncio.run(api_client.get_stats())
        st.success("✓ API Connected")
        st.metric("Documents", stats["total_documents"])
        st.metric("Chunks", stats["total_chunks"])
    except:
        st.error("✗ API Unavailable")
        st.info("Make sure the FastAPI backend is running on localhost:8000")

# Main content
if page == "Search":
    st.header("🔍 Search Documents")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Enter your search query",
            placeholder="e.g., 'recent progress on gene therapy'",
            label_visibility="collapsed",
        )
    
    with col2:
        top_k = st.number_input("Results", min_value=1, max_value=20, value=5)
    
    doc_type_filter = st.selectbox(
        "Filter by document type",
        ["All", "Meeting Minutes", "Progress Reports", "Research Papers"],
        key="doc_type_filter",
    )
    
    doc_type_map = {
        "All": None,
        "Meeting Minutes": "meeting_minutes",
        "Progress Reports": "progress_report",
        "Research Papers": "research_paper",
    }
    
    if query:
        with st.spinner("Searching..."):
            try:
                import asyncio
                results = asyncio.run(
                    api_client.search(
                        query,
                        top_k=top_k,
                        doc_type=doc_type_map[doc_type_filter],
                    )
                )
                
                if results["results"]:
                    st.success(f"Found {results['total']} results")
                    
                    for i, result in enumerate(results["results"], 1):
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**Result {i}**")
                                st.markdown(result["content"][:500] + "...")
                            
                            with col2:
                                st.metric("Combined Score", f"{result['combined_score']:.3f}")
                                st.caption(f"Vector: {result['vector_score']:.3f}")
                                st.caption(f"BM25: {result['bm25_score']:.3f}")
                            
                            with st.expander("Metadata"):
                                st.json(result["metadata"])
                else:
                    st.warning("No results found")
            
            except Exception as e:
                st.error(f"Search failed: {str(e)}")

elif page == "Upload Documents":
    st.header("📤 Upload Documents")
    
    st.info(
        "Supported formats: PDF, DOCX, TXT\n\n"
        "The system will automatically detect document type and apply optimal chunking strategy."
    )
    
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )
    
    if uploaded_files:
        if st.button("Process Documents", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                
                try:
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(
                        suffix=Path(uploaded_file.name).suffix,
                        delete=False,
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name
                    
                    # Upload to API
                    import asyncio
                    result = asyncio.run(api_client.upload(tmp_path))
                    
                    with st.container(border=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.success(f"✓ {uploaded_file.name}")
                            st.caption(f"Type: {result['doc_type']}")
                        with col2:
                            st.metric("Chunks Created", result['chunk_count'])
                    
                    # Cleanup
                    Path(tmp_path).unlink()
                
                except Exception as e:
                    st.error(f"✗ Failed to process {uploaded_file.name}: {str(e)}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.empty()
            st.success("Processing complete!")

elif page == "Statistics":
    st.header("📊 System Statistics")
    
    try:
        import asyncio
        stats = asyncio.run(api_client.get_stats())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Documents", stats["total_documents"])
        
        with col2:
            st.metric("Total Chunks", stats["total_chunks"])
        
        with col3:
            if stats["total_documents"] > 0:
                avg_chunks = stats["total_chunks"] / stats["total_documents"]
                st.metric("Avg Chunks/Doc", f"{avg_chunks:.1f}")
        
        st.divider()
        
        st.subheader("Documents by Type")
        if stats["documents_by_type"]:
            col1, col2 = st.columns(2)
            
            with col1:
                import plotly.graph_objects as go
                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=list(stats["documents_by_type"].keys()),
                            y=list(stats["documents_by_type"].values()),
                        )
                    ]
                )
                fig.update_layout(
                    title="Documents by Type",
                    xaxis_title="Document Type",
                    yaxis_title="Count",
                    height=400,
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.json(stats["documents_by_type"])
        
        st.divider()
        
        st.subheader("Processed Documents")
        if stats["documents"]:
            for doc in stats["documents"]:
                with st.expander(f"{Path(doc['file']).name} ({doc['doc_type']})"):
                    st.json(doc)
        else:
            st.info("No documents processed yet")
    
    except Exception as e:
        st.error(f"Failed to load statistics: {str(e)}")

elif page == "Settings":
    st.header("⚙️ Settings")
    
    st.subheader("API Configuration")
    st.code(f"API URL: {API_URL}", language="text")
    
    st.subheader("Document Processing")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Meeting Minutes Chunk Size", "300 tokens")
    
    with col2:
        st.metric("Progress Report Chunk Size", "500 tokens")
    
    with col3:
        st.metric("Research Paper Chunk Size", "1000 tokens")
    
    st.divider()
    
    st.subheader("Vector Search Settings")
    st.metric("Top-K Default", 5)
    st.metric("Search Strategy", "Hybrid (Vector + BM25)")
    
    st.divider()
    
    st.subheader("Dangerous Actions")
    
    if st.button("Clear All Documents", type="secondary"):
        if st.confirm("Are you sure? This will delete all indexed documents."):
            with st.spinner("Clearing..."):
                try:
                    import asyncio
                    asyncio.run(api_client.clear())
                    st.success("All documents cleared")
                except Exception as e:
                    st.error(f"Failed to clear: {str(e)}")
