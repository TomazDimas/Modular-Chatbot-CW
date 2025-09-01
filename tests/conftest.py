import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("REDIS_URL", "redis://localhost:6380/0")

from app.backend.main import app 

@pytest.fixture
def client():
    return TestClient(app)
