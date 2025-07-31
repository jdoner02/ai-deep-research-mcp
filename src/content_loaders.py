"""
Content Loaders for AI Deep Research MCP
Handles loading and parsing content from various sources (HTML, PDF, etc.)
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
import time
from urllib.parse import urlparse, urljoin

class HTMLContentLoader:
    """Loads and extracts content from HTML web pages"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def fetch_url(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        try:
            print(f"📥 Fetching content from: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Check if content is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'html' not in content_type:
                print(f"⚠️  Non-HTML content type: {content_type}")
                return None
                
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch {url}: {e}")
            return None
    
    def extract_content(self, html: str, source_url: str) -> Dict:
        """Extract clean content from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string.strip()
            elif soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            else:
                title = urlparse(source_url).netloc
            
            # Extract main content
            # Try to find main content areas
            content_candidates = []
            
            # Look for common content containers
            for selector in ['main', 'article', '.content', '.post', '.entry', '#content']:
                elements = soup.select(selector)
                if elements:
                    content_candidates.extend(elements)
            
            # If no specific content areas found, use body
            if not content_candidates:
                content_candidates = [soup.body] if soup.body else [soup]
            
            # Extract text from the best content candidate
            main_content = content_candidates[0] if content_candidates else soup
            
            # Get all text, preserving some structure
            paragraphs = []
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
                text = element.get_text().strip()
                if text and len(text) > 20:  # Filter out very short snippets
                    paragraphs.append(text)
            
            # Join paragraphs
            full_text = '\n\n'.join(paragraphs)
            
            # Clean up the text
            full_text = re.sub(r'\n\s*\n\s*\n', '\n\n', full_text)  # Remove excessive newlines
            full_text = re.sub(r'\s+', ' ', full_text)  # Normalize whitespace
            
            return {
                'title': title,
                'text': full_text,
                'source': source_url,
                'type': 'html',
                'length': len(full_text)
            }
            
        except Exception as e:
            print(f"❌ Failed to parse HTML content: {e}")
            return {
                'title': 'Parse Error',
                'text': '',
                'source': source_url,
                'type': 'html',
                'length': 0
            }
    
    def load_from_url(self, url: str) -> Optional[Dict]:
        """Load and extract content from a URL"""
        html = self.fetch_url(url)
        if html:
            return self.extract_content(html, url)
        return None

class MultiSourceContentLoader:
    """Loads content from multiple sources with different formats"""
    
    def __init__(self):
        self.html_loader = HTMLContentLoader()
    
    def load_multiple_urls(self, urls: list, max_concurrent: int = 3) -> list:
        """Load content from multiple URLs"""
        results = []
        
        for i, url in enumerate(urls):
            print(f"📄 Loading content {i+1}/{len(urls)}: {url}")
            
            try:
                # Determine content type and use appropriate loader
                if url.endswith('.pdf'):
                    # For now, skip PDFs (would need separate PDF loader)
                    print(f"⏭️  Skipping PDF: {url}")
                    continue
                else:
                    # Assume HTML content
                    content = self.html_loader.load_from_url(url)
                    if content and content['length'] > 100:  # Only include substantial content
                        results.append(content)
                        print(f"✅ Loaded {content['length']} characters from {content['title']}")
                    else:
                        print(f"❌ No substantial content from {url}")
                
                # Be polite - small delay between requests
                if i < len(urls) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error loading {url}: {e}")
                continue
        
        print(f"📊 Successfully loaded {len(results)} content sources")
        return results
