# Shared pytest configuration for the coala test suite.
#
# `functioncall_test.py` is an example script (not a proper pytest module) that
# issues live calls to the Google Generative AI API at import time. Collecting
# it would hang the test run, so we explicitly skip it here.
collect_ignore = ["functioncall_test.py"]
