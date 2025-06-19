# Job Description Wordcloud Generator

A Streamlit web application that scrapes job descriptions from URLs and generates interactive wordclouds to analyze common terms and requirements.

## Features

- 🔗 **URL Scraping**: Automatically scrape job descriptions from multiple URLs using requests-html
- 📊 **Interactive Wordclouds**: Generate beautiful wordclouds with customizable parameters
- 📈 **Data Visualization**: View top words with frequency charts
- 📋 **Data Export**: Download results as CSV files
- ⚙️ **Customizable Settings**: Adjust n-gram size, frequency thresholds, and word limits
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd jd-wordcloud
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download NLTK data (one-time setup)**
   ```bash
   python setup_nltk.py
   ```
   Or manually:
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

4. **Run the app**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

### Using Dev Container (Recommended)

If you're using VS Code with Dev Containers:

1. **Open in Dev Container**
   - Open the project in VS Code
   - When prompted, click "Reopen in Container"
   - The container will automatically install dependencies and download NLTK data

2. **The app will start automatically**
   - Streamlit will be available at `http://localhost:8501`
   - All dependencies and NLTK data are pre-configured

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Or build and run manually**
   ```bash
   docker build -t wordcloud-app .
   docker run -p 8501:8501 wordcloud-app
   ```

## Usage

1. **Enter Job URLs**: Paste job URLs in the text area (one per line)
2. **Configure Settings**: Adjust wordcloud parameters in the sidebar
3. **Generate Wordcloud**: Click the "Generate Wordcloud" button
4. **View Results**: Explore the results in the interactive tabs

### Configuration Options

- **N-gram Size**: 1 (single words), 2 (word pairs), 3 (word triplets)
- **Minimum Frequency**: Minimum times a word must appear to be included
- **Maximum Words**: Maximum number of words to display in the wordcloud

## Project Structure

```
jd-wordcloud/
├── streamlit_app.py              # Main Streamlit application
├── setup_nltk.py                 # NLTK data setup script
├── requirements.txt              # Python dependencies
├── .devcontainer/
│   └── devcontainer.json        # Dev container configuration
├── urls_to_wordcloud/           # Package directory
│   ├── __init__.py
│   ├── scrape_url.py
│   └── generate_wordcloud.py
└── README.md                    # This file
```

## Dependencies

### Core Dependencies
- **Streamlit**: Web application framework
- **requests-html**: Web scraping with JavaScript rendering
- **BeautifulSoup4**: HTML parsing
- **WordCloud**: Wordcloud generation
- **NLTK**: Natural language processing
- **Plotly**: Interactive data visualization
- **Pandas**: Data manipulation
- **nest-asyncio**: Async support for Streamlit

## Troubleshooting

### Common Issues

1. **NLTK data missing**
   - Run: `python setup_nltk.py`
   - Or manually: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`

2. **ModuleNotFoundError: No module named 'requests_html'**
   - Install missing dependencies: `pip install -r requirements.txt`

3. **App hangs on startup**
   - This usually means NLTK data is being downloaded. Wait for it to complete (only happens once)

4. **Port already in use**
   - Change the port: `streamlit run streamlit_app.py --server.port=8502`

### Performance Tips

- Limit the number of URLs to 10-20 for optimal performance
- Use n-gram size 1 for faster processing
- Increase minimum frequency to reduce word count

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information