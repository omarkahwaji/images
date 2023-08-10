"""
This module provides a FastAPI application to handle image data processing and database operations.
It includes startup event to clean and load image data into the database,
endpoints to fetch image data based on depth range, and exception handlers for database errors.
"""

import base64
import logging

import pandas as pd
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from exceptions.exceptions import (
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseCreationError,
    DatabaseServiceError,
    ColorMapError,
)
from models.models import (
    ImageDepthRangeResponse,
    ImageDepthRangeRequest,
    DataFrameRequest,
    ImageDataFrameResponse,
)
from services.database import DatabaseService
from services.image_processing import ImageProcessingService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

app = FastAPI()


@app.on_event("startup")
async def startup_event() -> None:
    """
    This function is executed at the startup of the FastAPI application.
    It cleans the image data and loads it into the database.
    """
    input_file_path = "image/img.csv"
    data_cleaner = ImageProcessingService(input_file_path)
    cleaned_data: pd.DataFrame = data_cleaner.clean_data()

    image_depth_identifier = cleaned_data["depth"]
    cleaned_data = cleaned_data.drop(columns=["depth"])

    image = data_cleaner.dataframe_to_image(cleaned_data)

    resized_image = data_cleaner.resize_image(image, new_width=150)
    resized_data = data_cleaner.image_to_dataframe(resized_image)

    resized_data["depth"] = image_depth_identifier
    resized_data["image_name"] = "test_image"
    database_service = DatabaseService()
    database_service.insert_data(table_name="images", dataframe=resized_data)
    logger.info("Startup complete.! Image loaded to database successfully.")


@app.get("/image-depth-range", response_model=ImageDepthRangeResponse)
async def get_image_data(request: ImageDepthRangeRequest) -> ImageDepthRangeResponse:
    """
    This endpoint fetches image data from the database based on the depth range and colormap provided in the request.
    """
    database_service = DatabaseService()
    logger.info("Fetching image data from database...")
    image = database_service.get_image_data(
        depth_min=request.depth_min,
        depth_max=request.depth_max,
        colormap=request.colormap,
        image_name=request.image_name,
    )

    # Encoding the image data in base64
    encoded_image = base64.b64encode(image.tobytes()).decode("utf-8")

    return ImageDepthRangeResponse(image=encoded_image)


@app.post("/upload-image", response_model=ImageDataFrameResponse)
async def upload_image(request: DataFrameRequest) -> ImageDataFrameResponse:
    try:
        # Convert the request data into a DataFrame
        df = pd.DataFrame(request.data)

        # Convert the entire dataframe data into an image
        image = ImageProcessingService.dataframe_to_image(df)

        # Resize the image
        resized_image = ImageProcessingService.resize_image(image, new_width=150)

        # Convert the resized image back to a dataframe
        resized_data_df = ImageProcessingService.image_to_dataframe(resized_image)

        # Assign the image name and depth (taken from the first row as they are consistent)
        resized_data_df["image_name"] = df["image_name"][0]
        resized_data_df["depth"] = df["depth"][0]

        # Store the resized image data in the database
        database_service = DatabaseService()
        database_service.insert_data(table_name="images", dataframe=resized_data_df)

        return ImageDataFrameResponse(
            message="Data uploaded and stored successfully.", success=True
        )
    except Exception as e:
        logger.error(f"Error occurred while uploading dataframe data: {e}")
        return ImageDataFrameResponse(message=f"Error occurred: {e}", success=False)


@app.get("/", response_class=JSONResponse)
async def root() -> JSONResponse:
    """
    This endpoint returns a simple greeting message.
    """
    return JSONResponse(status_code=200, content={"message": "Hello, world!"})


@app.get("/health", response_class=JSONResponse)
async def health_check() -> JSONResponse:
    """
    This endpoint checks the health status of the application.
    """
    return JSONResponse(status_code=200, content={"status": "OK"})


@app.exception_handler(DatabaseConnectionError)
async def database_connection_error_handler(
    request: Request, exc: DatabaseConnectionError
) -> JSONResponse:
    """
    This function handles DatabaseConnectionError exceptions.
    """
    return JSONResponse(
        status_code=500,
        content={
            "message": f"An error occurred while connecting to the database.{exc}"
        },
    )


@app.exception_handler(DatabaseQueryError)
async def database_query_error_handler(
    request: Request, exc: DatabaseQueryError
) -> JSONResponse:
    """
    This function handles DatabaseQueryError exceptions.
    """
    return JSONResponse(
        status_code=400,
        content={"message": f"An error occurred while querying the database. {exc}"},
    )


@app.exception_handler(DatabaseConnectionError)
async def database_connection_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    This function handles general database connection exceptions.
    """
    return JSONResponse(
        status_code=500,
        content={"message": f"Failed to connect database. {exc}."},
    )


@app.exception_handler(DatabaseCreationError)
async def database_creation_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    This function handles DatabaseCreationError exceptions.
    """
    return JSONResponse(
        status_code=500,
        content={"message": f"Failed to create database and tables. {exc}."},
    )


@app.exception_handler(DatabaseServiceError)
async def database_creation_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    This function handles DatabaseServiceError exceptions.
    """
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal database error. {exc}."},
    )


@app.exception_handler(ColorMapError)
async def database_creation_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    This function handles ColorMapError exceptions.
    """
    return JSONResponse(
        status_code=400,
        content={"message": f"Invalid colormap. {exc}."},
    )
