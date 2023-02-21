from typing import List, Union

from geojson_pydantic import (Feature, GeometryCollection, LineString, MultiLineString, MultiPoint,
                              MultiPolygon, Point, Polygon)
from pydantic import BaseModel, validator


class GeoJSON(BaseModel):
    geometry: Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon, GeometryCollection]
    properties: dict = {}

    @validator('geometry')
    def validate_geometry(cls, v):
        if not isinstance(v, (Point, MultiPoint, LineString, MultiLineString, Polygon,
                              MultiPolygon, GeometryCollection)):
            raise ValueError("Invalid GeoJSON geometry")
        return v


class GeoJSONFeatureCollection(BaseModel):
    type: str
    features: List[Feature]

    @validator('type')
    def validate_type(cls, v):
        if v != "FeatureCollection":
            raise ValueError("Invalid GeoJSON type")
        return v

    @validator('features')
    def validate_features(cls, v):
        if not isinstance(v, list) or not v:
            raise ValueError("Invalid GeoJSON features")
        for feature in v:
            if not isinstance(feature, Feature):
                raise ValueError("Invalid GeoJSON feature")
            if "name" not in feature.properties:
                raise ValueError("Invalid GeoJSON feature properties, name is missing")
        return v
