from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.db.database import Base, engine
from app.api import evaluations, goals, kpis, results, minthcm_proxy

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PerformTrack",
    description="Módulo de evaluación de desempeño para MintHCM",
    version="0.1.0",
)

app.include_router(evaluations.router, tags=["Evaluaciones"])
app.include_router(goals.router, tags=["OKRs / Objetivos"])
app.include_router(kpis.router, tags=["KPIs"])
app.include_router(results.router, tags=["Resultados"])
app.include_router(minthcm_proxy.router, tags=["MintHCM"])


@app.get("/")
def root():
    return {"app": "PerformTrack", "version": "0.1.0", "status": "running"}
