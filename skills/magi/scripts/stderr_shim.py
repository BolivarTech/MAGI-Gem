from contextlib import contextmanager


@contextmanager
def _buffered_stderr_while(active: bool):
    # Dummy implementation for now to avoid missing imports
    yield
