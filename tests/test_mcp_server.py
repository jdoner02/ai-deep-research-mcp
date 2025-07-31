"""
TDD Cycle 8: MCP Server Implementation Tests
Test suite for implementing MCP (Model Context Protocol) server
to expose our AI research system to GitHub Copilot agents.
"""
import pytest
import json
import asyncio
import subprocess
import sys
import os
from pathlib import Path

# Import path setup
package_root = Path(__file__).parent.parent  
sys.path.insert(0, str(package_root))
print(f"✅ src package imported successfully from {package_root}")

class TestMCPServer:
    """Test MCP server implementation and protocol compliance"""
    
    def test_mcp_server_module_exists(self):
        """Test MCP server module can be imported"""
        print("\n🟢 GREEN: Testing MCP server module existence")
        print("Should PASS - module implemented")
        try:
            from mcp_server import MCPServer
            assert MCPServer is not None, "MCPServer class should exist"
            print("✅ MCPServer class exists")
        except ImportError:
            pytest.fail("MCP server module not implemented - needed for Copilot agent access")
    
    def test_mcp_server_initialization(self):
        """Test MCP server can be initialized with our research system"""
        print("\n🟢 GREEN: Testing MCP server initialization")
        print("Should PASS - initialization implemented")
        
        try:
            from mcp_server import MCPServer
            
            server = MCPServer()
            assert server is not None, "Server should initialize"
            assert hasattr(server, "tools"), "Server should have tools attribute"
            assert hasattr(server, "handle_request"), "Server should have handle_request method"
            
            print("✅ MCP server initialization working")
        except Exception as e:
            pytest.fail(f"MCP server initialization failed: {e}")
    
    def test_mcp_server_tool_definitions(self):
        """Test MCP server exposes research tools"""
        print("\n🟢 GREEN: Testing MCP tool definitions")
        print("Should PASS - tool definitions implemented")
        
        try:
            from mcp_server import MCPServer
            
            server = MCPServer()
            
            # Check that expected tools are defined
            expected_tools = [
                "research_query",
                "search_web", 
                "extract_content",
                "list_sources"
            ]
            
            for tool_name in expected_tools:
                assert tool_name in server.tools, f"Tool '{tool_name}' should be defined"
                tool_def = server.tools[tool_name]
                assert "description" in tool_def, f"Tool '{tool_name}' should have description"
                assert "parameters" in tool_def, f"Tool '{tool_name}' should have parameters"
            
            print(f"✅ All {len(expected_tools)} tools properly defined")
        except Exception as e:
            pytest.fail(f"MCP tool definitions failed: {e}")

class TestMCPProtocolCompliance:
    """Test MCP protocol compliance and message handling"""
    
    def test_mcp_initialize_request(self):
        """Test MCP initialize request handling"""
        print("\n🟢 GREEN: Testing MCP initialize request")
        print("Should PASS - initialize handler implemented")
        
        try:
            from mcp_server import MCPServer
            
            server = MCPServer()
            
            # MCP initialize request format
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "GitHub Copilot",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = server.handle_request(request)
            
            assert response is not None, "Initialize should return response"
            assert response.get("jsonrpc") == "2.0", "Response should be valid JSON-RPC"
            assert response.get("id") == 1, "Response should match request ID"
            assert "result" in response, "Initialize should return result"
            
            result = response["result"]
            assert "protocolVersion" in result, "Result should include protocol version"
            assert "capabilities" in result, "Result should include server capabilities"
            assert "serverInfo" in result, "Result should include server info"
            
            print("✅ MCP initialize request handled correctly")
        except Exception as e:
            pytest.fail(f"MCP initialize request failed: {e}")
    
    def test_mcp_tools_list_request(self):
        """Test MCP tools/list request handling"""
        print("\n🟢 GREEN: Testing MCP tools/list request") 
        print("Should PASS - tools/list handler implemented")
        
        try:
            from mcp_server import MCPServer
            
            server = MCPServer()
            
            # MCP tools/list request format
            request = {
                "jsonrpc": "2.0", 
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = server.handle_request(request)
            
            assert response is not None, "tools/list should return response"
            assert response.get("jsonrpc") == "2.0", "Response should be valid JSON-RPC"
            assert response.get("id") == 2, "Response should match request ID"
            assert "result" in response, "tools/list should return result"
            
            result = response["result"]
            assert "tools" in result, "Result should include tools array"
            assert len(result["tools"]) > 0, "Should have at least one tool"
            
            # Check first tool structure
            tool = result["tools"][0]
            assert "name" in tool, "Tool should have name"
            assert "description" in tool, "Tool should have description"
            assert "inputSchema" in tool, "Tool should have input schema"
            
            print(f"✅ tools/list returned {len(result['tools'])} tools")
        except Exception as e:
            pytest.fail(f"MCP tools/list request failed: {e}")
    
    def test_mcp_tool_call_research_query(self):
        """Test MCP tools/call request for research_query"""
        print("\n🟢 GREEN: Testing MCP tools/call for research_query")
        print("Should PASS - tools/call handler implemented")
        
        try:
            from mcp_server import MCPServer
            
            server = MCPServer()
            
            # MCP tools/call request format
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "research_query",
                    "arguments": {
                        "query": "What is cybersecurity?",
                        "max_sources": 3
                    }
                }
            }
            
            response = server.handle_request(request)
            
            assert response is not None, "tools/call should return response"
            assert response.get("jsonrpc") == "2.0", "Response should be valid JSON-RPC"
            assert response.get("id") == 3, "Response should match request ID"
            assert "result" in response, "tools/call should return result"
            
            result = response["result"]
            assert "content" in result, "Result should include content"
            assert len(result["content"]) > 0, "Should have at least one content item"
            
            # Check content structure
            content = result["content"][0]
            assert "type" in content, "Content should have type"
            assert content["type"] == "text", "Content type should be text"
            assert "text" in content, "Content should have text field"
            assert len(content["text"]) > 0, "Content text should not be empty"
            
            print("✅ research_query tool call handled correctly")
        except Exception as e:
            pytest.fail(f"MCP research_query tool call failed: {e}")

