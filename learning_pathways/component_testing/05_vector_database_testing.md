# 📚 Vector Databases and Semantic Search - Educational Module

## Welcome to Digital Library Management!

Imagine you're the head librarian of the world's most advanced digital library. Instead of organizing books by just their titles or subjects, you have a magical system that understands the *meaning* of every book and can instantly find books that are similar in concept, even if they use completely different words!

This is exactly what vector databases do in modern AI systems. They store information not just as text, but as mathematical representations called "vectors" that capture the meaning and context of the content. This enables incredibly powerful semantic search - finding information based on meaning rather than just matching keywords.

In this educational module, we'll learn how to test vector database systems, understand how semantic search works, and explore how to build reliable data storage systems that power modern AI applications.

## 🧮 What are Vector Databases?

Think of traditional databases like old library card catalogs - they organize information by exact categories and keywords. Vector databases are like having a librarian who understands the meaning and relationships between all the books, even if they're written in different languages or use different terminology.

### The Magic of Vector Embeddings

When we put text into a vector database, it first gets converted into a "vector embedding" - a list of numbers that represents the meaning of the text:

```python
# Text gets converted to vectors (simplified example)
"Dogs are loyal pets" → [0.2, 0.8, 0.1, 0.9, 0.3, ...]
"Cats are independent animals" → [0.1, 0.7, 0.2, 0.8, 0.4, ...]
"Python is a programming language" → [0.9, 0.1, 0.8, 0.2, 0.7, ...]
```

These numbers capture semantic meaning, so similar concepts will have similar numbers, even if the words are different!

### Real-World Example: Research Paper Discovery

Imagine you're researching "renewable energy solutions" for a school project. Here's how a vector database helps:

**Traditional keyword search:**
- Query: "renewable energy"
- Finds: Only documents with exactly those words
- Misses: Papers about "solar power", "wind turbines", "sustainable electricity"

**Vector database semantic search:**
- Query: "renewable energy solutions"
- Understands: Energy + sustainability + alternatives + environment
- Finds: Papers about solar, wind, hydro, geothermal, even if they never say "renewable energy"
- Also finds: Policy papers, economic analyses, technology comparisons

Amazing! The vector database understood what you were *really* looking for, not just the exact words you used.

## 🏗️ Vector Database Components

### 1. **StoredChunk: The Digital Library Card**
Every piece of information in our vector database gets stored as a "chunk" with complete metadata:

```python
@dataclass
class StoredChunk:
    """
    Like a library catalog card, but for the digital age!
    
    Contains not just the content, but everything needed to
    find, understand, and reference the information later.
    """
    id: str                    # Unique identifier (like a library call number)
    text: str                  # The actual content
    source_url: str           # Where we found this information
    metadata: Dict[str, Any]  # Extra info (title, author, date, etc.)
    embedding: np.ndarray     # The mathematical representation of meaning
    embedding_model: str      # Which AI model created the embedding
    timestamp: str           # When we stored this information

# Real example:
research_chunk = StoredChunk(
    id="renewable_001",
    text="Solar panels convert sunlight directly into electricity through photovoltaic cells, making them a clean and sustainable energy source.",
    source_url="https://energy.gov/solar-energy-basics",
    metadata={
        "title": "Solar Energy Basics",
        "author": "U.S. Department of Energy",
        "publication_date": "2025-01-15",
        "document_type": "government_resource",
        "reading_level": 8,
        "word_count": 234
    },
    embedding=np.array([0.23, 0.81, 0.45, 0.67, ...]),  # 384 numbers representing meaning
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    timestamp="2025-01-18T10:30:00Z"
)
```

### 2. **SearchResult: The Perfect Match**
When you search the vector database, you get back ranked results:

```python
@dataclass
class SearchResult:
    """
    Search results ranked by how well they match your query.
    
    Like getting back the most relevant books from a librarian
    who really understands what you're looking for.
    """
    id: str                    # Reference to the stored chunk
    text: str                  # The relevant content
    source_url: str           # Where this came from
    metadata: Dict[str, Any]  # Additional information
    score: float              # How well this matches (0.0 to 1.0)
    rank: int                 # Position in search results (1st, 2nd, 3rd...)

# Example search results for "how do solar panels work?"
search_results = [
    SearchResult(
        id="renewable_001",
        text="Solar panels convert sunlight directly into electricity through photovoltaic cells...",
        source_url="https://energy.gov/solar-energy-basics",
        metadata={"title": "Solar Energy Basics", "credibility": 0.95},
        score=0.94,  # Excellent match!
        rank=1       # Top result
    ),
    SearchResult(
        id="renewable_087", 
        text="Photovoltaic technology harnesses solar radiation to generate clean power...",
        source_url="https://nrel.gov/photovoltaic-research",
        metadata={"title": "PV Research Overview", "credibility": 0.92},
        score=0.89,  # Very good match
        rank=2       # Second result
    )
]
```

## 🧪 Testing Vector Databases: Building Reliable Digital Libraries

### Why Test Vector Database Systems?
Vector databases are complex because they involve:
- **Mathematical operations**: Vector similarity calculations
- **Large-scale data**: Thousands or millions of documents
- **Performance requirements**: Fast search even with huge datasets
- **Data persistence**: Information must survive system restarts
- **Accuracy concerns**: Search results must be relevant and ranked correctly
- **Memory management**: Efficient storage and retrieval of large vectors

