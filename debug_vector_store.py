#!/usr/bin/env python3
"""
Debug script to isolate VectorStore hanging issue
"""

import sys
import os
import tempfile
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

print("=== VectorStore Debug Session ===")

# Test basic imports
try:
    from vector_store import VectorStore, StoredChunk, SearchResult
    print("✓ VectorStore imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    exit(1)

# Test basic instantiation
try:
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / 'debug_vectorstore'
    print(f"✓ Temp directory created: {db_path}")
except Exception as e:
    print(f"✗ Temp directory creation failed: {e}")
    exit(1)

# Test VectorStore creation
try:
    print("Creating VectorStore...")
    store = VectorStore(persist_directory=str(db_path))
    print("✓ VectorStore created successfully")
except Exception as e:
    print(f"✗ VectorStore creation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test basic operations
try:
    print("Testing get_collection_size...")
    size = store.get_collection_size()
    print(f"✓ Collection size: {size}")
except Exception as e:
    print(f"✗ get_collection_size failed: {e}")
    import traceback
    traceback.print_exc()

# Test search with empty collection
try:
    print("Testing search_by_vector on empty collection...")
    test_vector = np.random.rand(384)
    results = store.search_by_vector(test_vector, top_k=1)
    print(f"✓ Search completed: {len(results)} results")
except Exception as e:
    print(f"✗ search_by_vector failed: {e}")
    import traceback
    traceback.print_exc()

print("=== Debug Session Complete ===")
