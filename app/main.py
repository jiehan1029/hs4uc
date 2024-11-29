from fastapi import FastAPI
from app.analyze_data import by_campus_rate, by_school_rate

app = FastAPI()


@app.get("/health")
def health_check():
    return {"Hello": "World"}


@app.get("/analyze")
def analyze_data(
    by: str = "school",
    select_campus: str = "all",
    select_year: str = "all",
    select_school_type: str = "all",
):
    if by == "campus":
        return by_campus_rate()
    if by == "school":
        return by_school_rate(
            select_campus=select_campus,
            select_year=select_year,
            select_school_type=select_school_type,
        )

    return "use ?by=campus or ?by=school"
