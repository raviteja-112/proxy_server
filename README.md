# MITMProxy Content Filter and Domain Blocker

## Overview

This project is a custom [mitmproxy](https://mitmproxy.org/) addon designed to intercept, filter, and block HTTP/HTTPS traffic based on predefined rules. It provides domain blocking, content filtering, and detailed logging capabilities with log rotation. The script is built to enhance network security and content control by restricting access to specific domains and censoring predefined keywords in HTML content while preserving the structure of web pages.

Developed with Python, this addon leverages libraries like `mitmproxy`, `BeautifulSoup`, and the Python `logging` module to provide robust functionality for network administrators.

## Features

- **Domain Blocking**: Blocks access to specified domains (e.g., `bing.com`, `youtube.com`) and serves a custom "Access Denied" page.
- **Content Filtering**: Filters out predefined keywords (e.g., "badword", "drugs") from HTML content, replacing them with `[FILTERED]`.
- **Advanced HTML Processing**: Preserves the structure of HTML pages during filtering using `BeautifulSoup` with `lxml` or `html.parser`.
- **Logging**: Logs all requests and responses with detailed headers (in debug mode) to a rotating log file (`proxy.log`).
- **Log Rotation**: Limits log file size to 10MB with up to 3 backup files to prevent disk space issues.
- **TLS Error Handling**: Logs TLS handshake failures for troubleshooting.

## Requirements

- Python 3.7+
- [mitmproxy](https://mitmproxy.org/) (`pip install mitmproxy`)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) (`pip install beautifulsoup4`)
- [lxml](https://lxml.de/) (optional, recommended for better HTML parsing: `pip install lxml`)

## Installation

1. **Clone or Download the Repository**  
   Clone this repository or download the script file (e.g., `proxy_script.py`) to your local machine.

   ```bash
   git clone https://github.com/raviteja-112/proxy_server.git
   ```

2. **Install Dependencies**  
   Install the required Python packages using pip:

   ```bash
   pip install mitmproxy beautifulsoup4 lxml
   ```

3. **Verify mitmproxy Installation**  
   Ensure `mitmproxy` is installed and accessible:

   ```bash
   mitmproxy --version
   ```

## Usage

1. **Run the Proxy**  
   Execute the script with `mitmweb` or `mitmproxy`:

   ```bash
   mitmweb -s proxy_script.py
   ```

   Alternatively, use `mitmproxy` for non-interactive mode:

   ```bash
   mitmproxy -s proxy_script.py
   ```

2. **Configure Client**  
   Set up your client (e.g., browser or device) to use the proxy. By default, mitmproxy listens on `localhost:8080`. Update your network settings to route traffic through this proxy.

3. **Monitor Logs**  
   Logs are written to `proxy.log` in the working directory. Check this file for request/response details and filtering events.

## Configuration

The script includes several configurable options at the top of the file:

- **`BLOCKED_DOMAINS`**: Set of domains to block (e.g., `{"bing.com", "youtube.com"}`).
- **`CONTENT_FILTER_WORDS`**: Set of words to filter from HTML content (e.g., `{"badword", "drugs"}`).
- **`LOG_FILE`**: Log file name (default: `proxy.log`).
- **`MAX_LOG_SIZE`**: Maximum log file size before rotation (default: 10MB).
- **`LOG_BACKUPS`**: Number of backup log files (default: 3).
- **`BLOCK_PAGE_HTML`**: Custom HTML template for the "Access Denied" page.
- **`REPLACEMENT_TEXT`**: Text to replace filtered words (default: `[FILTERED]`).

Modify these variables directly in the script to suit your needs.

### Example Configuration
```python
BLOCKED_DOMAINS = {"example.com", "socialmedia.com"}
CONTENT_FILTER_WORDS = {"secret", "confidential"}
LOG_FILE = "custom_proxy.log"
```

## Logging

- **Format**: Logs include timestamps, log levels, and messages (e.g., `2025-04-01 12:00:00 [INFO] REQ → GET http://example.com`).
- **Levels**: 
  - `INFO`: General request/response logging.
  - `WARNING`: Blocked requests or filtered content.
  - `ERROR`: TLS failures or content processing errors.
  - `DEBUG`: Detailed headers (disabled by default; enable by adjusting `logger.setLevel(logging.DEBUG)`).

Logs rotate automatically when the file size exceeds `MAX_LOG_SIZE`, ensuring efficient disk usage.

## Notes

- **Performance**: Using `lxml` as the HTML parser (if installed) improves parsing speed and structure preservation.
- **Security**: Ensure the proxy is properly secured (e.g., with SSL/TLS certificates) when deploying in a production environment.
- **Limitations**: Filtering is applied only to `text/html` content and skips `<script>`, `<style>`, and `<noscript>` tags to avoid breaking functionality.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue with suggestions, bug reports, or improvements.

## License

This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.