Testing ensures our digital library works reliably, finds the right information quickly, and handles real-world usage patterns.

### The TDD Approach for Vector Databases

Let's learn by building comprehensive tests for a vector database system:

#### 🔴 RED Phase: Write Failing Tests First

```python
import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock

# These imports will fail initially - that's expected in TDD!
try:
    from src.vector_store import VectorStore, StoredChunk, SearchResult
    from src.embedder import EmbeddedChunk
except ImportError:
    VectorStore = None
    StoredChunk = None
    SearchResult = None
    EmbeddedChunk = None

class TestVectorDatabase:
    """
    📚 Test suite for Vector Database and Semantic Search Systems.
    
    We're testing a digital library system that understands meaning,
    not just keywords. Like testing a super-smart librarian who can
    find exactly what you need even if you don't know the right words.
    
    🎯 Learning Goals:
    - Understand how vector databases store and retrieve information
    - Learn about semantic search and similarity scoring
    - Practice testing data persistence and database operations
    - Explore batch processing and performance optimization
    - See how to test mathematical operations in real applications
    """
    
    def setup_method(self):
        """Set up a temporary database for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_library"
    
    def teardown_method(self):
        """Clean up after each test"""
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_stored_chunk_captures_complete_information(self):
        """
        📋 Test that StoredChunk holds everything needed for a digital library entry.
        
        Like a library catalog card, each stored chunk needs complete information:
        not just the content, but where it came from, when it was added,
        and mathematical representation for semantic search.
        
        💡 Complete information includes:
        - id: Unique identifier for quick reference
        - text: The actual content people will read
        - source_url: Where we found this information (for credibility)
        - metadata: Extra details (title, author, date, etc.)
        - embedding: Mathematical representation of meaning
        - embedding_model: Which AI model created the vectors
        - timestamp: When this was added to our library
        """
        assert StoredChunk is not None, "StoredChunk class should exist"
        
        # Create a comprehensive library entry
        embedding_vector = np.array([0.23, 0.81, 0.45, 0.67, 0.12, 0.89] * 64)  # 384 dimensions
        
        library_entry = StoredChunk(
            id="science_renewable_001",
            text="""Solar energy is one of the most promising renewable energy sources. 
                    Solar panels, also called photovoltaic (PV) systems, convert sunlight 
                    directly into electricity through the photovoltaic effect. Modern solar 
                    panels can achieve efficiency rates of over 20%, making them increasingly 
                    cost-effective for both residential and commercial applications.""",
            
            source_url="https://energy.gov/eere/solar/solar-energy-basics",
            
            metadata={
                "title": "Solar Energy Basics - Understanding Photovoltaic Systems",
                "author": "U.S. Department of Energy",
                "publication_date": "2025-01-15",
                "last_updated": "2025-01-18",
                "document_type": "government_educational_resource",
                "subject_categories": ["renewable energy", "solar power", "environmental science"],
                "reading_level": "grade_8",
                "word_count": 87,
                "credibility_score": 0.98,  # Very high credibility (government source)
                "language": "en",
                "geographic_focus": "united_states"
            },
            
            embedding=embedding_vector,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            timestamp="2025-01-18T14:30:00Z"
        )
        
        # Verify all information is properly stored
        assert library_entry.id == "science_renewable_001"
        assert "photovoltaic" in library_entry.text.lower()
        assert "Solar Energy Basics" in library_entry.metadata["title"]
        assert library_entry.metadata["credibility_score"] == 0.98
        assert library_entry.embedding_model.startswith("sentence-transformers")
        assert len(library_entry.embedding) == 384  # Standard embedding size
        assert library_entry.source_url.startswith("https://")

    def test_search_result_provides_ranked_relevance(self):
        """
        🔍 Test that SearchResult shows relevance ranking and scoring.
        
        When someone searches our digital library, they should get back results
        ranked by relevance, with scores showing how well each result matches
        their query. Like a librarian saying "This book is exactly what you want,
        this other book is pretty close, and this third one might be helpful."
        
        💡 Search results should include:
        - All the content information from StoredChunk
        - score: How well this matches the search (0.0 to 1.0)
        - rank: Position in the results list (1st, 2nd, 3rd...)
        - Explanation of why this result was chosen
        """
        assert SearchResult is not None, "SearchResult class should exist"
        
        # Test highly relevant result
        perfect_match = SearchResult(
            id="renewable_solar_basics_001",
            text="Solar panels convert sunlight into electricity through photovoltaic cells, providing clean renewable energy for homes and businesses.",
            source_url="https://nrel.gov/solar-basics",
            metadata={
                "title": "How Solar Panels Work",
                "relevance_factors": ["exact_topic_match", "recent_publication", "authoritative_source"],
                "search_terms_found": ["solar panels", "electricity", "renewable energy"],
                "semantic_match_strength": "excellent"
            },
            score=0.94,  # Excellent match (94% similarity)
            rank=1       # Top result
        )
        
        # Test moderately relevant result
        partial_match = SearchResult(
            id="renewable_wind_power_045",
            text="Wind turbines generate electricity from wind power, offering another sustainable energy alternative alongside solar and hydroelectric systems.",
            source_url="https://energy.gov/wind-power",
            metadata={
                "title": "Wind Power Fundamentals", 
                "relevance_factors": ["related_topic", "renewable_energy_category"],
                "search_terms_found": ["electricity", "renewable"],
                "semantic_match_strength": "moderate"
            },
            score=0.67,  # Moderate match (67% similarity)
            rank=2       # Second result
        )
        
        # Verify ranking and scoring work correctly
        assert perfect_match.score > partial_match.score, "Higher scores should rank higher"
        assert perfect_match.rank < partial_match.rank, "Lower rank numbers are better positions"
        assert 0.0 <= perfect_match.score <= 1.0, "Scores should be between 0 and 1"
        assert 0.0 <= partial_match.score <= 1.0, "Scores should be between 0 and 1"
        assert perfect_match.rank == 1, "Best match should be rank 1"
        assert partial_match.rank == 2, "Second best match should be rank 2"

    def test_vector_store_initialization(self):
        """
        🏗️ Test that VectorStore creates a proper digital library database.
        
        Like setting up a new library building, we need to make sure
        the database is properly initialized with all the systems needed
        to store, organize, and retrieve information effectively.
        
        💡 Initialization should include:
        - Database connection and setup
        - Collection/table creation for storing documents
        - Proper configuration of vector dimensions
        - Persistence directory for saving data
        - Error handling for setup problems
        """
        assert VectorStore is not None, "VectorStore class should exist"
        
        # Test basic initialization
        library = VectorStore(persist_directory=str(self.db_path))
        
        # Verify core components are set up
        assert library is not None, "Library should be created successfully"
        assert hasattr(library, 'collection_name'), "Should have a collection name"
        assert hasattr(library, 'persist_directory'), "Should track where data is stored"
        assert hasattr(library, 'collection'), "Should have database collection"
        
        # Test that collection is properly configured
        assert library.collection is not None, "Database collection should be initialized"
        assert library.collection_name == "research_documents", "Should use appropriate collection name"
        assert library.persist_directory == str(self.db_path), "Should remember storage location"
        
        # Test reinitialization with same path works
        library2 = VectorStore(persist_directory=str(self.db_path))
        assert library2.collection is not None, "Should be able to reconnect to existing database"

    def test_add_single_document_to_library(self):
        """
        📖 Test adding a single document to our digital library.
        
        Like a librarian cataloging a new book, we need to test that
        documents are properly processed, stored with all metadata,
        and made searchable in the database.
        
        💡 Adding a document involves:
        - Converting text to vector embeddings
        - Storing content with complete metadata
        - Assigning unique identifiers
        - Making it searchable immediately
        - Tracking library size changes
        """
        library = VectorStore(persist_directory=str(self.db_path))
        
        # Create a sample research document
        embedding_vector = np.random.rand(384)  # Typical embedding size
        
        research_document = EmbeddedChunk(
            text="Artificial intelligence is transforming education by providing personalized learning experiences, automated grading, and intelligent tutoring systems that adapt to individual student needs.",
            source_url="https://education.ai/personalized-learning",
            chunk_id="edu_ai_001",
            metadata={
                "title": "AI in Education: Personalized Learning",
                "author": "Dr. Sarah Chen",
                "publication_date": "2025-01-10",
                "subject": "educational_technology",
                "reading_level": "college",
                "word_count": 28
            },
            start_char=0,
            end_char=156,
            embedding=embedding_vector,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Library should start empty
        initial_size = library.get_collection_size()
        assert initial_size == 0, "New library should be empty"
        
        # Add the document
        success = library.add_chunk(research_document)
        
        # Verify document was added successfully
        assert success is True, "Document addition should succeed"
        new_size = library.get_collection_size()
        assert new_size == 1, "Library should contain exactly one document"
        assert new_size > initial_size, "Library size should increase"

    def test_batch_add_multiple_documents(self):
        """
        📚 Test adding multiple documents at once (batch processing).
        
        Real libraries receive many books at once and need efficient
        systems to catalog them all. Similarly, research systems often
        need to process hundreds or thousands of documents together.
        
        💡 Batch processing should:
        - Handle multiple documents efficiently
        - Maintain data integrity for all documents
        - Provide feedback on success/failure for each document
        - Be faster than adding documents one by one
        - Handle partial failures gracefully
        """
        library = VectorStore(persist_directory=str(self.db_path))
        
        # Create a collection of educational documents
        education_topics = [
            ("AI in Healthcare", "Machine learning algorithms are revolutionizing medical diagnosis and treatment planning."),
            ("Renewable Energy Future", "Solar and wind technologies are becoming the dominant sources of electricity worldwide."), 
            ("Climate Change Solutions", "Carbon capture technology and reforestation efforts show promise for reducing atmospheric CO2."),
            ("Space Exploration Progress", "Recent Mars missions have provided unprecedented data about planetary geology and potential for life."),
            ("Quantum Computing Advances", "Quantum processors are approaching the point where they can outperform classical computers.")
        ]
        
        document_batch = []
        for i, (title, content) in enumerate(education_topics):
            # Create unique but predictable embeddings for testing
            embedding = np.array([hash(content) % 1000 / 1000.0] * 384)
            
            document = EmbeddedChunk(
                text=content,
                source_url=f"https://research.edu/topic-{i+1}",
                chunk_id=f"research_doc_{i+1:03d}",
                metadata={
                    "title": title,
                    "topic_id": i+1,
                    "batch_number": 1,
                    "processing_date": "2025-01-18"
                },
                start_char=0,
                end_char=len(content),
                embedding=embedding,
                embedding_model="test-model-v1"
            )
            document_batch.append(document)
        
        # Library should start empty
        assert library.get_collection_size() == 0, "Library should start empty"
        
        # Add all documents at once
        results = library.add_chunks(document_batch)
        
        # Verify batch processing worked correctly
        assert results is True or isinstance(results, list), "Should return success indicator or detailed results"
        final_size = library.get_collection_size()
        assert final_size == 5, "Library should contain all 5 documents"
        
        # Verify each document type is represented
        assert final_size == len(education_topics), "Should have same number as input documents"

    def test_semantic_search_finds_meaning_not_keywords(self):
        """
        🔍 Test that semantic search finds relevant content based on meaning.
        
        This is the magical part of vector databases! Unlike traditional
        keyword search that only finds exact word matches, semantic search
        understands meaning and finds relevant content even when different
        words are used.
        
        💡 Semantic search should:
        - Find relevant content even with different vocabulary
        - Rank results by semantic similarity
        - Handle synonyms and related concepts
        - Work across different writing styles
        - Provide confidence scores for matches
        """
        library = VectorStore(persist_directory=str(self.db_path))
        
        # Add a diverse knowledge base about learning and education
        knowledge_base = [
            # Document 1: Formal academic language
            ("Pedagogical approaches in modern educational systems emphasize student-centered learning methodologies and differentiated instruction techniques.", "academic_pedagogy"),
            
            # Document 2: Casual explanation of same concepts  
            ("Good teaching means focusing on what each student needs and using different ways to help them learn based on how they learn best.", "practical_teaching"),
            
            # Document 3: Technology focus
            ("Educational technology platforms provide adaptive learning algorithms that personalize content delivery based on individual learner progress.", "edtech_systems"),
            
            # Document 4: Completely different topic
            ("Quantum mechanics describes the behavior of matter and energy at the atomic and subatomic level through wave functions and probability distributions.", "quantum_physics"),
            
            # Document 5: Related but different educational concept
            ("Assessment strategies should measure not just what students know, but how they apply knowledge to solve real-world problems.", "assessment_methods")
        ]
        
        # Add documents to library
        documents = []
        for i, (text, topic) in enumerate(knowledge_base):
            # Create meaningful embeddings (in real system, these would come from AI models)
            # For testing, we simulate embeddings that group similar concepts
            if "teaching" in topic or "pedagogy" in topic or "edtech" in topic:
                # Education-related documents get similar embeddings
                base_vector = [0.8, 0.7, 0.9, 0.6, 0.8]
            elif "assessment" in topic:
                # Assessment gets somewhat similar to education
                base_vector = [0.7, 0.6, 0.8, 0.5, 0.7]
            else:
                # Quantum physics gets very different embedding
                base_vector = [0.2, 0.1, 0.3, 0.9, 0.2]
            
            # Extend to 384 dimensions
            embedding = np.array(base_vector * 77)  # 77 * 5 = 385, take first 384
            embedding = embedding[:384]
            
            document = EmbeddedChunk(
                text=text,
                source_url=f"https://knowledge.edu/doc-{i+1}",
                chunk_id=f"knowledge_{i+1:03d}",
                metadata={"topic": topic, "doc_index": i+1},
                start_char=0,
                end_char=len(text),
                embedding=embedding,
                embedding_model="semantic-test-model"
            )
            documents.append(document)
        
        library.add_chunks(documents)
        
        # Test semantic search with education-related query
        # This should find education documents even though query uses different words
        search_query = "How can teachers help students learn more effectively?"
        results = library.search_by_text(search_query, top_k=3)
        
        # Verify semantic search results
        assert len(results) > 0, "Should find relevant results"
        assert len(results) <= 3, "Should respect top_k limit"
        assert all(isinstance(r, SearchResult) for r in results), "Results should be SearchResult objects"
        
        # Results should be ranked by relevance (highest scores first)
        for i in range(len(results) - 1):
            assert results[i].score >= results[i+1].score, "Results should be ranked by score"
        
        # Top results should be education-related, not quantum physics
        top_result = results[0]
        assert "quantum" not in top_result.text.lower(), "Should not match unrelated physics content"
        assert any(word in top_result.text.lower() for word in ["teaching", "learning", "student", "education"]), "Should find education-related content"

    def test_vector_similarity_search_with_exact_vectors(self):
        """
        🧮 Test vector-based similarity search with mathematical precision.
        
        This tests the core mathematical operations that power semantic search.
        By searching with specific vectors, we can verify that the similarity
        calculations work correctly and return appropriately ranked results.
        
        💡 Vector similarity should:
        - Find exact matches with highest scores
        - Rank similar vectors by mathematical similarity
        - Handle different vector distances correctly
        - Provide consistent scoring across searches
        - Work with various vector dimensions
        """
        library = VectorStore(persist_directory=str(self.db_path))
        
        # Create vectors with known mathematical relationships
        base_vector = np.array([1.0, 0.0, 0.0, 1.0, 0.5] * 77)[:384]  # Base pattern
        similar_vector = np.array([0.9, 0.1, 0.1, 0.9, 0.4] * 77)[:384]  # Very similar
        different_vector = np.array([0.1, 0.9, 0.8, 0.2, 0.9] * 77)[:384]  # Quite different
        
        test_vectors = [base_vector, similar_vector, different_vector]
        
        # Add documents with these specific vectors
        for i, vector in enumerate(test_vectors):
            document = EmbeddedChunk(
                text=f"Test document {i+1} with vector pattern {i+1}",
                source_url=f"https://test.example/vector-{i+1}",
                chunk_id=f"vector_test_{i+1:03d}",
                metadata={"vector_type": f"pattern_{i+1}"},
                start_char=0,
                end_char=30,
                embedding=vector,
                embedding_model="mathematical-test-model"
            )
            library.add_chunk(document)
        
        # Search using the base vector - should find exact match first
        search_results = library.search_by_vector(base_vector, top_k=3)
        
        # Verify mathematical similarity ranking
        assert len(search_results) == 3, "Should return all documents"
        
        # First result should be exact match (or very close)
        exact_match = search_results[0]
        assert exact_match.score > 0.95, "Exact match should have very high score"
        assert "vector_test_001" in exact_match.id, "Should find the exact vector match first"
        
        # Results should be in descending order of similarity
        assert search_results[0].score >= search_results[1].score, "First result should be best match"
        assert search_results[1].score >= search_results[2].score, "Second result should be better than third"
        
        # Different vector should have lowest score
        different_match = search_results[2]
        assert different_match.score < exact_match.score, "Different vector should have lower similarity"

    def test_document_deletion_and_library_management(self):
        """
        🗑️ Test removing documents from the digital library.
        
        Libraries need to remove outdated books, and digital libraries
        need to remove outdated or incorrect information. This tests
        that documents can be safely deleted without affecting other
        documents or corrupting the database.
        
        💡 Document deletion should:
        - Remove specific documents by ID
        - Update library size correctly
        - Not affect other documents
        - Handle attempts to delete non-existent documents
        - Allow bulk deletion by source or criteria
        """
        library = VectorStore(persist_directory=str(self.db_path))
        
        # Add several test documents
        test_documents = []
        for i in range(5):
            embedding = np.random.rand(384)
            document = EmbeddedChunk(
                text=f"Test document number {i+1} with unique content about topic {i+1}.",
                source_url=f"https://test.source/doc-{i+1}",
                chunk_id=f"delete_test_{i+1:03d}",
                metadata={"doc_number": i+1, "test_batch": "deletion_test"},
                start_char=0,
                end_char=50,
                embedding=embedding,
                embedding_model="deletion-test-model"
            )
            test_documents.append(document)
        
        library.add_chunks(test_documents)
        assert library.get_collection_size() == 5, "Should have 5 documents initially"
        
        # Test single document deletion
        deletion_result = library.delete_chunk("delete_test_003")
        
        assert deletion_result is True, "Deletion should succeed"
        assert library.get_collection_size() == 4, "Should have 4 documents after deletion"
        
        # Verify the correct document was deleted
        remaining_results = library.search_by_text("Test document number 3", top_k=5)
        assert not any("delete_test_003" in result.id for result in remaining_results), "Deleted document should not be found"
        
        # Verify other documents are still there
        other_results = library.search_by_text("Test document number 1", top_k=5)
        assert any("delete_test_001" in result.id for result in other_results), "Other documents should remain"
        
        # Test deletion of non-existent document
        fake_deletion = library.delete_chunk("nonexistent_document")
        assert fake_deletion is False, "Deleting non-existent document should return False"
        assert library.get_collection_size() == 4, "Size should not change for failed deletion"

    def test_bulk_deletion_by_source(self):
        """
        🏢 Test removing all documents from a specific source.
        
        Sometimes we need to remove all content from a particular website
        or source that's no longer reliable. This tests bulk deletion
        operations that can remove multiple related documents at once.
        
        💡 Bulk deletion should:
        - Remove all documents matching criteria
        - Be more efficient than individual deletions  
        - Provide feedback on how many documents were removed
        - Handle cases where no documents match criteria
        - Maintain database integrity during bulk operations
        """
        library = VectorStore(persist_directory=str(self.db_path))
        
        # Add documents from different sources
        sources = [
            "https://reliable.edu/research",
            "https://reliable.edu/studies", 
            "https://questionable.blog/posts",
            "https://questionable.blog/articles",
            "https://trustworthy.gov/reports"
        ]
        
        documents = []
        for i, source in enumerate(sources):
            embedding = np.random.rand(384)
            document = EmbeddedChunk(
                text=f"Content from source {i+1}: This is document {i+1} with information from {source}.",
                source_url=source,
                chunk_id=f"source_test_{i+1:03d}",
                metadata={"source_index": i+1, "domain": source.split('/')[2]},
                start_char=0,
                end_char=60,
                embedding=embedding,
                embedding_model="source-test-model"
            )
            documents.append(document)
        
        library.add_chunks(documents)
        assert library.get_collection_size() == 5, "Should have 5 documents from different sources"
        
        # Remove all documents from questionable.blog domain
        deleted_count = library.delete_by_source_pattern("questionable.blog")
        
        assert deleted_count == 2, "Should delete 2 documents from questionable.blog"
        assert library.get_collection_size() == 3, "Should have 3 documents remaining"
        
        # Verify questionable.blog documents are gone
        remaining_results = library.search_by_text("questionable", top_k=5)
        assert len(remaining_results) == 0, "Should not find any questionable.blog content"
        
        # Verify other sources remain
        reliable_results = library.search_by_text("reliable.edu", top_k=5)
        assert len(reliable_results) >= 1, "Should still find reliable.edu content"

    def test_database_persistence_across_sessions(self):
        """
        💾 Test that data persists when database is closed and reopened.
        
        Real databases must save information permanently, not just in memory.
        This tests that documents added to our vector library are still
        there when we restart the system, like books staying on library
        shelves even when the library closes and reopens.
        
        💡 Persistence should:
        - Save all documents to permanent storage
        - Preserve embeddings and metadata
        - Allow reconnection to existing database
        - Maintain search functionality after restart
        - Handle database files correctly
        """
        # Create library and add documents
        library1 = VectorStore(persist_directory=str(self.db_path))
        
        persistent_document = EmbeddedChunk(
            text="This document should survive database restarts and remain searchable across sessions.",
            source_url="https://persistence.test/document",
            chunk_id="persistence_test_001",
            metadata={"test_type": "persistence", "creation_session": 1},
            start_char=0,
            end_char=89,
            embedding=np.random.rand(384),
            embedding_model="persistence-test-model"
        )
        
        library1.add_chunk(persistent_document)
        assert library1.get_collection_size() == 1, "Document should be added in first session"
        
        # Verify document is searchable in first session
        session1_results = library1.search_by_text("survive database restarts", top_k=1)
        assert len(session1_results) == 1, "Should find document in first session"
        assert "persistence_test_001" in session1_results[0].id, "Should find correct document"
        
        # Close first session (simulate database shutdown)
        del library1
        
        # Create new library instance with same persist directory (simulate restart)
        library2 = VectorStore(persist_directory=str(self.db_path))
        
        # Verify document survived the restart
        assert library2.get_collection_size() == 1, "Document should survive restart"
        
        # Verify document is still searchable after restart
        session2_results = library2.search_by_text("survive database restarts", top_k=1)
        assert len(session2_results) == 1, "Should find document after restart"
        assert "persistence_test_001" in session2_results[0].id, "Should find same document after restart"
        assert session2_results[0].text == persistent_document.text, "Text should be identical after restart"

    def test_large_scale_performance_and_memory_management(self):
        """
        ⚡ Test performance with larger datasets and memory efficiency.
        
        Real-world vector databases need to handle thousands or millions
        of documents efficiently. This tests that our system can handle
        larger datasets without running out of memory or becoming too slow.
        
        💡 Performance testing should verify:
        - Reasonable speed with larger document collections
        - Memory usage doesn't grow unbounded
        - Search performance remains acceptable at scale
        - Batch operations are more efficient than individual operations
        - Database remains responsive under load
        """
        library = VectorStore(persist_directory=str(self.db_path))
        
        # Test with moderately large dataset (100 documents)
        large_batch = []
        for i in range(100):
            # Create varied content to test realistic scenarios
            topics = ["science", "technology", "education", "environment", "health"]
            topic = topics[i % len(topics)]
            
            text = f"Document {i+1} about {topic}: This is detailed content for document {i+1} covering various aspects of {topic} research and applications in modern society."
            
            # Create diverse but predictable embeddings
            embedding = np.array([hash(text + str(i)) % 1000 / 1000.0] * 384)
            
            document = EmbeddedChunk(
                text=text,
                source_url=f"https://largescale.test/doc-{i+1:04d}",
                chunk_id=f"scale_test_{i+1:04d}",
                metadata={"doc_index": i+1, "topic": topic, "batch": "performance_test"},
                start_char=0,
                end_char=len(text),
                embedding=embedding,
                embedding_model="performance-test-model"
            )
            large_batch.append(document)
        
        # Time the batch addition
        import time
        start_time = time.time()
        library.add_chunks(large_batch)
        add_time = time.time() - start_time
        
        # Verify all documents were added
        final_size = library.get_collection_size()
        assert final_size == 100, "Should have all 100 documents"
        
        # Test search performance with larger dataset
        start_time = time.time()
        search_results = library.search_by_text("science research applications", top_k=10)
        search_time = time.time() - start_time
        
        # Verify search results are reasonable
        assert len(search_results) <= 10, "Should respect top_k limit"
        assert len(search_results) > 0, "Should find relevant results"
        
        # Performance should be reasonable (adjust thresholds based on system)
        assert add_time < 30, f"Batch addition should complete in reasonable time (took {add_time:.2f}s)"
        assert search_time < 5, f"Search should complete quickly (took {search_time:.2f}s)"
        
        # Test that search quality is maintained at scale
        science_results = library.search_by_text("science", top_k=5)
        assert any("science" in result.text.lower() for result in science_results), "Should find science-related content"

    def test_error_handling_and_edge_cases(self):
        """
        🚨 Test error handling and unusual situations.
        
        Real systems need to handle problems gracefully: corrupted data,
        invalid inputs, network issues, disk full errors, etc. This tests
        that our vector database handles edge cases without crashing.
        
        💡 Error handling should cover:
        - Invalid embeddings (wrong dimensions, NaN values)
        - Duplicate document IDs  
        - Empty or malformed text content
        - Database connection issues
        - Disk space or permission problems
        - Search with invalid parameters
        """
        library = VectorStore(persist_directory=str(self.db_path))
        
        # Test invalid embedding dimensions
        with pytest.raises((ValueError, AssertionError)) as exc_info:
            invalid_document = EmbeddedChunk(
                text="Document with wrong embedding size",
                source_url="https://test.invalid/wrong-size",
                chunk_id="invalid_embedding_001",
                metadata={"error_test": "wrong_dimensions"},
                start_char=0,
                end_char=35,
                embedding=np.array([0.1, 0.2, 0.3]),  # Too small! Should be 384
                embedding_model="error-test-model"
            )
            library.add_chunk(invalid_document)
        
        assert "embedding" in str(exc_info.value).lower() or "dimension" in str(exc_info.value).lower()
        
        # Test NaN values in embeddings
        nan_embedding = np.full(384, np.nan)
        with pytest.raises((ValueError, AssertionError)):
            nan_document = EmbeddedChunk(
                text="Document with NaN embedding values",
                source_url="https://test.invalid/nan-values",
                chunk_id="nan_embedding_001", 
                metadata={"error_test": "nan_values"},
                start_char=0,
                end_char=32,
                embedding=nan_embedding,
                embedding_model="error-test-model"
            )
            library.add_chunk(nan_document)
        
        # Test empty text content (should handle gracefully)
        empty_document = EmbeddedChunk(
            text="",  # Empty text
            source_url="https://test.edge/empty-text",
            chunk_id="empty_text_001",
            metadata={"error_test": "empty_content"},
            start_char=0,
            end_char=0,
            embedding=np.random.rand(384),
            embedding_model="error-test-model"
        )
        
        # Should either handle gracefully or raise informative error
        try:
            result = library.add_chunk(empty_document)
            # If it succeeds, verify it's handled properly
            if result:
                assert library.get_collection_size() >= 0, "Collection size should remain valid"
        except ValueError as e:
            # If it raises error, should be informative
            assert "text" in str(e).lower() or "empty" in str(e).lower()
        
        # Test search with invalid parameters
        with pytest.raises((ValueError, TypeError)):
            library.search_by_vector("invalid_vector_type", top_k=5)  # String instead of array
        
        with pytest.raises((ValueError, TypeError)):
            library.search_by_text("valid query", top_k=-1)  # Negative top_k
```

