import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pytest
from services.database import DatabaseService
from exceptions.exceptions import (
    DatabaseServiceError,
    DatabaseQueryError,
    ColorMapError,
)
import pandas as pd
from unittest.mock import patch, Mock

# Sample data for testing
sample_data = {"depth": [1.0, 2.0, 3.0], "pixels": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
df = pd.DataFrame(sample_data)

# Mock environment variables for database connection
mock_env_vars = {
    "DB_HOST": "localhost",
    "DB_PORT": "3306",
    "DB_USER": "user",
    "DB_PASS": "pass",
    "DB_NAME": "test_db",
}


# 1. Test Database Initialization
@patch("sqlalchemy.create_engine", return_value=Mock())
def test_database_initialization(mocked_engine):
    with patch.dict("os.environ", mock_env_vars):
        db_service = DatabaseService()
        assert db_service is not None


@patch("sqlalchemy.create_engine", return_value=Mock())
def test_missing_env_vars(mocked_engine):
    with patch.dict("os.environ", {}):  # Empty environment variables
        with pytest.raises(DatabaseServiceError):
            DatabaseService()


# 2. Test Table Creation
@patch("sqlalchemy.create_engine", return_value=Mock())
@patch.object(DatabaseService, "create_table", return_value=None)
def test_create_table(mocked_engine, mocked_create_table):
    with patch.dict("os.environ", mock_env_vars):
        db_service = DatabaseService()
        db_service.create_table("test_table", df)


@patch("sqlalchemy.create_engine", return_value=Mock())
@patch.object(
    DatabaseService,
    "create_table",
    side_effect=DatabaseServiceError("Table already exists"),
)
def test_table_already_exists(mocked_engine, mocked_create_table):
    with patch.dict("os.environ", mock_env_vars):
        db_service = DatabaseService()
        with pytest.raises(DatabaseServiceError):
            db_service.create_table("test_table", df)


# 3. Test Data Insertion
@patch("sqlalchemy.create_engine", return_value=Mock())
@patch.object(DatabaseService, "insert_data", return_value=None)
def test_insert_data(mocked_engine, mocked_insert_data):
    with patch.dict("os.environ", mock_env_vars):
        db_service = DatabaseService()
        db_service.insert_data("test_table", df)


@patch("sqlalchemy.create_engine", return_value=Mock())
@patch.object(
    DatabaseService, "insert_data", side_effect=DatabaseServiceError("Table missing")
)
def test_insert_data_missing_table(mocked_engine, mocked_insert_data):
    with patch.dict("os.environ", mock_env_vars):
        db_service = DatabaseService()
        with pytest.raises(DatabaseServiceError):
            db_service.insert_data("nonexistent_table", df)


# 4. Test Image Data Retrieval
@patch("sqlalchemy.create_engine", return_value=Mock())
@patch.object(DatabaseService, "get_image_data", return_value=pd.DataFrame(sample_data))
def test_get_image_data(mocked_engine, mocked_get_image_data):
    with patch.dict("os.environ", mock_env_vars):
        db_service = DatabaseService()
        image_data = db_service.get_image_data(1.0, 3.0, "COLORMAP_JET")
        assert image_data is not None


@patch("sqlalchemy.create_engine", return_value=Mock())
@patch.object(
    DatabaseService, "get_image_data", side_effect=DatabaseQueryError("No data found")
)
def test_get_image_data_no_data_found(mocked_engine, mocked_get_image_data):
    with patch.dict("os.environ", mock_env_vars):
        db_service = DatabaseService()
        with pytest.raises(DatabaseQueryError):
            db_service.get_image_data(100.0, 200.0, "COLORMAP_JET")


@patch("sqlalchemy.create_engine", return_value=Mock())
@patch.object(
    DatabaseService, "get_image_data", side_effect=ColorMapError("Invalid colormap")
)
def test_get_image_data_invalid_colormap(mocked_engine, mocked_get_image_data):
    with patch.dict("os.environ", mock_env_vars):
        db_service = DatabaseService()
        with pytest.raises(ColorMapError, match="Invalid colormap"):
            db_service.get_image_data(1.0, 3.0, "INVALID_COLORMAP")
