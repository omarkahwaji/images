import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
from services.image_processing import ImageProcessingService
from unittest.mock import patch
from PIL import Image
from exceptions.exceptions import DataCleanerError
import numpy as np


@pytest.fixture
def sample_data_df():
    data = {"depth": [100, 150, 200], "pixels": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
    return pd.DataFrame(data)


def test_clean_data(sample_data_df):
    with patch.object(pd, "read_csv", return_value=sample_data_df):
        cleaner = ImageProcessingService("sample_file.csv")
        df = cleaner.clean_data()
        assert not df.isnull().values.any()


@patch.object(pd, "read_csv", side_effect=FileNotFoundError)
def test_clean_data_file_not_found(mocked_read_csv):
    cleaner = ImageProcessingService("nonexistent_file.csv")
    with pytest.raises(DataCleanerError):
        cleaner.clean_data()


def test_dataframe_to_image():
    cleaner = ImageProcessingService("tests/large_sample_file.csv")
    df = cleaner.clean_data()
    image = cleaner.dataframe_to_image(df)
    assert isinstance(image, Image.Image)


def test_resize_image():
    cleaner = ImageProcessingService("sample_file.csv")
    original_image = Image.new("RGB", (100, 50))
    resized_image = cleaner.resize_image(original_image, 50)
    assert resized_image.size == (50, 25)


def test_image_to_dataframe():
    grayscale_data = np.random.randint(0, 256, size=(50, 150))
    grayscale_image = Image.fromarray(np.uint8(grayscale_data))

    df_grayscale = ImageProcessingService.image_to_dataframe(grayscale_image)
    assert df_grayscale.shape == grayscale_data.shape
    assert np.array_equal(df_grayscale.values, grayscale_data)

    rgb_data = np.random.randint(0, 256, size=(50, 150, 3))
    rgb_image = Image.fromarray(np.uint8(rgb_data))

    df_rgb = ImageProcessingService.image_to_dataframe(rgb_image)
    assert df_rgb.shape == (rgb_data.shape[0], rgb_data.shape[1] * rgb_data.shape[2])
    assert np.array_equal(df_rgb.values, rgb_data.reshape(rgb_data.shape[0], -1))
