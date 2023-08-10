"""Image related module."""
import numpy as np
import pandas as pd
from PIL import Image

from exceptions.exceptions import DataCleanerError


class ImageProcessingService:
    """Class to perform image processing tasks."""
    def __init__(self, file_path: str):
        """
        Initialize a new instance of the DataCleaner class.

        Args:
            file_path (str): The path to the input file.
        """
        self.file_path = file_path

    def clean_data(self) -> pd.DataFrame:
        """
        Read data from a CSV file, drop rows with missing data, and return the cleaned DataFrame.

        Returns:
            pd.DataFrame: The cleaned DataFrame.

        Raises:
            DataCleanerError: If an error occurs while reading the file, parsing the CSV, or cleaning the data.
        """
        try:
            image_data = pd.read_csv(self.file_path)
        except FileNotFoundError as exc:
            raise DataCleanerError(
                "The file specified in file_path does not exist."
            ) from exc
        except pd.errors.ParserError as exc:
            raise DataCleanerError(
                "Invalid pixel value encountered while parsing the CSV file."
            ) from exc
        except Exception as exc:
            raise DataCleanerError(
                "Non-finite value encountered while cleaning the data."
            ) from exc

        image_data = image_data.dropna()

        return image_data

    @staticmethod
    def dataframe_to_image(data: pd.DataFrame) -> Image.Image:
        """
        Convert a DataFrame to an image.

        Args:
            data (pd.DataFrame): The input DataFrame.

        Returns:
            PIL.Image.Image: The output image.

        Raises:
            DataCleanerError: If an error occurs while converting the DataFrame to an image.
        """
        try:
            # Defensive programming: Drop the depth column if it exists
            if "depth" in data.columns:
                data = data.drop(columns=["depth", "image_name"], axis=1)

            # Convert the DataFrame values directly into an image
            image = Image.fromarray(np.uint8(data.values))
        except ValueError as exc:
            raise DataCleanerError(
                f"Invalid pixel value encountered while converting DataFrame to image.{exc}"
            ) from exc
        except Exception as exc:
            raise DataCleanerError(
                f"An error occurred while processing the image. {exc}"
            ) from exc

        return image

    @staticmethod
    def resize_image(image: Image.Image, new_width: int) -> Image.Image:
        """
        Resize an image to a new width while maintaining the aspect ratio.

        Args:
            image (PIL.Image.Image): The original image.
            new_width (int): The new width.

        Returns:
            PIL.Image.Image: The resized image.

        Raises:
            DataCleanerError: If an error occurs while resizing the image.
        """
        try:
            (original_width, original_height) = image.size
            new_height = int(new_width * original_height / original_width)
            image.thumbnail((new_width, new_height))
        except Exception as exc:
            raise DataCleanerError("An error occurred while resizing the image.") from exc

        return image

    @staticmethod
    def image_to_dataframe(image: Image.Image) -> pd.DataFrame:
        """
        Convert an image back to a DataFrame.

        Args:
            image (PIL.Image.Image): The input image.

        Returns:
            pd.DataFrame: The output DataFrame.

        Raises:
            DataCleanerError: If an error occurs while converting the image to a DataFrame.
        """
        try:
            image_array = np.array(image)

            # Check if the image is 3D (like RGB)
            if len(image_array.shape) == 3:
                # Flatten each row of pixels into a single row for the DataFrame
                height, width, _ = image_array.shape
                flattened_array = image_array.reshape(height, width * 3)
                data = pd.DataFrame(flattened_array)
            else:
                # Directly convert 2D image array to DataFrame
                data = pd.DataFrame(image_array)
        except Exception as exc:
            raise DataCleanerError(
                f"An error occurred while converting the image to a DataFrame. {exc}"
            ) from exc

        return data
