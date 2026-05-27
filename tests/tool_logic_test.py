"""Tests for the pure helpers in ``coala.tool_logic``.

These exercises stick to logic that does not require an actual CWL runtime or
container engine, so they can run quickly in any environment.
"""

import gzip
import os
from pathlib import Path
from urllib.parse import urlparse

import pytest
from cwltool.context import RuntimeContext

from coala import tool_logic
from coala.tool_logic import (
    _canonical_file_uri,
    _local_path_to_file_uri,
    _read_file_content,
    _remote_uri_string,
    configure_container_runner,
)


class TestRemoteUriString:
    @pytest.mark.parametrize("uri", [
        "http://example.com/file.txt",
        "https://example.com/file.txt",
        "ftp://example.com/file.txt",
        "s3://bucket/key",
        "gs://bucket/key",
    ])
    def test_remote_schemes_detected(self, uri):
        assert _remote_uri_string(uri) is True

    @pytest.mark.parametrize("s", [
        "file:///tmp/foo.txt",
        "/tmp/foo.txt",
        "relative/path.txt",
        "",
        "plain_string",
    ])
    def test_non_remote_strings(self, s):
        assert _remote_uri_string(s) is False


class TestLocalPathToFileUri:
    def test_absolute_path_becomes_file_uri(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("hi")

        uri = _local_path_to_file_uri(str(f))
        assert uri.startswith("file://")

        parsed = urlparse(uri)
        assert parsed.scheme == "file"
        # Path is resolved and absolute.
        assert Path(parsed.path) == f.resolve()

    def test_relative_path_is_resolved(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        f = tmp_path / "rel.txt"
        f.write_text("hi")

        uri = _local_path_to_file_uri("rel.txt")
        parsed = urlparse(uri)
        assert Path(parsed.path) == f.resolve()

    def test_user_home_is_expanded(self, tmp_path, monkeypatch):
        # Simulate a home directory under tmp_path so that '~' expands there.
        monkeypatch.setenv("HOME", str(tmp_path))
        f = tmp_path / "home_file.txt"
        f.write_text("hi")

        uri = _local_path_to_file_uri("~/home_file.txt")
        parsed = urlparse(uri)
        assert Path(parsed.path) == f.resolve()


class TestCanonicalFileUri:
    def test_roundtrip_for_local_path(self, tmp_path):
        f = tmp_path / "data.txt"
        f.write_text("payload")

        raw_uri = f.resolve().as_uri()
        canonical = _canonical_file_uri(raw_uri)

        assert canonical == raw_uri

    def test_percent_encoded_path_is_decoded(self, tmp_path):
        # Create a file whose name requires percent-encoding in URIs.
        f = tmp_path / "name with space.txt"
        f.write_text("x")

        raw_uri = f.resolve().as_uri()  # already percent-encodes spaces
        canonical = _canonical_file_uri(raw_uri)
        parsed = urlparse(canonical)
        assert Path(parsed.path).name == "name with space.txt" or "%20" in parsed.path

    def test_non_file_uri_rejected(self):
        with pytest.raises(ValueError):
            _canonical_file_uri("http://example.com/x")


class TestReadFileContent:
    def test_plain_text_file(self, tmp_path):
        f = tmp_path / "plain.txt"
        f.write_text("line1\nline2\n")

        # Newlines are stripped by the helper.
        assert _read_file_content(str(f)) == "line1line2"

    def test_gzip_file(self, tmp_path):
        f = tmp_path / "data.txt.gz"
        with gzip.open(f, "wt", encoding="utf-8") as fh:
            fh.write("abc\ndef\n")

        assert _read_file_content(str(f)) == "abcdef"

    def test_binary_file_returns_path(self, tmp_path):
        f = tmp_path / "blob.bin"
        # Include bytes that cannot be decoded as UTF-8.
        f.write_bytes(b"\xff\xfe\x00\x01\x80")

        result = _read_file_content(str(f))
        assert result == str(f)

    def test_missing_file_returns_path(self, tmp_path):
        missing = tmp_path / "does_not_exist.txt"
        # OSError path: _read_file_content swallows it and returns the path.
        assert _read_file_content(str(missing)) == str(missing)


class TestConfigureContainerRunner:
    def test_docker(self):
        ctx = RuntimeContext()
        configure_container_runner(ctx, "docker")
        assert ctx.default_container == "docker"
        assert ctx.singularity is False
        assert ctx.podman is False

    def test_podman(self):
        ctx = RuntimeContext()
        configure_container_runner(ctx, "podman")
        assert ctx.default_container == "podman"
        assert ctx.podman is True
        assert ctx.singularity is False

    def test_singularity(self):
        ctx = RuntimeContext()
        configure_container_runner(ctx, "singularity")
        assert ctx.default_container == "singularity"
        assert ctx.singularity is True
        assert ctx.podman is False

    def test_other_runner(self):
        ctx = RuntimeContext()
        configure_container_runner(ctx, "udocker")
        assert ctx.default_container == "udocker"
        assert ctx.singularity is False
        assert ctx.podman is False


class TestRunToolFileNormalization:
    """Unit-test the file-coercion branch inside ``run_tool`` without invoking
    any real CWL tool: we stub out the CWL ``tool`` object with just enough
    surface area for the function to route through its normalization code.
    """

    def _make_stub_tool(self, inputs_schema):
        captured = {}

        class _Inner:
            inputs_record_schema = {"fields": inputs_schema}

        class _Stub:
            t = _Inner()

            def __call__(self, **kwargs):
                captured["kwargs"] = kwargs
                # Return an empty output map – outputs list below is empty.
                return {}

        return _Stub(), captured

    def test_single_file_path_becomes_file_object(self, tmp_path):
        f = tmp_path / "input.txt"
        f.write_text("x")

        tool, captured = self._make_stub_tool([
            {"name": "input_file", "type": "File"},
        ])

        outs = tool_logic.run_tool(
            tool,
            {"input_file": str(f)},
            outputs=[],
        )

        assert outs == {}
        file_obj = captured["kwargs"]["input_file"]
        assert isinstance(file_obj, dict)
        assert file_obj["class"] == "File"
        assert file_obj["location"].startswith("file://")
        assert Path(urlparse(file_obj["location"]).path) == f.resolve()

    def test_remote_uri_kept_as_string(self):
        tool, captured = self._make_stub_tool([
            {"name": "input_file", "type": ["null", "File"]},
        ])

        url = "https://example.com/data.txt"
        tool_logic.run_tool(
            tool,
            {"input_file": url},
            outputs=[],
        )

        assert captured["kwargs"]["input_file"] == url

    def test_file_array_of_paths(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("a")
        f2.write_text("b")

        tool, captured = self._make_stub_tool([
            {
                "name": "inputs",
                "type": {"type": "array", "items": "File"},
            },
        ])

        tool_logic.run_tool(
            tool,
            {"inputs": [str(f1), str(f2)]},
            outputs=[],
        )

        arr = captured["kwargs"]["inputs"]
        assert isinstance(arr, list) and len(arr) == 2
        for item, original in zip(arr, [f1, f2]):
            assert item["class"] == "File"
            assert Path(urlparse(item["location"]).path) == original.resolve()

    def test_non_file_param_passed_through(self):
        tool, captured = self._make_stub_tool([
            {"name": "threshold", "type": "float"},
            {"name": "label", "type": "string"},
        ])

        tool_logic.run_tool(
            tool,
            {"threshold": 0.5, "label": "hello"},
            outputs=[],
        )

        assert captured["kwargs"]["threshold"] == 0.5
        assert captured["kwargs"]["label"] == "hello"

    def test_none_param_is_skipped(self):
        tool, captured = self._make_stub_tool([
            {"name": "input_file", "type": ["null", "File"]},
        ])

        tool_logic.run_tool(
            tool,
            {"input_file": None},
            outputs=[],
        )

        # None stays None; no File wrapping.
        assert captured["kwargs"]["input_file"] is None

    def test_single_directory_path_becomes_directory_object(self, tmp_path):
        tool, captured = self._make_stub_tool([
            {"name": "db_dir", "type": ["null", "Directory"]},
        ])

        tool_logic.run_tool(
            tool,
            {"db_dir": str(tmp_path)},
            outputs=[],
        )

        dir_obj = captured["kwargs"]["db_dir"]
        assert isinstance(dir_obj, dict)
        assert dir_obj["class"] == "Directory"
        assert dir_obj["location"].startswith("file://")
        assert Path(urlparse(dir_obj["location"]).path) == tmp_path.resolve()

    def test_directory_array_of_paths(self, tmp_path):
        d1 = tmp_path / "db1"
        d2 = tmp_path / "db2"
        d1.mkdir()
        d2.mkdir()

        tool, captured = self._make_stub_tool([
            {
                "name": "db_dirs",
                "type": {"type": "array", "items": "Directory"},
            },
        ])

        tool_logic.run_tool(
            tool,
            {"db_dirs": [str(d1), str(d2)]},
            outputs=[],
        )

        arr = captured["kwargs"]["db_dirs"]
        assert isinstance(arr, list) and len(arr) == 2
        for item, original in zip(arr, [d1, d2]):
            assert item["class"] == "Directory"
            assert Path(urlparse(item["location"]).path) == original.resolve()
