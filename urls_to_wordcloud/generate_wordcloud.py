import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import os
import glob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

nltk.download('punkt_tab')
# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')

def preprocess_text(text, n_gram_size=1):
    """Clean and tokenize text, optionally creating n-grams."""
    # Remove non-alphanumeric characters and convert to lowercase
    text = re.sub(r'\W+', ' ', text.lower())

    # Tokenize words
    words = word_tokenize(text)

    # Filter out short words and stop words
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if len(word) > 2 and word not in stop_words]

    # Create n-grams if specified
    if n_gram_size > 1:
        ngrams = []
        for i in range(len(filtered_words) - n_gram_size + 1):
            ngram = ' '.join(filtered_words[i:i + n_gram_size])
            ngrams.append(ngram)
        return ngrams
    else:
        return filtered_words


def calculate_word_frequencies(texts, min_frequency=1, n_gram_size=1):
    """Calculate word frequencies from texts, filtering by minimum frequency."""
    word_counts = Counter()

    for text in texts:
        words = preprocess_text(text, n_gram_size)
        word_counts.update(words)

    # Filter words by minimum frequency
    filtered_counts = {word: count for word, count in word_counts.items()
                      if count >= min_frequency}

    return filtered_counts


def get_top_words(word_counts, top_n=10):
    """Get the top N most frequent words from word_counts."""
    if not word_counts:
        return []

    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:top_n]


def generate_wordcloud(word_counts, max_words=50, min_frequency=2, n_gram_size=1):
    """Generate and display word cloud."""
    if not word_counts:
        print("No words found matching the minimum frequency criteria.")
        return

    wordcloud = WordCloud(
        width=1200,
        height=800,
        background_color="white",
        max_words=max_words,
        colormap='viridis',
        relative_scaling=0.5
    )

    wordcloud.generate_from_frequencies(word_counts)

    # Plot WordCloud
    plt.figure(figsize=(15, 10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")

    ngram_text = f" ({n_gram_size}-grams)" if n_gram_size > 1 else ""
    plt.title(f"Word Cloud from Job Descriptions{ngram_text} (min frequency: {min_frequency})",
              fontsize=16, pad=20)
    plt.tight_layout()
    plt.show()

def create_job_descriptions_wordcloud(n_gram_size=1, min_frequency=2, max_words=50):
    """Create a word cloud from job description files with specified parameters."""
    # Define the path to job description files
    job_files_path = "job_descriptions/*.txt"

    # Check if files exist
    if not glob.glob(job_files_path):
        print(f"No files found matching pattern: {job_files_path}")
        return

    # Read all job description files
    print(f"Reading job description files from {job_files_path}...")
    corpus = read_files(job_files_path)
    print(f"Read {len(corpus)} files")

    # Calculate word frequencies
    ngram_text = f" ({n_gram_size}-grams)" if n_gram_size > 1 else ""
    print(f"Calculating word frequencies{ngram_text} (min frequency: {min_frequency})...")
    word_counts = calculate_word_frequencies(corpus, min_frequency, n_gram_size)
    print(f"Found {len(word_counts)} unique words{ngram_text} with frequency >= {min_frequency}")

    # Generate and display word cloud
    print("Generating word cloud...")
    generate_wordcloud(word_counts, max_words, min_frequency, n_gram_size)

if __name__ == "__main__":
    # Example usage - you can modify these parameters
    create_job_descriptions_wordcloud(n_gram_size=2, min_frequency=2, max_words=50)
