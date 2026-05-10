from contextlib import contextmanager
from typing import Generator


@contextmanager
def _buffered_stderr_while(active: bool) -> Generator[None, None, None]:
    # Dummy implementation for now to avoid missing imports
    yield