#### 🟢 GREEN Phase: Implement to Pass Tests

After writing comprehensive tests, we'd implement the vector database system:

```python
import numpy as np
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import hashlib
import time
from pathlib import Path

@dataclass
class StoredChunk:
    """Complete information for a document chunk stored in vector database"""
    id: str
    text: str
    source_url: str
    metadata: Dict[str, Any]
    embedding: np.ndarray
    embedding_model: str
    timestamp: str

@dataclass
class SearchResult:
    """Search result with relevance ranking and metadata"""
    id: str
    text: str
    source_url: str
    metadata: Dict[str, Any]
    score: float
    rank: int

class VectorStore:
    """Educational vector database for semantic search and document storage"""
    
    def __init__(self, persist_directory: str, collection_name: str = "research_documents"):
        """Initialize vector database with persistent storage"""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
    
    def add_chunk(self, chunk: 'EmbeddedChunk') -> bool:
        """Add a single document chunk to the vector database"""
        try:
            # Validate embedding dimensions
            if len(chunk.embedding) != 384:
                raise ValueError(f"Expected 384-dimensional embedding, got {len(chunk.embedding)}")
            
            # Check for NaN values
            if np.isnan(chunk.embedding).any():
                raise ValueError("Embedding contains NaN values")
            
            # Prepare data for ChromaDB
            self.collection.add(
                embeddings=[chunk.embedding.tolist()],
                documents=[chunk.text],
                metadatas=[{
                    "source_url": chunk.source_url,
                    "embedding_model": chunk.embedding_model,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    **chunk.metadata
                }],
                ids=[chunk.chunk_id]
            )
            
            return True
            
        except Exception as e:
            print(f"Error adding chunk {chunk.chunk_id}: {str(e)}")
            return False
    
    def add_chunks(self, chunks: List['EmbeddedChunk']) -> bool:
        """Add multiple document chunks efficiently"""
        try:
            embeddings = [chunk.embedding.tolist() for chunk in chunks]
            documents = [chunk.text for chunk in chunks]
            metadatas = []
            ids = [chunk.chunk_id for chunk in chunks]
            
            for chunk in chunks:
                metadata = {
                    "source_url": chunk.source_url,
                    "embedding_model": chunk.embedding_model,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    **chunk.metadata
                }
                metadatas.append(metadata)
            
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
            
        except Exception as e:
            print(f"Error adding batch of chunks: {str(e)}")
            return False
    
    def search_by_vector(self, query_vector: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        """Search for similar documents using vector similarity"""
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        
        if not isinstance(query_vector, np.ndarray):
            raise TypeError("query_vector must be numpy array")
        
        results = self.collection.query(
            query_embeddings=[query_vector.tolist()],
            n_results=top_k
        )
        
        return self._format_search_results(results)
    
    def search_by_text(self, query_text: str, top_k: int = 5) -> List[SearchResult]:
        """Search for similar documents using text query"""
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        
        # In real implementation, this would use an embedder to convert text to vector
        # For testing, we'll simulate this with a simple hash-based embedding
        query_embedding = np.array([hash(query_text + str(i)) % 1000 / 1000.0 for i in range(384)])
        
        return self.search_by_vector(query_embedding, top_k)
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a specific document chunk"""
        try:
            self.collection.delete(ids=[chunk_id])
            return True
        except Exception:
            return False
    
    def delete_by_source_pattern(self, source_pattern: str) -> int:
        """Delete all chunks matching source pattern"""
        # Get all documents
        all_results = self.collection.get()
        
        # Find matching IDs
        matching_ids = []
        for i, metadata in enumerate(all_results['metadatas']):
            if source_pattern in metadata.get('source_url', ''):
                matching_ids.append(all_results['ids'][i])
        
        # Delete matching documents
        if matching_ids:
            self.collection.delete(ids=matching_ids)
        
        return len(matching_ids)
    
    def get_collection_size(self) -> int:
        """Get the total number of documents in the collection"""
        return self.collection.count()
    
    def _format_search_results(self, raw_results: Dict) -> List[SearchResult]:
        """Convert ChromaDB results to SearchResult objects"""
        results = []
        
        if not raw_results['ids'] or not raw_results['ids'][0]:
            return results
        
        for rank, (doc_id, doc_text, metadata, distance) in enumerate(zip(
            raw_results['ids'][0],
            raw_results['documents'][0],
            raw_results['metadatas'][0],
            raw_results['distances'][0]
        )):
            # Convert distance to similarity score (cosine distance -> cosine similarity)
            score = 1.0 - distance
            
            result = SearchResult(
                id=doc_id,
                text=doc_text,
                source_url=metadata.get('source_url', ''),
                metadata=metadata,
                score=max(0.0, min(1.0, score)),  # Clamp between 0 and 1
                rank=rank + 1
            )
            results.append(result)
        
        return results
```

