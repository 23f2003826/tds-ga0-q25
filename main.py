from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import pandas as pd
import numpy as np
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["*"],
)

DATA_FILE = Path.cwd() / "q-vercel-latency.json"

print("DATA_FILE =", DATA_FILE)
print("EXISTS =", DATA_FILE.exists())
df = pd.read_json(DATA_FILE)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.get("/")
def home():
    return "FastAPI is running"

@app.post("/")
def analyze(body: RequestBody):
    result = {}

    for region in body.regions:

        region_df = df[df["region"] == region]

        result[region] = {
            "avg_latency": float(region_df["latency_ms"].mean()),
            "p95_latency": float(
                np.percentile(region_df["latency_ms"], 95)
            ),
            "avg_uptime": float(region_df["uptime_pct"].mean()),
            "breaches": int(
                (region_df["latency_ms"] > body.threshold_ms).sum()
            ),
        }

    return result

@app.get("/hello")
def hello():
    return {"message": "Hello World"}