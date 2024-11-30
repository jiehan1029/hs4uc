from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.analyze_data import by_campus_rate, by_school_rate

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"Hello": "World"}


@app.get("/analyze")
def analyze_data(
    by: str = "school",
    select_campus: str = "all",
    select_year: str = "all",
    select_school_type: str = "all",
    page: int = 1,
    page_size: int = 10,
):
    if by == "campus":
        return by_campus_rate()

    return by_school_rate(
        select_campus=select_campus,
        select_year=select_year,
        select_school_type=select_school_type,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
