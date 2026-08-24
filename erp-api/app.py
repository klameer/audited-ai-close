"""Codeless Ops demo API — one Cloud Run service, many demo datasets.

Each folder under datasets/ with a tools.py becomes a use case:
  MCP   /mcp/<dataset>/     (claude.ai custom connector, one per use case)
  REST  /v1/<dataset>/...   (curl-able twin, if the dataset defines a router)

A dataset's tools.py must expose `mcp` (a FastMCP with
settings.streamable_http_path = "/") and may expose `rest` (an APIRouter).

Auth: X-API-Key header or ?key= query on everything except /health.
Key resolution per dataset: env DEMO_API_KEY_<DATASET> (upper-snake) else
DEMO_API_KEY. If neither is set, auth is OFF (local dev only — Cloud Run
always sets a key). Read-only fictional data throughout; safe to leave up.
"""
import importlib.util
import os
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

DATASETS_DIR = Path(__file__).resolve().parent / "datasets"


def load_datasets() -> dict:
    datasets = {}
    for d in sorted(DATASETS_DIR.iterdir()):
        tools = d / "tools.py"
        if tools.exists():
            spec = importlib.util.spec_from_file_location(f"dataset_{d.name}", tools)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            datasets[d.name] = module
    return datasets


DATASETS = load_datasets()


def _dataset_key(dataset: str) -> str | None:
    env = f"DEMO_API_KEY_{dataset.upper().replace('-', '_')}"
    return os.environ.get(env) or os.environ.get("DEMO_API_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        for module in DATASETS.values():
            await stack.enter_async_context(module.mcp.session_manager.run())
        yield


app = FastAPI(title="Codeless Ops demo API", lifespan=lifespan)


@app.middleware("http")
async def require_key(request: Request, call_next):
    parts = request.url.path.strip("/").split("/")
    if parts[0] in ("mcp", "v1") and len(parts) > 1:
        key = _dataset_key(parts[1])
        if key:
            supplied = request.headers.get("x-api-key") or request.query_params.get("key")
            if supplied != key:
                return JSONResponse({"detail": "Missing or invalid API key"}, status_code=401)
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok", "service": "Codeless Ops demo API (mock, read-only)",
            "datasets": sorted(DATASETS)}


for name, module in DATASETS.items():
    app.mount(f"/mcp/{name}", module.mcp.streamable_http_app())
    if hasattr(module, "rest"):
        app.include_router(module.rest, prefix=f"/v1/{name}")
