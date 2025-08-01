"""
Test suite for scholarly source integration - arXiv, Google Scholar, etc.
Following TDD methodology: RED-GREEN-REFACTOR
"""
import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestScholarlySourceIntegration:
    """Test cases for scholarly source search and retrieval"""
    
    def test_arxiv_search_component_exists(self):
        """Test that arXiv search component exists and can search papers"""
        print("\n🔴 RED Phase: Testing arXiv search component")
        print("Expected to FAIL - arXiv search component not implemented")
        
        from src.scholarly_sources import ArxivSearcher
        searcher = ArxivSearcher()
        
        results = searcher.search("machine learning", max_results=5)
        
        assert len(results) >= 1, f"Should find arXiv papers, got {len(results)}"
        
        # Results should have proper academic metadata
        for result in results[:2]:
            assert 'title' in result, "arXiv result should have title"
            assert 'authors' in result, "arXiv result should have authors"
            assert 'abstract' in result, "arXiv result should have abstract"
            assert 'pdf_url' in result, "arXiv result should have PDF URL"
            assert 'published' in result, "arXiv result should have publication date"
    
    def test_google_scholar_search_component_exists(self):
        """Test that Google Scholar search component exists"""
        print("\n🔴 RED Phase: Testing Google Scholar search component")
        print("Expected to FAIL - Google Scholar search component not implemented")
        
        from src.scholarly_sources import GoogleScholarSearcher
        searcher = GoogleScholarSearcher()
        
        results = searcher.search("cybersecurity education", max_results=3)
        
        assert len(results) >= 1, f"Should find scholarly papers, got {len(results)}"
        
        # Results should have scholarly metadata
        for result in results[:1]:
            assert 'title' in result, "Scholar result should have title"
            assert 'authors' in result, "Scholar result should have authors"
            assert 'source' in result, "Scholar result should have source/venue"
            assert 'citation_count' in result, "Scholar result should have citation count"
    
    def test_semantic_scholar_search_component_exists(self):
        """Test that Semantic Scholar API search component exists"""
        print("\n🔴 RED Phase: Testing Semantic Scholar search component")
        print("Expected to FAIL - Semantic Scholar search component not implemented")
        
        from src.scholarly_sources import SemanticScholarSearcher
        searcher = SemanticScholarSearcher()
        
        results = searcher.search("deep learning", max_results=3)
        
        assert len(results) >= 1, f"Should find papers via Semantic Scholar, got {len(results)}"
        
        # Results should have API-provided metadata
        for result in results[:1]:
            assert 'title' in result, "Semantic Scholar result should have title"
            assert 'authors' in result, "Semantic Scholar result should have authors"
            assert 'abstract' in result, "Semantic Scholar result should have abstract"
            assert 'year' in result, "Semantic Scholar result should have year"
            assert 'citation_count' in result, "Semantic Scholar result should have citation count"
    
    def test_unified_scholarly_search_exists(self):
        """Test that unified scholarly search aggregates all sources"""
        print("\n🔴 RED Phase: Testing unified scholarly search")
        print("Expected to FAIL - unified scholarly search not implemented")
        
        from src.scholarly_sources import UnifiedScholarlySearcher
        searcher = UnifiedScholarlySearcher()
        
        results = searcher.search("artificial intelligence ethics", max_results=10)
        
        assert len(results) >= 5, f"Should aggregate multiple scholarly sources, got {len(results)}"
        
        # Should have results from multiple sources
        sources = set(result.get('source_type', 'unknown') for result in results)
        assert len(sources) >= 2, f"Should aggregate from multiple source types, got: {sources}"
        
        # Results should be deduplicated and ranked
        titles = [result['title'] for result in results]
        assert len(set(titles)) == len(titles), "Results should be deduplicated"
    
    def test_enhanced_web_search_includes_scholarly_sources(self):
        """Test that enhanced web search integrates scholarly sources"""
        print("\n🔴 RED Phase: Testing enhanced web search with scholarly integration")
        print("Expected to FAIL - enhanced web search not implemented")
        
        from src.web_search import EnhancedWebSearcher
        searcher = EnhancedWebSearcher(include_scholarly=True)
        
        results = searcher.search("quantum computing", max_results=15)
        
        assert len(results) >= 10, f"Should find comprehensive results, got {len(results)}"
        
        # Should include both web and scholarly results
        source_types = set(result.get('source_type', 'web') for result in results)
        expected_types = {'web', 'arxiv', 'scholar', 'semantic_scholar'}
        
        assert len(source_types.intersection(expected_types)) >= 2, \
            f"Should include multiple source types, got: {source_types}"
    
    def test_pdf_download_and_processing_for_papers(self):
        """Test that system can download and process academic PDFs"""
        print("\n🔴 RED Phase: Testing PDF download and processing")
        print("Expected to FAIL - PDF processing pipeline not fully integrated")
        
        from src.scholarly_sources import PaperProcessor
        processor = PaperProcessor()
        
        # Test with a known arXiv paper
        paper_url = "https://arxiv.org/pdf/1706.03762.pdf"  # Attention is All You Need
        
        processed_paper = processor.download_and_process(paper_url)
        
        assert processed_paper is not None, "Should successfully process paper"
        assert 'text' in processed_paper, "Should extract text from PDF"
        assert 'metadata' in processed_paper, "Should extract metadata"
        assert len(processed_paper['text']) > 1000, "Should extract substantial text content"
    
    def test_citation_formatting_for_academic_sources(self):
        """Test that citation manager properly formats academic sources"""
        print("\n🔴 RED Phase: Testing academic citation formatting")
        print("Expected to FAIL - academic citation formatting not implemented")
        
        from src.citation_manager import CitationManager, CitationStyle
        from src.scholarly_sources import ArxivSearcher
        
        citation_manager = CitationManager()
        searcher = ArxivSearcher()
        
        # Get a sample arXiv paper
        papers = searcher.search("transformer neural networks", max_results=1)
        assert len(papers) >= 1, "Should find at least one paper for citation test"
        
        paper = papers[0]
        
        # Test academic citation formats
        apa_citation = citation_manager.format_academic_citation(paper, CitationStyle.APA)
        mla_citation = citation_manager.format_academic_citation(paper, CitationStyle.MLA)
        chicago_citation = citation_manager.format_academic_citation(paper, CitationStyle.CHICAGO)
        
        assert "arXiv" in apa_citation, "APA citation should include arXiv identifier"
        assert len(apa_citation) > 50, "APA citation should be substantial"
        assert len(mla_citation) > 50, "MLA citation should be substantial"
        assert len(chicago_citation) > 50, "Chicago citation should be substantial"


