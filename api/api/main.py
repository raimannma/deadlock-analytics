import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.requests import Request
from starlette.responses import RedirectResponse

from api.routers import v1

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Deadlock Analytics API",
    description="API for Deadlock analytics, including match, player, hero and item statistics.",
)

Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.include_router(v1.router)


@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    is_success = 200 <= response.status_code < 300
    is_docs = request.url.path.replace("/", "").startswith("docs")
    is_health = request.url.path.replace("/", "").startswith("health")
    if is_success and not is_docs and not is_health:
        response.headers["Cache-Control"] = "public, max-age=1200"
    return response


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse("/docs")


@app.get("/health", include_in_schema=False)
def get_health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
