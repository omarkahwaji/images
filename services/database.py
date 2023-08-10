"""Database related module."""
import os

import cv2
import numpy as np
import pandas as pd
from mysql.connector import Error as MySQLError
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import create_engine, Table, MetaData, Column
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Integer, Float, String
from sqlalchemy_utils import database_exists, create_database

from exceptions.exceptions import (
    DatabaseConnectionError,
    DatabaseServiceError,
    DatabaseQueryError,
    ColorMapError,
)


class DatabaseService:
    """Calss to perform database tasks."""

    def __init__(self):
        """
        Initialize a new instance of the DatabaseService class.
        """
        try:
            self._init_db()
        except MySQLError as exc:
            raise DatabaseConnectionError(
                "Failed to initialize database connection: {}".format(exc)
            ) from exc

    def _init_db(self):
        """
        Initialize the database connection.
        """
        try:
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT")
            db_user = os.getenv("DB_USER")
            db_pass = os.getenv("DB_PASS")
            db_name = os.getenv("DB_NAME")
            db_url = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
            self.engine = create_engine(db_url)
            self.sql_session = sessionmaker(bind=self.engine)
        except Exception as exc:
            raise DatabaseServiceError(
                "Missing environment variable(s) for database connection: {}".format(exc)
            ) from exc

    def create_table(self, table_name: str, dataframe: pd.DataFrame) -> None:
        """
        Create a table in the database.

        Args:
            table_name (str): The name of the table.
            dataframe (pd.DataFrame): The DataFrame based on which the table is to be created.
        """
        try:
            inspector = inspect(self.engine)
            if not inspector.has_table(table_name):
                if not database_exists(self.engine.url):
                    create_database(self.engine.url)

                metadata = MetaData()

                columns = []
                for column_name, dtype in dataframe.dtypes.items():
                    if "int64" in str(dtype):
                        columns.append(Column(column_name, Integer()))
                    elif "float64" in str(dtype):
                        columns.append(Column(column_name, Float()))  # type: ignore
                    elif "object" in str(dtype):
                        columns.append(Column(column_name, String(255)))  # type: ignore

                table = Table(  # pylint: disable=unused-variable
                    table_name, metadata, *columns, PrimaryKeyConstraint("image_name")
                )
                metadata.create_all(self.engine)
        except SQLAlchemyError as exc:
            raise DatabaseServiceError("Failed to create table: {}".format(exc)) from exc

    def insert_data(self, table_name: str, dataframe: pd.DataFrame):
        """
        Insert data into a table in the database.

        Args:
            table_name (str): The name of the table.
            dataframe (pd.DataFrame): The DataFrame to be inserted into the table.
        """
        try:
            dataframe.reset_index(drop=True, inplace=True)
            self.create_table(table_name, dataframe)
            dataframe.to_sql(table_name, self.engine, if_exists="replace", index=False)
        except SQLAlchemyError as exc:
            raise DatabaseServiceError("Failed to insert data: {}".format(exc)) from exc

    def get_image_data(
            self,
            depth_min: float,
            depth_max: float,
            colormap: str,
            image_name: str,
            table_name: str = "images",
    ) -> np.ndarray:
        """
        Get image data from the database based on a depth range and apply a colormap.

        Args:
            table_name (str): The name of the table.
            depth_min (int): The minimum depth.
            depth_max (int): The maximum depth.
            colormap (str): The colormap to be applied.
            image_name (str): The name of the image.

        Returns:
            np.ndarray: The image data.

        Raises:
            DatabaseServiceError: If an error occurs while getting the image data.
            ColorMapError: If an error occurs while applying the colormap.

        """
        try:
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=self.engine)
            with self.sql_session() as session:
                result = (
                    session.query(table)
                    .filter(
                        table.columns.depth.between(depth_min, depth_max),
                        table.columns.image_name == image_name,
                    )
                    .all()
                )
            dataframe = pd.DataFrame(result)

            if dataframe.empty:
                raise DatabaseQueryError(
                    "Failed to get image data: No data found for the provided depth range."
                )

            dataframe = dataframe.drop(columns=["depth", "image_name"])
            image = np.array(dataframe.values, dtype=np.uint8)
            image = cv2.applyColorMap(image, getattr(cv2, colormap.upper()))
            return image
        except SQLAlchemyError as exc:
            raise DatabaseServiceError("Failed to get image data: {}".format(exc)) from exc
        except AttributeError as exc:
            raise ColorMapError(
                "Failed to apply custom color mapping to the image: {}".format(exc)
            ) from exc