class TestGitHubPagesIntegration:
    """Test cases for GitHub Pages deployment readiness"""
    
    def test_static_web_interface_exists(self):
        """Test that static web interface is ready for GitHub Pages"""
        print("\n🔴 RED Phase: Testing GitHub Pages static interface")
        print("Expected to FAIL - GitHub Pages interface not implemented")
        
        from pathlib import Path
        
        # Check for GitHub Pages structure
        pages_dir = Path(__file__).parent.parent / "docs"
        assert pages_dir.exists(), "Should have docs/ directory for GitHub Pages"
        
        index_file = pages_dir / "index.html"
        assert index_file.exists(), "Should have index.html for GitHub Pages"
        
        # Check for static API endpoint simulation
        api_dir = pages_dir / "api"
        assert api_dir.exists(), "Should have api/ directory for static API simulation"
        
        config_file = pages_dir / "_config.yml"
        assert config_file.exists(), "Should have Jekyll config for GitHub Pages"
    
    def test_client_side_research_system_exists(self):
        """Test that client-side research system exists for GitHub Pages"""
        print("\n🔴 RED Phase: Testing client-side research system")
        print("Expected to FAIL - client-side system not implemented")
        
        from pathlib import Path
        
        pages_dir = Path(__file__).parent.parent / "docs"
        js_dir = pages_dir / "js"
        
        assert js_dir.exists(), "Should have js/ directory"
        
        # Check for core JavaScript files
        core_files = [
            "research-engine.js",
            "api-client.js", 
            "citation-formatter.js",
            "ui-controller.js"
        ]
        
        for file_name in core_files:
            js_file = js_dir / file_name
            assert js_file.exists(), f"Should have {file_name} for client-side functionality"
    
    def test_github_actions_workflow_exists(self):
        """Test that GitHub Actions workflow exists for automated deployment"""
        print("\n🔴 RED Phase: Testing GitHub Actions workflow")
        print("Expected to FAIL - GitHub Actions workflow not implemented")
        
        from pathlib import Path
        
        workflows_dir = Path(__file__).parent.parent / ".github" / "workflows"
        assert workflows_dir.exists(), "Should have .github/workflows directory"
        
        deploy_workflow = workflows_dir / "deploy-pages.yml"
        assert deploy_workflow.exists(), "Should have GitHub Pages deployment workflow"
        
        test_workflow = workflows_dir / "test.yml"  
        assert test_workflow.exists(), "Should have testing workflow"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
