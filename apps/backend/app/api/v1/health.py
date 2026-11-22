from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness simples. Checagens de dependências (readiness) entram na Fase 1."""
    return {"status": "ok"}
