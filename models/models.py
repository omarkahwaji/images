from typing import List, Dict, Any

from pydantic import BaseModel


class ImageDataRow(BaseModel):
    depth: float
    pixels: List[float]


class ImageDepthRangeRequest(BaseModel):
    depth_min: float
    depth_max: float
    colormap: str = "COLORMAP_JET"
    image_name: str = "test_image"


class ImageDepthRangeResponse(BaseModel):
    image: str


class DataFrameRequest(BaseModel):
    data: Dict[str, List[Any]]


class ImageDataFrameResponse(BaseModel):
    message: str
