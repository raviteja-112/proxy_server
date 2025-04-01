from mitmproxy import http, ctx
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString
import re

# Configuration
BLOCKED_DOMAINS = {"bing.com", "youtube.com"}
LOG_FILE = "proxy.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUPS = 3
BLOCK_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Blocked</title></head>
<body style="font-family: Arial; padding: 50px;">
  <h1 style="color: #cc0000;">Access Denied</h1>
  <p>The site <strong>{domain}</strong> has been blocked by the Network Administrator.</p>
  <p>Contact Network Administrator for additional information.</p>
</body>
</html>
"""

CONTENT_FILTER_WORDS = {
    "badword", "inappropriate", "offensive", "bomb", "VIT", "hello", "china", "drugs", "torture"
}
REPLACEMENT_TEXT = "[FILTERED]"

class FeatureModule:
    def __init__(self):
        # Configure logging with rotation
        self.logger = logging.getLogger("CustomProxyLogger")
        self.logger.setLevel(logging.INFO)

        # Configure rotating file handler
        file_handler = RotatingFileHandler(
            LOG_FILE,
            mode='a',
            maxBytes=MAX_LOG_SIZE,
            backupCount=LOG_BACKUPS,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.propagate = False

        self.blocked_count = 0
        self.parser = self._determine_best_parser()

    def _determine_best_parser(self):
        """Select best HTML parser preserving structure"""
        try:
            # Prefer lxml for better HTML structure preservation
            soup = BeautifulSoup("", "lxml")
            return "lxml"
        except Exception:
            return "html.parser"

    def request(self, flow: http.HTTPFlow):
        if any(domain in flow.request.pretty_host for domain in BLOCKED_DOMAINS):
            self.blocked_count += 1
            self._block_request(flow)
            return

        self._log_request(flow)

    def response(self, flow: http.HTTPFlow):
        self._log_response(flow)

        if "text/html" in flow.response.headers.get("Content-Type", ""):
            self._filter_content(flow)

    def _block_request(self, flow: http.HTTPFlow):
        domain = flow.request.pretty_host
        self.logger.warning(f"Blocked request to {domain}")
        block_html = BLOCK_PAGE_HTML.format(domain=domain)
        flow.response = http.Response.make(
            403,
            block_html.encode(),
            {"Content-Type": "text/html"}
        )

    def _log_request(self, flow: http.HTTPFlow):
        self.logger.info(f"REQ → {flow.request.method} {flow.request.pretty_url}")
        if flow.request.headers:
            self.logger.debug(f"Headers: {dict(flow.request.headers)}")

    def _log_response(self, flow: http.HTTPFlow):
        self.logger.info(f"RES ← {flow.response.status_code} {flow.request.pretty_url}")
        if flow.response.headers:
            self.logger.debug(f"Headers: {dict(flow.response.headers)}")

    def _filter_content(self, flow: http.HTTPFlow):
        try:
            content = flow.response.text
            modified_content = self._process_html(content)
            if modified_content != content:
                flow.response.text = modified_content
                self.logger.warning(f"Filtered content in {flow.request.pretty_url}")
        except Exception as e:
            self.logger.error(f"Error filtering content: {e}")

    def _process_html(self, content: str) -> str:
        """Advanced HTML processing preserving structure"""
        soup = BeautifulSoup(content, self.parser)

        # Create regex pattern for forbidden words
        pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, CONTENT_FILTER_WORDS)) + r')\b',
            flags=re.IGNORECASE
        )

        # Process all text nodes while preserving structure
        for element in soup.find_all(text=True):
            parent_tag = element.parent.name.lower() if element.parent else ""
            
            # Skip non-visible content and special tags
            if parent_tag in ("script", "style", "noscript"):
                continue

            # Replace forbidden words while preserving whitespace
            new_text = pattern.sub(REPLACEMENT_TEXT, element)
            
            # Preserve original structure and whitespace
            if isinstance(element, NavigableString) and new_text != element:
                element.replace_with(new_text)

        # Serialize HTML without introducing formatting changes
        return str(soup).replace(">", ">\n").replace("<", "\n<")

    def server_tls_failed(self, flow: http.HTTPFlow, error: str):
        self.logger.error(f"TLS handshake failed with {flow.server_conn.address}: {error}")

addons = [
    FeatureModule()
]