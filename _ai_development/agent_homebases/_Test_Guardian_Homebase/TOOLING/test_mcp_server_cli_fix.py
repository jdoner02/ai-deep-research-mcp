"""
TDD Cycle: Fix MCP Server CLI Issue
RED Phase: Write failing test that captures the expected behavior
"""
import pytest
import subprocess
import sys
import os
from pathlib import Path


class TestMCPServerCLIFix:
    """Test MCP server CLI functionality - RED phase"""
    
    def test_mcp_server_check_mode_should_exit_quickly(self):
        """
        🔴 RED Phase Test: MCP server --check mode should exit quickly
        
        This test verifies that running the MCP server in --check mode
        exits quickly without loading heavy dependencies like transformers/torch.
        """
        print("\n🔴 RED Phase: Testing MCP server --check mode performance")
        print("Expected to PASS after fix - should exit quickly")
        
        # Get the correct working directory 
        current_dir = Path(__file__).parent  # TOOLING dir
        homebase_dir = current_dir.parent    # _Test_Guardian_Homebase dir  
        project_root = homebase_dir.parent   # ai_deep_research_mcp dir
        
        try:
            # Test the fixed command that avoids module loading issues
            result = subprocess.run([
                sys.executable, "__main__.py", "--check"
            ], 
            capture_output=True, 
            text=True, 
            timeout=2,  # Short timeout to verify quick exit
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root)}
            )
            
            # Should complete successfully
            assert result.returncode == 0, f"Check mode should succeed, got return code {result.returncode}"
            
            # Should contain expected output
            output = result.stdout.strip()
            assert "AI Deep Research MCP Server" in output, f"Should identify server, got: {output}"
            assert "Tools available:" in output, f"Should list tools, got: {output}"
            assert "research_query" in output, f"Should list research_query tool, got: {output}"
            
            print("✅ MCP server --check mode working correctly")
            print(f"✅ Output: {output[:200]}...")
            
        except subprocess.TimeoutExpired as e:
            pytest.fail(f"MCP server --check mode still hanging after fix: {e}")
        except FileNotFoundError as e:
            pytest.fail(f"MCP server module not found: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error in --check mode: {e}")
    
    def test_mcp_server_check_mode_output_format(self):
        """
        RED: Test that --check mode produces properly formatted output
        """
        print("\n🔴 RED Phase: Testing --check mode output format")
        
        current_dir = Path(__file__).parent  # TOOLING dir
        homebase_dir = current_dir.parent    # _Test_Guardian_Homebase dir  
        project_root = homebase_dir.parent   # ai_deep_research_mcp dir
        
        try:
            result = subprocess.run([
                sys.executable, "__main__.py", "--check"
            ], 
            capture_output=True, 
            text=True, 
            timeout=3,
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root)}
            )
            
            assert result.returncode == 0, "Check mode should succeed"
            
            output_lines = result.stdout.strip().split('\n')
            
            # Verify expected output structure
            assert len(output_lines) >= 4, f"Should have at least 4 lines of output, got {len(output_lines)}"
            assert "AI Deep Research MCP Server" in output_lines[0], "First line should be server name"
            assert "Version:" in result.stdout, "Should include version info"
            assert "Protocol:" in result.stdout, "Should include protocol info"
            
            # Verify all tools are listed
            expected_tools = ["research_query", "search_web", "extract_content", "list_sources"]
            for tool in expected_tools:
                assert tool in result.stdout, f"Should list {tool} tool"
            
            print("✅ Output format validation passed")
            
        except subprocess.TimeoutExpired:
            pytest.fail("MCP server --check mode hanging - fix needed")
        except Exception as e:
            pytest.fail(f"Output format test failed: {e}")


if __name__ == "__main__":
    print("🧪 TDD Cycle - RED Phase: MCP Server CLI Fix")
    print("="*60)
    
    # Run the tests - they should PASS after we fix the issue
    test_cli = TestMCPServerCLIFix()
    
    try:
        print("\n1️⃣  Testing --check mode performance...")
        test_cli.test_mcp_server_check_mode_should_exit_quickly()
    except Exception as e:
        print(f"❌ EXPECTED FAILURE (RED): {e}")
    
    try:
        print("\n2️⃣  Testing --check mode output format...")
        test_cli.test_mcp_server_check_mode_should_exit_quickly()
    except Exception as e:
        print(f"❌ EXPECTED FAILURE (RED): {e}")
    
    print("\n🎯 RED Phase Complete - Now implementing GREEN phase fix...")
