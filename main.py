import streamlit as st
from rag import process_urls, generate_answer

# Page configuration
st.set_page_config(
    page_title="URL Insights Explorer",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.header("📥 Input URLs")
url1 = st.sidebar.text_input("URL 1", placeholder="https://example.com/page1")
url2 = st.sidebar.text_input("URL 2", placeholder="https://example.com/page2")
url3 = st.sidebar.text_input("URL 3", placeholder="https://example.com/page3")

process_url_button = st.sidebar.button("🔄 Process URLs")

st.sidebar.markdown("---")
st.sidebar.header("❓ Ask a Question")
query = st.sidebar.text_input("Your question here...")
ask_button = st.sidebar.button("💬 Get Answer")

# Main area
st.title("🌐 URL Insights Explorer")
st.markdown(
    "Easily scrape and analyze content from any webpage URL, then ask questions to receive concise, sourced insights."
)

placeholder = st.empty()

# Process URLs
if process_url_button:
    urls = [url for url in (url1, url2, url3) if url.strip()]
    if not urls:
        placeholder.error("🚨 You must provide at least one valid URL.")
    else:
        with st.spinner("Processing URLs..."):
            for status in process_urls(urls):
                placeholder.info(status)

# Generate Answer
if ask_button and query:
    try:
        with st.spinner("Generating answer..."):
            answer, sources = generate_answer(query)

        st.subheader("📝 Answer")
        st.write(answer)

        if sources:
            st.subheader("🔗 Sources")
            for src in sources.split("\n"):
                st.markdown(f"- {src}")
    except RuntimeError:
        placeholder.error("🚨 You must process URLs before asking a question.")

# Footer
st.markdown("---")
