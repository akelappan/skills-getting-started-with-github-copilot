"""Pytest configuration and fixtures for the activities API tests"""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from src.app import app, activities as original_activities


@pytest.fixture
def fresh_activities():
    """
    Provide a fresh copy of activities for each test.
    This ensures test isolation - changes in one test don't affect others.
    """
    return deepcopy(original_activities)


@pytest.fixture
def mock_app(fresh_activities, monkeypatch):
    """
    Create a test app instance with fresh activities data.
    Uses monkeypatch to replace the global activities dictionary.
    """
    monkeypatch.setattr("src.app.activities", fresh_activities)
    return app


@pytest.fixture
def client(mock_app):
    """
    Provide a TestClient for making requests to the API without starting a server.
    """
    return TestClient(mock_app)