## 🎯 Key Testing Concepts You Learned

### 1. **Vector Database Fundamentals**
- Understanding how text converts to mathematical vectors
- Testing vector similarity calculations and rankings
- Managing high-dimensional data efficiently

### 2. **Database Operations Testing**
- CRUD operations (Create, Read, Update, Delete)
- Batch processing for efficiency
- Data persistence across sessions
- Transaction integrity and error recovery

### 3. **Semantic Search Validation**
- Testing meaning-based search vs keyword matching
- Verifying relevance ranking algorithms
- Measuring search quality and accuracy

### 4. **Performance and Scale Testing**
- Testing with realistic dataset sizes
- Memory usage and efficiency validation
- Search speed and responsiveness verification

### 5. **Error Handling and Edge Cases**
- Invalid data format handling
- Database connection error management
- Graceful degradation when operations fail

## 🚀 Practice Challenges

### Challenge 1: Multi-Language Vector Store
Write tests for a vector database that handles documents in multiple languages while maintaining semantic search accuracy.

### Challenge 2: Real-Time Updates
Write tests for a system that updates vector embeddings when source documents change, ensuring search results stay current.

### Challenge 3: Federated Search
Write tests for searching across multiple vector databases simultaneously and merging results by relevance.

### Challenge 4: Vector Analytics
Write tests for analyzing vector database contents: most common topics, content gaps, quality metrics.

