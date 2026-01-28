import pytest
import os
from coala.mcp_api import mcp_api


class TestMcpApi:
    """Basic feature tests for mcp_api class."""
    
    def test_init_default(self):
        """Test mcp_api initialization with default parameters."""
        mcp = mcp_api()
        assert mcp.host == '0.0.0.0'
        assert mcp.port == 8000
        assert mcp.container_runner is None
        assert mcp.tools == {}
        assert mcp.mcp is not None
    
    def test_init_custom(self):
        """Test mcp_api initialization with custom parameters."""
        mcp = mcp_api(host='127.0.0.1', port=9000, container_runner='docker')
        assert mcp.host == '127.0.0.1'
        assert mcp.port == 9000
        assert mcp.container_runner == 'docker'
        assert mcp.tools == {}
    
    def test_add_tool_default_name(self):
        """Test adding a tool with default name (from CWL file)."""
        cwl_file = 'tests/dockstore-tool-md5sum.cwl'
        assert os.path.exists(cwl_file), f"Test CWL file not found: {cwl_file}"
        
        mcp = mcp_api()
        mcp.add_tool(cwl_file)
        
        # Tool name should be derived from CWL id or filename
        # The CWL file has id: Md5sum, so tool_name should be 'Md5sum'
        assert 'Md5sum' in mcp.tools
        tool_info = mcp.tools['Md5sum']
        assert tool_info['cwl_file'] == cwl_file
        assert 'tool' in tool_info
        assert 'Base' in tool_info
        assert 'inputs' in tool_info
        assert 'outputs' in tool_info
    
    def test_add_tool_custom_name(self):
        """Test adding a tool with custom name."""
        cwl_file = 'tests/dockstore-tool-md5sum.cwl'
        assert os.path.exists(cwl_file), f"Test CWL file not found: {cwl_file}"
        
        mcp = mcp_api()
        custom_name = 'md5sum_custom'
        mcp.add_tool(cwl_file, tool_name=custom_name)
        
        assert custom_name in mcp.tools
        tool_info = mcp.tools[custom_name]
        assert tool_info['cwl_file'] == cwl_file
    
    def test_add_tool_nonexistent_file(self):
        """Test that adding a non-existent file raises FileNotFoundError."""
        mcp = mcp_api()
        with pytest.raises(FileNotFoundError):
            mcp.add_tool('nonexistent_file.cwl')
    
    def test_add_tool_directory_instead_of_file(self):
        """Test that adding a directory instead of file raises ValueError."""
        mcp = mcp_api()
        with pytest.raises(ValueError, match="Path is not a file"):
            mcp.add_tool('tests')
    
    def test_add_multiple_tools(self):
        """Test adding multiple tools."""
        cwl_file = 'tests/dockstore-tool-md5sum.cwl'
        assert os.path.exists(cwl_file), f"Test CWL file not found: {cwl_file}"
        
        mcp = mcp_api()
        mcp.add_tool(cwl_file, tool_name='tool1')
        mcp.add_tool(cwl_file, tool_name='tool2')
        
        assert 'tool1' in mcp.tools
        assert 'tool2' in mcp.tools
        assert len(mcp.tools) == 2
    
    def test_tool_info_structure(self):
        """Test that tool info has the expected structure."""
        cwl_file = 'tests/dockstore-tool-md5sum.cwl'
        assert os.path.exists(cwl_file), f"Test CWL file not found: {cwl_file}"
        
        mcp = mcp_api()
        mcp.add_tool(cwl_file, tool_name='test_tool')
        
        tool_info = mcp.tools['test_tool']
        required_keys = ['cwl_file', 'tool', 'Base', 'inputs', 'outputs']
        for key in required_keys:
            assert key in tool_info, f"Missing key '{key}' in tool_info"
        
        # Check that inputs and outputs are lists
        assert isinstance(tool_info['inputs'], list)
        assert isinstance(tool_info['outputs'], list)
        
        # Check that the CWL tool has expected structure
        assert tool_info['tool'] is not None