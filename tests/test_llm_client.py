#!/usr/bin/env python3
"""
AI Deep Research MCP - LLMClient Tests

Test suite for the LLMClient component that handles large language model integration
for answer generation and summarization. Follows TDD principles.

PHASE: RED - Writing failing tests first
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, AsyncIterator
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Import from src package using the fixed import system
from src.llm_client import (
    LLMClient, 
    LLMConfig, 
    GenerationResponse, 
    ChatMessage, 
    MessageRole,
    TokenUsage,
    GenerationError
)
from src.retriever import RetrievalResult


class TestLLMClient:
    """Test the LLMClient component for language model integration"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "llm_config.json"
    
    def teardown_method(self):
        """Clean up test fixtures after each test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_llm_client_exists(self):
        """Test that LLMClient class can be instantiated"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.7,
            max_tokens=1000
        )
        
        client = LLMClient(config=config)
        
        assert client is not None
        assert hasattr(client, 'generate_response')
        assert hasattr(client, 'generate_summary')
        assert hasattr(client, 'generate_with_context')
    
    def test_llm_config_dataclass(self):
        """Test LLMConfig dataclass structure and validation"""
        config = LLMConfig(
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=2000,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            timeout=30.0,
            api_key="test-key",
            base_url="https://api.openai.com/v1"
        )
        
        assert config.model_name == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.top_p == 0.9
        assert config.frequency_penalty == 0.1
        assert config.presence_penalty == 0.1
        assert config.timeout == 30.0
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.openai.com/v1"
        
        # Test validation
        with pytest.raises(ValueError):
            LLMConfig(model_name="", temperature=0.7, max_tokens=1000)
        
        with pytest.raises(ValueError):
            LLMConfig(model_name="test", temperature=-0.1, max_tokens=1000)
        
        with pytest.raises(ValueError):
            LLMConfig(model_name="test", temperature=0.7, max_tokens=0)
    
    def test_generation_response_dataclass(self):
        """Test GenerationResponse dataclass structure"""
        response = GenerationResponse(
            text="Generated response text",
            finish_reason="stop",
            token_usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
            model="gpt-4",
            response_time=1.5,
            citations=["Source 1", "Source 2"]
        )
        
        assert response.text == "Generated response text"
        assert response.finish_reason == "stop"
        assert response.token_usage.total_tokens == 150
        assert response.model == "gpt-4"
        assert response.response_time == 1.5
        assert response.citations == ["Source 1", "Source 2"]
    
    def test_chat_message_dataclass(self):
        """Test ChatMessage dataclass and MessageRole enum"""
        # Test system message
        system_msg = ChatMessage(
            role=MessageRole.SYSTEM,
            content="You are a helpful research assistant."
        )
        
        assert system_msg.role == MessageRole.SYSTEM
        assert system_msg.content == "You are a helpful research assistant."
        
        # Test user message
        user_msg = ChatMessage(
            role=MessageRole.USER,
            content="What is machine learning?",
            metadata={"query_id": "q123"}
        )
        
        assert user_msg.role == MessageRole.USER
        assert user_msg.content == "What is machine learning?"
        assert user_msg.metadata["query_id"] == "q123"
        
        # Test assistant message
        assistant_msg = ChatMessage(
            role=MessageRole.ASSISTANT,
            content="Machine learning is a subset of AI...",
            citations=["Source A", "Source B"]
        )
        
        assert assistant_msg.role == MessageRole.ASSISTANT
        assert assistant_msg.citations == ["Source A", "Source B"]
    
    def test_token_usage_dataclass(self):
        """Test TokenUsage dataclass calculations"""
        usage = TokenUsage(
            prompt_tokens=150,
            completion_tokens=75,
            total_tokens=225
        )
        
        assert usage.prompt_tokens == 150
        assert usage.completion_tokens == 75
        assert usage.total_tokens == 225
        
        # Test auto-calculation
        usage_auto = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50
            # total_tokens should be calculated automatically
        )
        
        assert usage_auto.total_tokens == 150
    
    @pytest.mark.asyncio
    async def test_basic_text_generation(self):
        """Test basic text generation functionality"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.7,
            max_tokens=1000
        )
        
        client = LLMClient(config=config)
        
        # Mock the underlying LLM call
        with patch.object(client, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = GenerationResponse(
                text="This is a test response about machine learning.",
                finish_reason="stop",
                token_usage=TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
                model="test-model",
                response_time=0.5
            )
            
            response = await client.generate_response("What is machine learning?")
            
            assert isinstance(response, GenerationResponse)
            assert "machine learning" in response.text.lower()
            assert response.finish_reason == "stop"
            assert response.token_usage.total_tokens == 30
            mock_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_summarization_with_sources(self):
        """Test summarization with retrieved sources"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.3,  # Lower temperature for summarization
            max_tokens=1500
        )
        
        client = LLMClient(config=config)
        
        # Create mock retrieval results
        retrieval_results = [
            RetrievalResult(
                chunk_id="chunk_1",
                text="Machine learning is a method of data analysis...",
                source_url="https://example.com/ml-guide",
                metadata={"title": "ML Guide"},
                relevance_score=0.9,
                rank=1
            ),
            RetrievalResult(
                chunk_id="chunk_2", 
                text="Deep learning uses neural networks with multiple layers...",
                source_url="https://example.com/dl-paper",
                metadata={"title": "Deep Learning Paper"},
                relevance_score=0.8,
                rank=2
            )
        ]
        
        with patch.object(client, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = GenerationResponse(
                text="Based on the sources, machine learning is a data analysis method that includes deep learning techniques using neural networks.",
                finish_reason="stop",
                token_usage=TokenUsage(prompt_tokens=200, completion_tokens=25, total_tokens=225),
                model="test-model",
                response_time=1.0,
                citations=["ML Guide", "Deep Learning Paper"]
            )
            
            response = await client.generate_summary(
                query="What is machine learning?",
                retrieved_context=retrieval_results
            )
            
            assert isinstance(response, GenerationResponse)
            assert len(response.citations) == 2
            assert "ML Guide" in response.citations
            assert "Deep Learning Paper" in response.citations
            mock_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_chat_conversation_handling(self):
        """Test multi-turn chat conversation support"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.7,
            max_tokens=1000
        )
        
        client = LLMClient(config=config)
        
        conversation = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content="You are a helpful research assistant."
            ),
            ChatMessage(
                role=MessageRole.USER,
                content="What is artificial intelligence?"
            ),
            ChatMessage(
                role=MessageRole.ASSISTANT,
                content="AI is a field of computer science..."
            ),
            ChatMessage(
                role=MessageRole.USER,
                content="How does it relate to machine learning?"
            )
        ]
        
        with patch.object(client, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = GenerationResponse(
                text="Machine learning is a subset of AI that focuses on algorithms that can learn from data.",
                finish_reason="stop",
                token_usage=TokenUsage(prompt_tokens=150, completion_tokens=20, total_tokens=170),
                model="test-model",
                response_time=0.8
            )
            
            response = await client.generate_with_context(
                messages=conversation
            )
            
            assert isinstance(response, GenerationResponse)
            assert "machine learning" in response.text.lower()
            mock_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_streaming_response_support(self):
        """Test streaming response generation"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.7,
            max_tokens=1000,
            stream=True
        )
        
        client = LLMClient(config=config)
        
        # Mock streaming response
        async def mock_stream():
            chunks = [
                "This ", "is ", "a ", "streaming ", "response."
            ]
            for chunk in chunks:
                yield chunk
        
        with patch.object(client, '_stream_llm', return_value=mock_stream()) as mock_stream_call:
            response_chunks = []
            async for chunk in client.generate_stream("Test streaming"):
                response_chunks.append(chunk)
            
            assert len(response_chunks) == 5
            assert "".join(response_chunks) == "This is a streaming response."
            mock_stream_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_and_retries(self):
        """Test error handling and retry mechanisms"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.7,
            max_tokens=1000,
            max_retries=3,
            retry_delay=0.1
        )
        
        client = LLMClient(config=config)
        
        # Test timeout error
        with patch.object(client, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = asyncio.TimeoutError("Request timed out")
            
            with pytest.raises(GenerationError) as exc_info:
                await client.generate_response("Test query")
            
            assert "timeout" in str(exc_info.value).lower()
            assert mock_call.call_count <= config.max_retries + 1
        
        # Test API error with successful retry
        with patch.object(client, '_call_llm', new_callable=AsyncMock) as mock_call:
            # First call fails, second succeeds
            mock_call.side_effect = [
                Exception("API error"),
                GenerationResponse(
                    text="Success after retry",
                    finish_reason="stop",
                    token_usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
                    model="test-model",
                    response_time=0.5
                )
            ]
            
            response = await client.generate_response("Test query")
            
            assert response.text == "Success after retry"
            assert mock_call.call_count == 2
    
    @pytest.mark.asyncio
    async def test_token_counting_and_limits(self):
        """Test token counting and enforcement of limits"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.7,
            max_tokens=100,  # Low limit for testing
            enforce_limits=True
        )
        
        client = LLMClient(config=config)
        
        # Test prompt that exceeds token limit
        very_long_prompt = "Test " * 1000  # Should exceed token limit
        
        with pytest.raises(GenerationError) as exc_info:
            await client.generate_response(very_long_prompt)
        
        assert "token limit" in str(exc_info.value).lower()
    
    def test_prompt_templates_and_formatting(self):
        """Test prompt template system and formatting"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.7,
            max_tokens=1000
        )
        
        client = LLMClient(config=config)
        
        # Test research summary template
        template_vars = {
            "query": "What is machine learning?",
            "context": "Machine learning is a subset of AI...",
            "sources": ["Source A", "Source B"]
        }
        
        formatted_prompt = client.format_research_prompt(**template_vars)
        
        assert "What is machine learning?" in formatted_prompt
        assert "Machine learning is a subset of AI" in formatted_prompt
        assert "Source A" in formatted_prompt
        assert "Source B" in formatted_prompt
        
        # Test citation formatting
        citations = client.format_citations(["https://example.com", "https://test.org"])
        
        assert "example.com" in citations
        assert "test.org" in citations
    
    @pytest.mark.asyncio
    async def test_model_switching_and_fallback(self):
        """Test switching between models and fallback mechanisms"""
        primary_config = LLMConfig(
            model_name="primary-model",
            temperature=0.7,
            max_tokens=1000
        )
        
        fallback_config = LLMConfig(
            model_name="fallback-model", 
            temperature=0.7,
            max_tokens=1000
        )
        
        client = LLMClient(
            config=primary_config,
            fallback_config=fallback_config
        )
        
        with patch.object(client, '_call_llm', new_callable=AsyncMock) as mock_call:
            # Primary model fails, fallback succeeds
            mock_call.side_effect = [
                Exception("Primary model unavailable"),
                GenerationResponse(
                    text="Response from fallback model",
                    finish_reason="stop",
                    token_usage=TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
                    model="fallback-model",
                    response_time=0.7
                )
            ]
            
            response = await client.generate_response("Test query")
            
            assert response.text == "Response from fallback model"
            assert response.model == "fallback-model"
            assert mock_call.call_count == 2
    
    def test_configuration_persistence(self):
        """Test saving and loading LLM configuration"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.8,
            max_tokens=1500,
            api_key="secret-key"
        )
        
        client = LLMClient(config=config)
        
        # Save configuration
        client.save_config(str(self.config_path))
        
        assert self.config_path.exists()
        
        # Load configuration
        loaded_client = LLMClient.from_config_file(str(self.config_path))
        
        assert loaded_client.config.model_name == "test-model"
        assert loaded_client.config.temperature == 0.8
        assert loaded_client.config.max_tokens == 1500
        # API key should be redacted in saved config for security
        assert loaded_client.config.api_key != "secret-key" or loaded_client.config.api_key is None
    
    @pytest.mark.asyncio
    async def test_concurrent_generation_handling(self):
        """Test handling multiple concurrent generation requests"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.7,
            max_tokens=1000,
            max_concurrent_requests=3
        )
        
        client = LLMClient(config=config)
        
        async def mock_generate(query):
            await asyncio.sleep(0.1)  # Simulate processing time
            return GenerationResponse(
                text=f"Response to: {query}",
                finish_reason="stop",
                token_usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
                model="test-model",
                response_time=0.1
            )
        
        with patch.object(client, '_call_llm', new_callable=AsyncMock, side_effect=mock_generate):
            # Launch multiple concurrent requests
            tasks = [
                client.generate_response(f"Query {i}")
                for i in range(5)
            ]
            
            responses = await asyncio.gather(*tasks)
            
            assert len(responses) == 5
            for i, response in enumerate(responses):
                assert f"Query {i}" in response.text
    
    def test_performance_metrics_tracking(self):
        """Test performance metrics collection and reporting"""
        config = LLMConfig(
            model_name="test-model",
            temperature=0.7,
            max_tokens=1000,
            track_performance=True
        )
        
        client = LLMClient(config=config)
        
        # Simulate some usage through the performance tracker
        client._performance_tracker.update_metrics(
            tokens_used=100,
            response_time=1.5,
            success=True
        )
        
        client._performance_tracker.update_metrics(
            tokens_used=150,
            response_time=2.0,
            success=True
        )
        
        metrics = client.get_performance_metrics()
        
        assert "total_requests" in metrics
        assert "total_tokens" in metrics
        assert "avg_response_time" in metrics
        assert "success_rate" in metrics
        
        assert metrics["total_requests"] == 2
        assert metrics["total_tokens"] == 250
        assert metrics["avg_response_time"] == 1.75
        assert metrics["success_rate"] == 1.0


class TestLLMClientIntegration:
    """Integration tests for LLMClient with other components"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures after each test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_end_to_end_research_generation(self):
        """Test complete research answer generation pipeline"""
        config = LLMConfig(
            model_name="test-research-model",
            temperature=0.3,
            max_tokens=2000
        )
        
        client = LLMClient(config=config)
        
        # Create realistic retrieval results
        retrieval_results = [
            RetrievalResult(
                chunk_id="academic_1",
                text="Machine learning algorithms enable computers to learn patterns from data without explicit programming. They form the foundation of modern AI systems.",
                source_url="https://academic.example.com/ml-foundations",
                metadata={"title": "Machine Learning Foundations", "author": "Dr. Smith", "year": 2024},
                relevance_score=0.95,
                rank=1
            ),
            RetrievalResult(
                chunk_id="academic_2",
                text="Deep learning, a subset of machine learning, uses neural networks with multiple layers to process complex patterns in data such as images and text.",
                source_url="https://academic.example.com/deep-learning",
                metadata={"title": "Deep Learning Applications", "author": "Dr. Johnson", "year": 2024},
                relevance_score=0.88,
                rank=2
            ),
            RetrievalResult(
                chunk_id="industry_1",
                text="In practice, machine learning is widely used in recommendation systems, fraud detection, and autonomous vehicles across various industries.",
                source_url="https://industry.example.com/ml-applications",
                metadata={"title": "ML in Industry", "domain": "industry"},
                relevance_score=0.82,
                rank=3
            )
        ]
        
        # Mock the LLM response for research generation
        expected_response = GenerationResponse(
            text="""Based on the research findings, machine learning is a fundamental approach in artificial intelligence that enables computers to learn patterns from data without explicit programming [1]. 

Machine learning algorithms form the foundation of modern AI systems and have evolved to include sophisticated techniques like deep learning, which uses neural networks with multiple layers to process complex patterns in data such as images and text [2].

In practical applications, machine learning has found widespread adoption across various industries, including recommendation systems, fraud detection, and autonomous vehicles [3]. This demonstrates the versatility and real-world impact of these technologies.

## Sources
[1] Machine Learning Foundations - Dr. Smith (2024)
[2] Deep Learning Applications - Dr. Johnson (2024) 
[3] ML in Industry - industry.example.com""",
            finish_reason="stop",
            token_usage=TokenUsage(prompt_tokens=350, completion_tokens=120, total_tokens=470),
            model="test-research-model",
            response_time=2.5,
            citations=[
                "Machine Learning Foundations - Dr. Smith (2024)",
                "Deep Learning Applications - Dr. Johnson (2024)",
                "ML in Industry - industry.example.com"
            ]
        )
        
        with patch.object(client, '_call_llm', new_callable=AsyncMock, return_value=expected_response):
            response = await client.generate_research_answer(
                query="What is machine learning and how is it used?",
                retrieved_context=retrieval_results,
                include_citations=True,
                citation_style="academic"
            )
            
            # Validate response structure
            assert isinstance(response, GenerationResponse)
            assert len(response.text) > 100  # Substantial response
            assert "machine learning" in response.text.lower()
            
            # Validate citations
            assert len(response.citations) == 3
            assert any("Dr. Smith" in citation for citation in response.citations)
            assert any("Dr. Johnson" in citation for citation in response.citations)
            
            # Validate source attribution in text
            assert "[1]" in response.text
            assert "[2]" in response.text  
            assert "[3]" in response.text
            
            # Validate performance metrics
            assert response.token_usage.total_tokens > 0
            assert response.response_time > 0
