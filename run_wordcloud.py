#!/usr/bin/env python3
"""
Module to scrape job descriptions from URLs and generate a wordcloud.
Designed for use with Streamlit applications.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path to import the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from urls_to_wordcloud.scrape_job_descriptions import scrape_job_descriptions
from urls_to_wordcloud.generate_wordcloud import (
    preprocess, calculate_word_frequencies, generate_wordcloud
)


def save_text_to_file(text, filename):
    """Save text content to a file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)


def create_wordcloud_from_urls(urls, n_gram_size=1, min_frequency=2, max_words=50, output_dir=None):
    """
    Scrape job descriptions from URLs and generate a wordcloud.

    Args:
        urls: List of URLs to scrape
        n_gram_size: Size of n-grams (1 for single words, 2 for bigrams, etc.)
        min_frequency: Minimum word frequency to include in wordcloud
        max_words: Maximum number of words to display in wordcloud
        output_dir: Directory to save temporary files (optional)

    Returns:
        dict: Results containing:
            - success: bool indicating if wordcloud was generated
            - message: str with status message
            - word_counts: dict of word frequencies (if successful)
            - combined_text: str of all scraped text (if successful)
            - scraped_results: dict of scraping results
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
    scraped_results = scrape_job_descriptions(valid_urls)

    # Collect all text content
    all_texts = []
    successful_scrapes = 0

    for domain, (text, error) in scraped_results.items():
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

    # Save combined text to file if output_dir is specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        combined_file = output_path / "combined_job_descriptions.txt"
        save_text_to_file(combined_text, combined_file)

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

    # Generate wordcloud
    generate_wordcloud(word_counts, max_words, min_frequency, n_gram_size)

    return {
        'success': True,
        'message': f'Successfully generated wordcloud from {successful_scrapes} URLs with {len(word_counts)} unique words.',
        'word_counts': word_counts,
        'combined_text': combined_text,
        'scraped_results': scraped_results
    }


def get_top_words(word_counts, top_n=10):
    """
    Get the top N most frequent words from word_counts.

    Args:
        word_counts: Dictionary of word frequencies
        top_n: Number of top words to return

    Returns:
        list: List of tuples (word, count) sorted by frequency
    """
    if not word_counts:
        return []

    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:top_n]


def validate_urls(urls):
    """
    Validate a list of URLs.

    Args:
        urls: List of URLs to validate

    Returns:
        tuple: (valid_urls, invalid_urls)
    """
    valid_urls = []
    invalid_urls = []

    for url in urls:
        if url.startswith(('http://', 'https://')):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)

    return valid_urls, invalid_urls