## 📚 Real-World Applications

Vector databases power many modern applications:
- **Search Engines** (Google, Bing - understanding query intent)
- **Recommendation Systems** (Netflix, Spotify - finding similar content)
- **AI Assistants** (ChatGPT, Claude - retrieving relevant knowledge)
- **E-commerce** (Amazon - product similarity and recommendations)
- **Academic Research** (Google Scholar - finding related papers)
- **Legal Systems** (case law similarity and precedent finding)
- **Medical Diagnosis** (symptom pattern matching)
- **Social Media** (content recommendation and moderation)

## 💡 Key Takeaways

1. **Vector databases store meaning, not just text** - They understand concepts and relationships
2. **Semantic search is more powerful than keyword search** - Finds relevant content even with different words
3. **Mathematical similarity drives search results** - Vector distances determine relevance rankings
4. **Performance testing is crucial at scale** - Real systems handle millions of documents
5. **Data persistence requires careful testing** - Information must survive system restarts
6. **Error handling prevents system failures** - Invalid data shouldn't crash the database
7. **Batch operations improve efficiency** - Processing multiple documents together is faster
8. **Testing embeddings requires understanding the math** - Vector similarity calculations must be verified

Remember: **Vector databases are like having a librarian who understands the meaning of every book and can instantly find exactly what you're looking for, even if you don't know the right words to describe it!** 📚🔍✨
