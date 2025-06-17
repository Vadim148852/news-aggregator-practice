import sys
import os
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from backend.app import news_store, store
from config import STUDENT_ID

@pytest.fixture(autouse=True)
def clear_stores():
    news_store[STUDENT_ID] = []
    store[STUDENT_ID] = []
    yield