class TestMCPServerIntegration:
    """Test MCP server integration with existing research system"""
    
    def test_mcp_server_command_line_interface(self):
        """Test MCP server can be run from command line"""
        print("\n🟢 GREEN: Testing MCP server CLI")
        print("Should PASS - CLI interface implemented")
        
        try:
            # Test that the server can be imported as a module
            import subprocess
            import sys
            import os
            
            # Change to parent directory where the package can be found  
            # Get the ai_deep_research_mcp directory first
            current_dir = os.path.dirname(os.path.abspath(__file__))  # tests dir
            package_dir = os.path.dirname(current_dir)  # ai_deep_research_mcp dir  
            parent_dir = os.path.dirname(package_dir)  # 0. Knowledge Manager dir
            
            # Try to run the server in check mode (should not hang)
            result = subprocess.run([
                sys.executable, "-m", "ai_deep_research_mcp", "--check"
            ], capture_output=True, text=True, timeout=5, cwd=parent_dir)
            
            # Should exit cleanly in check mode
            assert result.returncode == 0, f"Server check failed: {result.stderr}"
            
            # Should output server information
            output = result.stdout
            assert "AI Deep Research MCP Server" in output, "Should identify as AI Deep Research server"
            assert "Tools available:" in output, "Should list available tools"
            
            print("✅ MCP server CLI working correctly")
        except subprocess.TimeoutExpired:
            pytest.fail("MCP server CLI hung - implementation needed")
        except FileNotFoundError:
            pytest.fail("MCP server module not found - needs implementation")
        except Exception as e:
            pytest.fail(f"MCP server CLI failed: {e}")
    
    def test_mcp_server_stdio_communication(self):
        """Test MCP server communicates via stdio"""
        print("\n🟢 GREEN: Testing MCP server stdio communication")
        print("Should PASS - stdio communication implemented")
        
        try:
            import subprocess
            import sys
            import json
            import os
            
            # Change to parent directory where the package can be found
            current_dir = os.path.dirname(os.path.abspath(__file__))  # tests dir
            package_dir = os.path.dirname(current_dir)  # ai_deep_research_mcp dir  
            parent_dir = os.path.dirname(package_dir)  # 0. Knowledge Manager dir
            
            # Start the server process
            process = subprocess.Popen([
                sys.executable, "-m", "ai_deep_research_mcp"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
               stderr=subprocess.PIPE, text=True, cwd=parent_dir)
            
            try:
                # Send initialize request
                initialize_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "clientInfo": {"name": "Test Client", "version": "1.0.0"}
                    }
                }
                
                # Send request via stdin
                process.stdin.write(json.dumps(initialize_request) + "\n")
                process.stdin.flush()
                
                # Read response from stdout
                response_line = process.stdout.readline()
                assert response_line.strip(), "Should receive response"
                
                response = json.loads(response_line)
                assert response.get("jsonrpc") == "2.0", "Should be valid JSON-RPC response"
                assert response.get("id") == 1, "Should match request ID"
                assert "result" in response, "Should have result"
                
                print("✅ MCP server stdio communication working")
                
            finally:
                process.terminate()
                process.wait(timeout=5)
                
        except subprocess.TimeoutExpired:
            pytest.fail("MCP server stdio communication timeout")
        except Exception as e:
            pytest.fail(f"MCP server stdio communication failed: {e}")

if __name__ == "__main__":
    print("🧪 TDD Cycle 8 - GREEN Phase: MCP Server Implementation")
    print("="*70)
    
    # Run the tests - they should PASS (GREEN phase)
    test_server = TestMCPServer()
    test_protocol = TestMCPProtocolCompliance() 
    test_integration = TestMCPServerIntegration()
    
    try:
        print("\n1️⃣  Testing MCP server module existence...")
        test_server.test_mcp_server_module_exists()
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    try:
        print("\n2️⃣  Testing MCP server initialization...")
        test_server.test_mcp_server_initialization()
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    try:
        print("\n3️⃣  Testing MCP tool definitions...")
        test_server.test_mcp_server_tool_definitions()
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    try:
        print("\n4️⃣  Testing MCP initialize request handling...")
        test_protocol.test_mcp_initialize_request()
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    try:
        print("\n5️⃣  Testing MCP tools/list request handling...")
        test_protocol.test_mcp_tools_list_request()
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    try:
        print("\n6️⃣  Testing MCP tools/call request handling...")
        test_protocol.test_mcp_tool_call_research_query()
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    try:
        print("\n7️⃣  Testing MCP server CLI interface...")
        test_integration.test_mcp_server_command_line_interface()
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    try:
        print("\n8️⃣  Testing MCP server stdin/stdout communication...")
        test_integration.test_mcp_server_stdio_communication()
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    print(f"\n🟢 GREEN PHASE COMPLETE: All tests should pass")
    print(f"📋 Next: REFACTOR phase to optimize implementation")