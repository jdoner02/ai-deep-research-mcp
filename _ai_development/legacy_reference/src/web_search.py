"""
Web Search Component for AI Deep Research MCP
Provides web search functionality using DuckDuckGo
"""
import asyncio
import time
from typing import List, Dict, Optional
from duckduckgo_search import DDGS
import logging

class WebSearcher:
    """Web search component using DuckDuckGo search"""
    
    def __init__(self, max_results: int = 10, safe_search: str = "moderate"):
        self.max_results = max_results
        self.safe_search = safe_search
        self.ddgs = DDGS()
        
    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        Search the web for the given query
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with 'url', 'title', 'snippet' keys
        """
        results_limit = max_results or self.max_results
        
        try:
            print(f"🔍 Searching web for: '{query}'")
            
            # Use DuckDuckGo search
            search_results = []
            
            # Get web search results
            ddg_results = self.ddgs.text(
                query, 
                max_results=results_limit,
                safesearch=self.safe_search
            )
            
            for result in ddg_results:
                search_results.append({
                    'url': result.get('href', ''),
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'source': 'duckduckgo'
                })
                
            print(f"📊 Found {len(search_results)} search results")
            return search_results
            
        except Exception as e:
            print(f"❌ Web search failed: {e}")
            return []
    
    def search_educational(self, query: str) -> List[Dict]:
        """
        Search specifically for educational content
        Adds site filters for educational domains
        """
        # Add educational site preferences to query
        educational_query = f"{query} site:edu OR site:org OR curriculum OR syllabus"
        return self.search(educational_query)
    
    def search_ap_cyber(self) -> List[Dict]:
        """
        Specialized search for AP Cybersecurity content
        """
        queries = [
            "AP Computer Science Principles cybersecurity curriculum",
            "Advanced Placement cybersecurity course content",
            "AP CSP cyber security units College Board",
            "high school cybersecurity curriculum AP exam"
        ]
        
        all_results = []
        for query in queries:
            results = self.search(query, max_results=5)
            all_results.extend(results)
            time.sleep(1)  # Be polite to search engine
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results[:15]  # Return top 15 unique results


class EnhancedWebSearcher:
    """Enhanced web searcher that integrates scholarly sources"""
    
    def __init__(self, include_scholarly: bool = True):
        self.web_searcher = WebSearcher()
        self.include_scholarly = include_scholarly
        
        if include_scholarly:
            from .scholarly_sources import UnifiedScholarlySearcher
            self.scholarly_searcher = UnifiedScholarlySearcher()
    
    def search(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Enhanced search that combines web and scholarly results
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Combined list of web and scholarly results
        """
        all_results = []
        
        # Get web results (60% of total)
        web_results_count = int(max_results * 0.6)
        web_results = self.web_searcher.search(query, web_results_count)
        
        # Mark web results
        for result in web_results:
            result['source_type'] = 'web'
        
        all_results.extend(web_results)
        
        # Get scholarly results if enabled (40% of total)  
        if self.include_scholarly:
            scholarly_results_count = max_results - len(web_results)
            scholarly_results = self.scholarly_searcher.search(query, scholarly_results_count)
            all_results.extend(scholarly_results)
        
        return all_results[:max_results]
