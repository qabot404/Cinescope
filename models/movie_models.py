from typing import Optional, List

from pydantic import BaseModel


class MovieResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    location: Optional[str] = None
    published: bool
    genreId: int


class MoviesListResponse:
    movies: List[MovieResponse]
    total: int
    count: Optional[int] = None
    page: Optional[int] = None
    pageSize: Optional[int] = None
    pageCount: Optional[int] = None
