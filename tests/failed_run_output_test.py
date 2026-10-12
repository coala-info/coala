"""A failed CWL run reports what the tool printed to its captured streams.

cellranger-arc ``mkref`` printed "Invalid contig name encountered on GTF line 4: GL456210.1"
to standard output, which its CWL captures with ``stdout:``. cwltool's log then held only
"exited with status: 1", the MCP error said only "Completed permanentFail", and the caller
retried blind for three hours. These tests run real (container-free) CWL tools.
"""

from pathlib import Path

import pytest
from cwltool import factory
from cwltool.context import RuntimeContext
from cwltool.factory import WorkflowStatus

from coala.tool_logic import ToolRunFailed, _captured_stream_outputs, run_tool

_MESSAGE = "Invalid contig name encountered on GTF line 4: GL456210.1"


def _tool(tmp_path: Path, script: str, *, stdout: str | None = "tool.out",
          stderr: str | None = None, out_type: str = "stdout"):
    lines = [
        "cwlVersion: v1.2",
        "class: CommandLineTool",
        "baseCommand: [sh, -c]",
        f"arguments: [{script!r}]",
        "inputs: []",
        "outputs:",
        "  out:",
        f"    type: {out_type}",
    ]
    if out_type == "File":
        lines += ["    outputBinding:", "      glob: result.txt"]
    if stdout:
        lines.append(f"stdout: {stdout}")
    if stderr:
        lines.append(f"stderr: {stderr}")
    tmp_path.mkdir(parents=True, exist_ok=True)
    cwl = tmp_path / "tool.cwl"
    cwl.write_text("\n".join(lines) + "\n")
    rc = RuntimeContext()
    rc.outdir = str(tmp_path / "out")
    return factory.Factory(runtime_context=rc).make(str(cwl))


def _outputs(tool):
    return [{"name": "out", "type": "File"}]


def test_a_failed_run_carries_the_tools_own_stdout(tmp_path):
    tool = _tool(tmp_path, f"echo '{_MESSAGE}'; exit 1")
    with pytest.raises(ToolRunFailed) as err:
        run_tool(tool, {}, _outputs(tool), read_outs=True)
    text = str(err.value)
    assert text.startswith("Completed permanentFail.")
    assert _MESSAGE in text and "stdout (tool.out)" in text


def test_the_stdout_reaches_the_caller_even_without_read_outs(tmp_path):
    """``read_outs`` decides what a success returns; a failure always explains itself."""
    tool = _tool(tmp_path, f"echo '{_MESSAGE}'; exit 1")
    with pytest.raises(ToolRunFailed, match="GL456210.1"):
        run_tool(tool, {}, _outputs(tool), read_outs=False)


def test_a_captured_stderr_is_reported_too(tmp_path):
    tool = _tool(tmp_path, f"echo '{_MESSAGE}' 1>&2; exit 2", stdout=None,
                 stderr="tool.err", out_type="stderr")
    with pytest.raises(ToolRunFailed) as err:
        run_tool(tool, {}, _outputs(tool))
    assert "stderr (tool.err)" in str(err.value) and _MESSAGE in str(err.value)


def test_only_the_tail_of_a_long_log_is_kept(tmp_path):
    tool = _tool(tmp_path, f"seq 1 500; echo '{_MESSAGE}'; exit 1")
    with pytest.raises(ToolRunFailed) as err:
        run_tool(tool, {}, _outputs(tool))
    text = str(err.value)
    assert _MESSAGE in text
    assert "\n1\n" not in text and "500" in text


def test_a_failure_with_nothing_captured_is_reraised_unchanged(tmp_path):
    tool = _tool(tmp_path, "touch result.txt; exit 1", stdout=None, out_type="File")
    with pytest.raises(WorkflowStatus):
        run_tool(tool, {}, _outputs(tool))


def test_a_successful_run_is_unchanged(tmp_path):
    tool = _tool(tmp_path, "echo fine")
    out = run_tool(tool, {}, _outputs(tool), read_outs=True)
    assert out["out"] == "fine"


def test_stream_outputs_are_found_by_their_glob(tmp_path):
    tool = _tool(tmp_path, "echo hi")
    assert _captured_stream_outputs(tool) == {"out": "stdout"}
    plain = _tool(tmp_path / "plain", "touch result.txt", stdout=None, out_type="File")
    assert _captured_stream_outputs(plain) == {}
