import pytest
from entrypoint_hook import EntrypointHook

@pytest.fixture
def hook():
    """
    Prepare & cleanup EntrypointHook for tests.
    Enable/disable entrypoint system calls.
    """
    test_hook = EntrypointHook()
    yield test_hook
    test_hook._reset_hooks()
