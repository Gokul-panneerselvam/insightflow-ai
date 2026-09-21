"""Convenience entry point for Insightflow AI backend."""

import uvicorn

from src.app.core.config import settings


def main():
    """Run the backend server."""
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
