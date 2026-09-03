from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.ready = True

    try:
        yield
    finally:
        app.state.ready = False



app = FastAPI(lifespan=lifespan)


app = FastAPI(
    title="Incentiv Recommendation System",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Report whether the application has completed startup."""
    status = "ok" if getattr(app.state, "ready", False) else "starting"
    return {"status": status}
