from fastapi import FastAPI
from app.analyze_data import by_campus_rate

app = FastAPI()


@app.get("/health")
def health_check():
    return {"Hello": "World"}


@app.get("/analyze")
def analyze_data():
    by_campus_results = by_campus_rate()
    return by_campus_results
