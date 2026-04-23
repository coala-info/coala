"""Tests for ``coala.remote_api.tool_api``.

These tests avoid actually binding a network socket or executing the CWL tool
(which would require Docker). They focus on the initialisation logic –
building the Pydantic input model, discovering inputs/outputs and wiring up
FastAPI routes – using the bundled md5sum CWL fixture.
"""

from typing import get_args, get_origin, Union
from fastapi.testclient import TestClient

from coala.remote_api import tool_api


CWL_FILE = 'tests/dockstore-tool-md5sum.cwl'


class TestToolApiInit:
    def test_defaults(self):
        api = tool_api(cwl_file=CWL_FILE)
        assert api.cwl_file == CWL_FILE
        assert api.tool_name == 'tool'
        assert api.host == '0.0.0.0'
        assert api.port == 8000
        assert api.read_outs is False
        assert api.server is None
        assert api.url is None

    def test_custom_params(self):
        api = tool_api(
            cwl_file=CWL_FILE,
            tool_name='md5sum',
            host='127.0.0.1',
            port=9100,
            read_outs=True,
        )
        assert api.tool_name == 'md5sum'
        assert api.host == '127.0.0.1'
        assert api.port == 9100
        assert api.read_outs is True

    def test_inputs_outputs_loaded(self):
        api = tool_api(cwl_file=CWL_FILE, tool_name='md5sum')
        input_names = {it['name'] for it in api.inputs}
        output_names = {ot['name'] for ot in api.outputs}
        assert 'input_file' in input_names
        assert 'output_file' in output_names

    def test_pydantic_model_structure(self):
        """Input file fields should map to ``Optional[str]`` in the generated
        Pydantic model – they are modelled as string paths and all fields are
        marked optional by the current implementation."""
        api = tool_api(cwl_file=CWL_FILE, tool_name='md5sum')
        Base = api.Base
        assert 'input_file' in Base.model_fields

        annotation = Base.model_fields['input_file'].annotation
        # Accept either bare str or Optional[str] (Union[str, None]).
        if get_origin(annotation) is Union:
            args = set(get_args(annotation))
            assert str in args
            assert type(None) in args
        else:
            assert annotation is str


class TestToolApiRoutes:
    def test_fastapi_routes_registered(self):
        api = tool_api(cwl_file=CWL_FILE, tool_name='md5sum')
        paths = {route.path for route in api.app.routes}
        assert '/uploadFile/' in paths
        assert '/md5sum/' in paths

    def test_tool_name_influences_route(self):
        api = tool_api(cwl_file=CWL_FILE, tool_name='my_custom_name')
        paths = {route.path for route in api.app.routes}
        assert '/my_custom_name/' in paths

    def test_upload_endpoint_accepts_file(self, tmp_path):
        """The /uploadFile/ endpoint persists the upload and echoes metadata.

        This does NOT touch the CWL-running endpoint (which requires Docker).
        """
        api = tool_api(cwl_file=CWL_FILE, tool_name='md5sum')
        payload = b"hello-upload"
        src = tmp_path / "up.txt"
        src.write_bytes(payload)

        with TestClient(api.app) as client:
            with open(src, "rb") as fh:
                resp = client.post(
                    "/uploadFile/",
                    files={"file": ("up.txt", fh, "text/plain")},
                )

        assert resp.status_code == 200
        body = resp.json()
        assert body["filename"] == "up.txt"
        assert "filepath" in body
        # The server stores the file on disk with identical contents.
        with open(body["filepath"], "rb") as fh:
            assert fh.read() == payload
