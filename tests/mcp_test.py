import os
from typing import Optional

import pytest
from pydantic import Field, create_model

from coala.mcp_api import mcp_api


CWL_FILE = 'tests/dockstore-tool-md5sum.cwl'


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


class TestCwlTypeHint:
    """Exercises mcp_api._cwl_type_hint across the supported type forms."""

    @pytest.fixture
    def api(self):
        return mcp_api()

    @pytest.mark.parametrize("type_val,expected", [
        ('string', 'str'),
        ('File', 'file path'),
        ('int', 'int'),
        ('float', 'float'),
        ('double', 'float'),
        ('boolean', 'bool'),
    ])
    def test_plain_scalar_types(self, api, type_val, expected):
        assert api._cwl_type_hint(type_val) == expected

    @pytest.mark.parametrize("type_val,expected", [
        (['null', 'File'], 'file path'),
        (['null', 'string'], 'str'),
        (['null', 'int'], 'int'),
    ])
    def test_optional_types(self, api, type_val, expected):
        assert api._cwl_type_hint(type_val) == expected

    @pytest.mark.parametrize("type_val,expected", [
        ('float[]', 'array of float'),
        ('int[]', 'array of int'),
        ('string[]', 'array of str'),
        (['null', 'File[]'], 'array of file path'),
    ])
    def test_shorthand_array_types(self, api, type_val, expected):
        assert api._cwl_type_hint(type_val) == expected

    def test_dict_array_type(self, api):
        t = {'type': 'array', 'items': 'float'}
        assert api._cwl_type_hint(t) == 'array of float'

    def test_optional_dict_array_type(self, api):
        t = ['null', {'type': 'array', 'items': 'File'}]
        assert api._cwl_type_hint(t) == 'array of file path'

    @pytest.mark.parametrize("type_val", [None, '', 'unknown_type'])
    def test_missing_or_unknown_returns_empty(self, api, type_val):
        assert api._cwl_type_hint(type_val) == ""


class TestBuildDescriptions:
    @pytest.fixture
    def api(self):
        return mcp_api()

    def test_field_description_with_type_hint(self, api):
        model = create_model(
            'M',
            counts=(str, Field(description='Raw counts file')),
        )
        input_field = {'name': 'counts', 'doc': 'Raw counts file', 'type': 'File'}
        desc = api._build_field_description('counts', input_field, model.model_fields['counts'])
        assert 'counts' in desc
        assert 'Raw counts file' in desc
        assert 'str' in desc
        assert 'file path' in desc

    def test_field_description_without_type_hint(self, api):
        model = create_model(
            'M',
            weird=(str, Field(description='Something')),
        )
        input_field = {'name': 'weird', 'doc': 'Something', 'type': 'enum'}
        desc = api._build_field_description('weird', input_field, model.model_fields['weird'])
        assert 'weird' in desc
        assert 'Something' in desc
        assert 'str' in desc

    def test_optional_field_description(self, api):
        model = create_model(
            'M',
            flag=(Optional[int], None),
        )
        input_field = {'name': 'flag', 'doc': 'A flag', 'type': ['null', 'int']}
        desc = api._build_field_description('flag', input_field, model.model_fields['flag'])
        assert 'flag' in desc
        assert 'A flag' in desc
        assert 'int' in desc

    def test_output_description_with_type_hint(self, api):
        out = {'name': 'output_file', 'doc': 'The result', 'type': 'File'}
        desc = api._build_output_description(out)
        assert desc == 'output_file: The result, file path'

    def test_output_description_without_type_hint(self, api):
        out = {'name': 'x', 'doc': 'desc', 'type': 'enum'}
        desc = api._build_output_description(out)
        assert desc == 'x: desc'


class TestTransformInputValue:
    @pytest.fixture
    def api(self):
        return mcp_api()

    def test_none_value_passthrough(self, api):
        assert api._transform_input_value('f', None, 'File') is None

    def test_existing_file_resolved_to_absolute(self, api, tmp_path, monkeypatch):
        f = tmp_path / "data.txt"
        f.write_text("x")
        monkeypatch.chdir(tmp_path)

        result = api._transform_input_value('input_file', 'data.txt', 'File')
        assert os.path.isabs(result)
        assert os.path.abspath(result) == str(f)

    def test_file_uri_is_preserved(self, api, tmp_path):
        uri = (tmp_path / "x.txt").as_uri()
        result = api._transform_input_value('input_file', uri, 'File')
        assert result == uri

    def test_unresolvable_file_returned_as_is(self, api):
        result = api._transform_input_value('input_file', 'no_such_file.xyz', 'File')
        assert result == 'no_such_file.xyz'

    def test_string_with_nonexistent_dir_kept_whole(self, api):
        # Directory does not exist -> keep the original string.
        result = api._transform_input_value('name', '/zzz/definitely/missing/foo.txt', 'string')
        assert result == '/zzz/definitely/missing/foo.txt'

    def test_string_with_existing_dir_becomes_basename(self, api, tmp_path):
        full_path = tmp_path / "thing.txt"
        result = api._transform_input_value('name', str(full_path), 'string')
        assert result == 'thing.txt'

    def test_string_without_path_separator_passthrough(self, api):
        result = api._transform_input_value('name', 'simple_value', 'string')
        assert result == 'simple_value'

    def test_optional_file_type_list(self, api, tmp_path, monkeypatch):
        f = tmp_path / "opt.txt"
        f.write_text("y")
        monkeypatch.chdir(tmp_path)

        result = api._transform_input_value('f', 'opt.txt', ['null', 'File'])
        assert result == str(f)

    def test_array_of_strings_transformed_elementwise(self, api, tmp_path):
        full = tmp_path / "inside.txt"
        values = [str(full), 'plain']
        result = api._transform_input_value('names', values, 'string[]')
        assert result == ['inside.txt', 'plain']

    def test_array_of_files_via_dict_type(self, api, tmp_path, monkeypatch):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("a")
        f2.write_text("b")
        monkeypatch.chdir(tmp_path)

        typ = {'type': 'array', 'items': 'File'}
        result = api._transform_input_value('files', ['a.txt', 'b.txt'], typ)
        assert result == [str(f1), str(f2)]


class TestAddToolRegistration:
    def test_tool_appears_in_mcp_registry(self):
        """add_tool must register the function with the underlying FastMCP."""
        mcp = mcp_api()
        mcp.add_tool(CWL_FILE, tool_name='md5_reg_test')

        tm = mcp.mcp._tool_manager
        names = {t.name for t in tm.list_tools()}
        assert 'md5_reg_test' in names

    def test_base_model_exposes_input_field(self):
        mcp = mcp_api()
        mcp.add_tool(CWL_FILE, tool_name='md5_base_test')
        Base = mcp.tools['md5_base_test']['Base']
        assert 'input_file' in Base.model_fields

    def test_id_without_fragment_falls_back_to_filename(self, tmp_path):
        """When the CWL 'id' has no '#fragment', the filename basename is used."""
        cwl_content = tmp_path / "noid.cwl"
        cwl_content.write_text(
            "cwlVersion: v1.0\n"
            "class: CommandLineTool\n"
            "baseCommand: echo\n"
            "inputs:\n"
            "  message:\n"
            "    type: string\n"
            "    inputBinding:\n"
            "      position: 1\n"
            "outputs: []\n"
        )
        mcp = mcp_api()
        mcp.add_tool(str(cwl_content))
        assert 'noid' in mcp.tools