from typing import Optional, List

from pydantic import BaseModel


class MovieResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    location: Optional[str] = None
    published: bool
    genreId: int


class MoviesListResponse(BaseModel):
    movies: List[MovieResponse]
    total: Optional[int] = None
    count: Optional[int] = None
    page: Optional[int] = None
    pageSize: Optional[int] = None
    pageCount: Optional[int] = None
