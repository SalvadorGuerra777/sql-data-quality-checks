import pytest

import dq


@pytest.fixture
def db():
    conn = dq.connect()
    yield conn
    conn.close()
