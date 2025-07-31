"""
Enhanced Arbitrary Query Research System - Web-Based Multi-Source Research
Handles any research query with dynamic web search and content retrieval
"""
import asyncio
import json
import sys
import tempfile
from pathlib import Path
import logging
import time
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import all required components
from web_search import WebSearcher
from content_loaders import MultiSourceContentLoader
from document_parser import DocumentParser
from embedder import Embedder
from vector_store import VectorStore

class ArbitraryQueryResearcher:
    """Research system that can handle any query dynamically using web search"""
    
    def __init__(self, max_sources: int = 10):
        self.max_sources = max_sources
        self.web_searcher = WebSearcher()
        self.content_loader = MultiSourceContentLoader()
        self.document_parser = DocumentParser()
        self.embedder = Embedder()
        
        # Create temporary directory for vector store
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.vector_store = VectorStore(self.temp_dir)
        
    def generate_search_queries(self, query: str) -> List[str]:
        """Generate multiple search query variations for comprehensive research"""
        base_query = query.strip()
        
        # For AP Cyber specifically, be more specific to avoid AP News
        if 'ap cyber' in base_query.lower():
            search_queries = [
                "Advanced Placement cybersecurity curriculum",
                "AP Computer Science Principles cybersecurity units",
                "high school cybersecurity course AP exam",
                "College Board cybersecurity curriculum",
                "AP CSP cyber security lesson plans",
                "cybersecurity education high school curriculum"
            ]
        else:
            # Generate search variations for other queries
            search_queries = [
                base_query,
                f"{base_query} explained",
                f"{base_query} guide tutorial",
                f"{base_query} overview summary",
                f"what is {base_query}",
                f"{base_query} curriculum course"
            ]
        
        return search_queries[:6]  # Limit to 6 variations
    
    def search_web_sources(self, query: str) -> List[Dict]:
        """Search the web for relevant sources"""
        print(f"🌐 Searching web sources for: '{query}'")
        
        # Generate search query variations
        search_queries = self.generate_search_queries(query)
        
        all_sources = []
        for search_query in search_queries:
            try:
                results = self.web_searcher.search(search_query, max_results=3)
                all_sources.extend(results)
                time.sleep(1)  # Be polite to search engine
            except Exception as e:
                print(f"❌ Search failed for '{search_query}': {e}")
                continue
        
        # Remove duplicates and limit results  
        seen_urls = set()
        unique_sources = []
        for source in all_sources:
            url = source.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)
        
        return unique_sources[:self.max_sources]
    
    def load_and_process_sources(self, sources: List[Dict]) -> List[Dict]:
        """Load content from web sources and process into documents"""
        print(f"📄 Loading content from {len(sources)} web sources...")
        
        # Extract URLs from search results
        urls = [source['url'] for source in sources if source.get('url')]
        
        # Load content from URLs
        documents = self.content_loader.load_multiple_urls(urls)
        
        # Parse and chunk the documents
        processed_docs = []
        for doc in documents:
            try:
                # Parse the document (mainly for chunking)
                parsed_doc = self.document_parser.parse_text(doc['text'], doc['source'])
                
                # Extract chunks from parsed document
                if hasattr(parsed_doc, 'chunks'):
                    chunks = parsed_doc.chunks
                elif isinstance(parsed_doc, dict) and 'chunks' in parsed_doc:
                    chunks = parsed_doc['chunks']
                else:
                    # Fallback: create simple chunks
                    text = doc['text']
                    chunk_size = 1000
                    chunks = []
                    for i in range(0, len(text), chunk_size):
                        chunk_text = text[i:i+chunk_size]
                        chunks.append({
                            'content': chunk_text,
                            'source': doc['source'],
                            'chunk_id': f"chunk_{i//chunk_size}"
                        })
                
                processed_doc = {
                    'title': doc['title'],
                    'source': doc['source'],
                    'type': doc['type'],
                    'chunks': chunks,
                    'metadata': {
                        'length': doc['length'],
                        'chunk_count': len(chunks)
                    }
                }
                processed_docs.append(processed_doc)
                
            except Exception as e:
                print(f"❌ Failed to process document from {doc['source']}: {e}")
                continue
        
        return processed_docs
    
    def index_documents(self, documents: List[Dict]) -> Dict:
        """Index documents in vector store for semantic search"""
        print(f"🔍 Indexing {len(documents)} documents...")
        
        all_chunks = []
        for doc in documents:
            for chunk in doc['chunks']:
                chunk_with_source = {**chunk, 'source_title': doc['title']}
                all_chunks.append(chunk_with_source)
        
        if not all_chunks:
            return {'chunks_indexed': 0, 'documents_processed': 0}
        
        # Generate embeddings for chunks
        embeddings = []
        for chunk in all_chunks:
            try:
                embedding = self.embedder.get_embedding(chunk['content'])
                embeddings.append(embedding)
            except Exception as e:
                print(f"❌ Failed to generate embedding: {e}")
                embeddings.append(None)
        
        # Store in vector database
        valid_chunks = []
        valid_embeddings = []
        for chunk, embedding in zip(all_chunks, embeddings):
            if embedding is not None:
                valid_chunks.append(chunk)
                valid_embeddings.append(embedding)
        
        if valid_chunks:
            self.vector_store.store_documents(valid_chunks, valid_embeddings)
        
        return {
            'chunks_indexed': len(valid_chunks),
            'documents_processed': len(documents)
        }
    
    def retrieve_relevant_content(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve most relevant content chunks for the query"""
        print(f"🎯 Retrieving relevant content for: '{query}'")
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.get_embedding(query)
            
            # Search vector store
            results = self.vector_store.search(query_embedding, top_k=top_k)
            
            return results
            
        except Exception as e:
            print(f"❌ Content retrieval failed: {e}")
            return []
    
    def calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score between query and content"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0.0
        
        # Simple word overlap scoring
        overlap = len(query_words.intersection(content_words))
        relevance = overlap / len(query_words)
        
        return min(relevance, 1.0)
    
    def generate_answer(self, query: str, relevant_content: List[Dict]) -> str:
        """Generate comprehensive answer from relevant content"""
        if not relevant_content:
            return f"No relevant information found for query: '{query}'"
        
        # Compile information from relevant chunks
        info_parts = []
        sources_used = set()
        
        for item in relevant_content:
            content = item.get('content', '')
            source = item.get('source', 'Unknown')
            source_title = item.get('source_title', 'Unknown Document')
            
            if content and len(content) > 50:  # Only include substantial content
                info_parts.append(f"From {source_title}: {content}")
                sources_used.add(f"{source_title} ({source})")
        
        if not info_parts:
            return f"Insufficient relevant content found for query: '{query}'"
        
        # Compile answer
        answer_parts = [
            f"Research findings for '{query}':\n",
            "\n".join(info_parts[:5]),  # Limit to top 5 pieces of content
            f"\n\nThis information was compiled from {len(sources_used)} web sources."
        ]
        
        return "\n".join(answer_parts)
    
    def research_query(self, query: str) -> Dict[str, Any]:
        """Main research method - handles any arbitrary query"""
        print(f"🔬 Starting research for query: '{query}'")
        start_time = time.time()
        
        try:
            # Step 1: Search web for relevant sources
            web_sources = self.search_web_sources(query)
            if not web_sources:
                return {
                    'success': False,
                    'error': 'No web sources found',
                    'query': query
                }
            
            # Step 2: Load and process content from sources
            documents = self.load_and_process_sources(web_sources)
            if not documents:
                return {
                    'success': False,
                    'error': 'No content loaded from sources',
                    'query': query,
                    'sources_found': len(web_sources)
                }
            
            # Step 3: Index documents for semantic search
            index_stats = self.index_documents(documents)
            
            # Step 4: Retrieve relevant content
            relevant_content = self.retrieve_relevant_content(query)
            
            # Step 5: Generate comprehensive answer
            answer = self.generate_answer(query, relevant_content)
            
            # Compile sources information
            sources = []
            for doc in documents:
                sources.append({
                    'title': doc['title'],
                    'url': doc['source'],
                    'type': doc['type'],
                    'chunks': len(doc['chunks'])
                })
            
            end_time = time.time()
            
            result = {
                'success': True,
                'query': query,
                'answer': answer,
                'sources': sources,
                'statistics': {
                    'search_queries_generated': len(self.generate_search_queries(query)),
                    'web_sources_found': len(web_sources),
                    'documents_processed': index_stats['documents_processed'],
                    'chunks_indexed': index_stats['chunks_indexed'],
                    'relevant_results': len(relevant_content),
                    'processing_time': round(end_time - start_time, 2)
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'query': query
            }

# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_query_research.py '<query>'")
        sys.exit(1)
    
    query = sys.argv[1]
    researcher = ArbitraryQueryResearcher()
    
    print(f"🧠 AI Deep Research MCP - Enhanced Query Research")
    print(f"🔍 Query: {query}")
    print("=" * 60)
    
    result = researcher.research_query(query)
    
    # Output result as JSON for web interface
    print("RESULT_START")
    print(json.dumps(result, indent=2))
    print("RESULT_END")
