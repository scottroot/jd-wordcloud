from urls_to_wordcloud import scrape_url, calculate_word_frequencies, get_top_words
import streamlit as st
import pandas as pd
from requests_html import HTMLSession
import re
import time
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from urllib.parse import urlparse
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
import asyncio
import nest_asyncio

# Apply nest_asyncio to handle event loop issues in Streamlit
nest_asyncio.apply()

# Download NLTK data efficiently
@st.cache_resource
def download_nltk_data():
    """Download NLTK data once and cache the result."""
    try:
        # Check if data already exists
        nltk.data.find('corpora/stopwords')
        nltk.data.find('tokenizers/punkt')
        return True
    except LookupError:
        # Download missing data
        with st.spinner("📥 Downloading NLTK data (this only happens once)..."):
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
        return True

# Download NLTK data on app startup
download_nltk_data()

# Page configuration
st.set_page_config(
    page_title="Job Description Wordcloud Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def generate_wordcloud_plotly(word_counts, max_words=50):
    """Generate wordcloud and return as base64 image for Streamlit."""
    if not word_counts:
        return None

    # Create wordcloud
    wordcloud = WordCloud(
        width=1200,
        height=800,
        background_color="white",
        max_words=max_words,
        colormap='viridis',
        relative_scaling=0.5
    )

    wordcloud.generate_from_frequencies(word_counts)

    # Convert to image
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout()

    # Convert to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()

    return img_str


def create_wordcloud_from_urls(urls, n_gram_size=1, min_frequency=2, max_words=50):
    """
    Scrape job descriptions from URLs and generate a wordcloud.
    Streamlit Cloud compatible version using requests_html.
    """
    if not urls:
        return {
            'success': False,
            'message': 'No URLs provided.',
            'word_counts': {},
            'combined_text': '',
            'scraped_results': {}
        }

    # Validate URLs
    valid_urls = []
    for url in urls:
        if url.startswith(('http://', 'https://')):
            valid_urls.append(url)

    if not valid_urls:
        return {
            'success': False,
            'message': 'No valid URLs found.',
            'word_counts': {},
            'combined_text': '',
            'scraped_results': {}
        }

    # Scrape job descriptions
    scraped_results = {}
    all_texts = []
    successful_scrapes = 0

    for url in valid_urls:
        domain = urlparse(url).netloc
        text, error = scrape_url(url)
        scraped_results[domain] = (text, error)

        if not error:
            all_texts.append(text)
            successful_scrapes += 1

    if not all_texts:
        return {
            'success': False,
            'message': f'No content was successfully scraped from {len(valid_urls)} URLs.',
            'word_counts': {},
            'combined_text': '',
            'scraped_results': scraped_results
        }

    # Combine all text
    combined_text = " ".join(all_texts)

    # Calculate word frequencies
    word_counts = calculate_word_frequencies([combined_text], min_frequency, n_gram_size)

    if not word_counts:
        return {
            'success': False,
            'message': f'No words found matching the minimum frequency criteria ({min_frequency}).',
            'word_counts': {},
            'combined_text': combined_text,
            'scraped_results': scraped_results
        }

    return {
        'success': True,
        'message': f'Successfully generated wordcloud from {successful_scrapes} URLs with {len(word_counts)} unique words.',
        'word_counts': word_counts,
        'combined_text': combined_text,
        'scraped_results': scraped_results
    }


def validate_urls(urls):
    """Validate a list of URLs."""
    valid_urls = []
    invalid_urls = []

    for url in urls:
        if url.startswith(('http://', 'https://')):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)

    return valid_urls, invalid_urls

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Job Description Wordcloud Generator</h1>', unsafe_allow_html=True)

    # # Info about improved scraping
    # st.info("""
    # ✅ **Enhanced Scraping**: This version uses requests_html to render JavaScript content,
    # making it much more effective at extracting job descriptions from modern websites.
    # """)

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Wordcloud parameters
        st.subheader("Wordcloud Settings")
        n_gram_size = st.selectbox(
            "N-gram Size",
            options=[1, 2, 3],
            index=0,
            help="1 = single words, 2 = word pairs, 3 = word triplets"
        )

        min_frequency = st.number_input(
            "Minimum Frequency",
            min_value=1,
            value=2,
            help="Minimum number of times a word must appear to be included"
        )

        max_words = st.number_input(
            "Maximum Words",
            min_value=10,
            max_value=200,
            value=50,
            help="Maximum number of words to display in the wordcloud"
        )

        st.markdown("---")
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. Enter job URLs in the text area (one per line)
        2. Adjust wordcloud settings in the sidebar
        3. Click 'Generate Wordcloud' to start processing
        4. View results and download data
        """)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🔗 Job URLs")

        # URL input
        urls_input = st.text_area(
            "Enter job URLs (one per line):",
            height=200,
            placeholder="https://example.com/job1\nhttps://example.com/job2\nhttps://example.com/job3"
        )

        # Parse URLs
        urls = [url.strip() for url in urls_input.split('\n') if url.strip()]

        # Validate URLs
        if urls:
            valid_urls, invalid_urls = validate_urls(urls)

            if invalid_urls:
                st.warning(f"⚠️ {len(invalid_urls)} invalid URL(s) found and will be skipped:")
                for url in invalid_urls:
                    st.code(url)

        # Generate button
        generate_button = st.button(
            "🚀 Generate Wordcloud",
            type="primary",
            use_container_width=True
        )

    with col2:
        st.header("📈 Quick Stats")

        if urls:
            valid_urls, _ = validate_urls(urls)
            st.metric("Total URLs", len(urls))
            st.metric("Valid URLs", len(valid_urls))
            st.metric("Invalid URLs", len(urls) - len(valid_urls))
        else:
            st.info("Enter URLs to see statistics")

    # Processing and results
    if generate_button and urls:
        valid_urls, _ = validate_urls(urls)

        if not valid_urls:
            st.error("❌ No valid URLs to process. Please check your input.")
            return

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Update status
            status_text.text("🔄 Scraping job descriptions (this may take a moment for JavaScript rendering)...")
            progress_bar.progress(25)

            # Generate wordcloud
            result = create_wordcloud_from_urls(
                urls=valid_urls,
                n_gram_size=n_gram_size,
                min_frequency=min_frequency,
                max_words=max_words
            )

            progress_bar.progress(100)
            status_text.text("✅ Processing complete!")
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()

            # Display results
            if result['success']:
                st.success(result['message'])

                # Results tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Wordcloud", "📋 Top Words", "📈 Statistics", "📄 Raw Data"])

                with tab1:
                    st.subheader("Generated Wordcloud")

                    # Generate and display wordcloud
                    wordcloud_img = generate_wordcloud_plotly(result['word_counts'], max_words)
                    if wordcloud_img:
                        st.image(f"data:image/png;base64,{wordcloud_img}", use_container_width=True)
                    else:
                        st.error("Could not generate wordcloud")

                with tab2:
                    st.subheader("Top 20 Most Frequent Words")
                    top_words = get_top_words(result['word_counts'], 20)

                    if top_words:
                        # Create a DataFrame for better display
                        df_top_words = pd.DataFrame(top_words, columns=['Word', 'Frequency'])

                        # Display as table
                        st.dataframe(df_top_words, use_container_width=True)

                        # Create bar chart
                        fig = px.bar(
                            df_top_words.head(10),
                            x='Frequency',
                            y='Word',
                            orientation='h',
                            title="Top 10 Most Frequent Words",
                            color='Frequency',
                            color_continuous_scale='viridis'
                        )
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)

                        # Download option
                        csv = df_top_words.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Top Words CSV",
                            data=csv,
                            file_name="top_words.csv",
                            mime="text/csv"
                        )

                with tab3:
                    st.subheader("Scraping Statistics")

                    # Scraping results
                    scraped_results = result['scraped_results']
                    successful = sum(1 for _, (_, error) in scraped_results.items() if not error)
                    failed = len(scraped_results) - successful

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total URLs", len(scraped_results))
                    with col2:
                        st.metric("Successful", successful)
                    with col3:
                        st.metric("Failed", failed)

                    # Detailed results
                    st.subheader("Detailed Results")
                    for domain, (text, error) in scraped_results.items():
                        if error:
                            st.error(f"❌ {domain}: {error}")
                        else:
                            st.success(f"✅ {domain}: {len(text)} characters")

                with tab4:
                    st.subheader("Raw Data")

                    # Combined text info
                    combined_text = result['combined_text']
                    st.metric("Total Characters", len(combined_text))
                    st.metric("Total Words", len(combined_text.split()))

                    # Show sample of combined text
                    with st.expander("View Combined Text Sample (first 1000 characters)"):
                        st.text(combined_text[:1000] + "..." if len(combined_text) > 1000 else combined_text)

                    # Download combined text
                    st.download_button(
                        label="📥 Download Combined Text",
                        data=combined_text,
                        file_name="combined_job_descriptions.txt",
                        mime="text/plain"
                    )

                    # Download word frequencies
                    word_freq_df = pd.DataFrame(
                        result['word_counts'].items(),
                        columns=['Word', 'Frequency']
                    ).sort_values('Frequency', ascending=False)

                    csv_freq = word_freq_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download All Word Frequencies",
                        data=csv_freq,
                        file_name="word_frequencies.csv",
                        mime="text/csv"
                    )

            else:
                st.error(f"❌ {result['message']}")

                # Show partial results if available
                if result['scraped_results']:
                    st.subheader("Scraping Results")
                    for domain, (text, error) in result['scraped_results'].items():
                        if error:
                            st.error(f"❌ {domain}: {error}")
                        else:
                            st.success(f"✅ {domain}: {len(text)} characters")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.exception(e)

    elif generate_button and not urls:
        st.warning("⚠️ Please enter at least one URL to generate a wordcloud.")

if __name__ == "__main__":
    main()