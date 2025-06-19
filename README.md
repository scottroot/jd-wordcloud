# Job Description Wordcloud Generator

A Streamlit web application that scrapes job descriptions from URLs and generates interactive wordclouds to analyze common terms and requirements.

## Features

- 🔗 **URL Scraping**: Automatically scrape job descriptions from multiple URLs
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

3. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

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
- **Output Directory**: Optional directory to save combined text files

## Deployment Options

### Streamlit Cloud

1. Push your code to GitHub
2. Connect your repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy with the following settings:
   - **Main file path**: `app.py`
   - **Python version**: 3.9

### Heroku

1. **Create a `Procfile`**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### AWS/GCP/Azure

Use the provided Dockerfile for container deployment:

```bash
# Build the image
docker build -t wordcloud-app .

# Run the container
docker run -p 8501:8501 wordcloud-app
```

## Project Structure

```
jd-wordcloud/
├── app.py                          # Main Streamlit application
├── run_wordcloud.py               # Core wordcloud generation module
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── .streamlit/
│   └── config.toml               # Streamlit configuration
├── urls_to_wordcloud/            # Package directory
│   ├── __init__.py
│   ├── scrape_job_descriptions.py
│   └── generate_wordcloud.py
└── README.md                     # This file
```

## Dependencies

### Core Dependencies
- **Streamlit**: Web application framework
- **Selenium**: Web scraping and browser automation
- **BeautifulSoup4**: HTML parsing
- **WordCloud**: Wordcloud generation
- **NLTK**: Natural language processing
- **Plotly**: Interactive data visualization
- **Pandas**: Data manipulation

### System Dependencies
- **Chrome/ChromeDriver**: Required for web scraping (included in Docker)

## Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver not found**
   - Use the provided Dockerfile which includes Chrome
   - Or install Chrome and ChromeDriver manually

2. **NLTK data missing**
   - Run: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`

3. **Port already in use**
   - Change the port in `.streamlit/config.toml` or use `--server.port=8502`

4. **Memory issues with large datasets**
   - Reduce the number of URLs or increase Docker memory limits

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