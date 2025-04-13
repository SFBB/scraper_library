# Scraper Library

The Scraper Library is a Python-based module designed to scrape and process data from various sources, such as novels, and audio books.

## Features
- **Multi-Source Scraping**: Supports scraping from multiple platforms like 69Shu, Ximalaya, Syosetu, and more.
- **Adapters**: Includes text and audio file adapters for flexible data handling.
- **Progress Tracking**: Provides real-time progress reporting during scraping operations.
- **Threading**: Utilizes multi-threading for efficient data scraping.

## Project Structure
- `adapters/`: Contains adapters for handling different data formats (e.g., text, audio).
- `components/`: Includes utility components like progress reporters.
- `scrapers/`: Houses scraper implementations for various platforms.
- `src/`: Core library code, including utilities and the main coordinator.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/SFBB/scraper_library.git
   cd scraper_library
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the scrapers using the provided CLI or scripts. For example:
```bash
python -m src.novel_scraper_cli --source syosetu --url https://ncode.syosetu.com/n2267be/
```

## Supported Scrapers
- **69Shu**: Scrapes novels from 69Shu.net.
- **Ximalaya**: Extracts audio books from Ximalaya.
- **Syosetu**: Fetches novels from Syosetu (Japanese).
- **Quanben**: Retrieves novels from Quanben.
- **BaoBao88**: Scrapes audio novels from BaoBao88.

## Development
### Running Tests
Run the test suite to ensure everything works as expected:
```bash
pytest
```

### Code Style
Follow PEP 8 guidelines for Python code. Use tools like `flake8` for linting:
```bash
flake8 src/
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
