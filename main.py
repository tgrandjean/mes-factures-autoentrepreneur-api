"""Entry point for the project."""
import uvicorn
from app.settings import DEBUG


if __name__ == "__main__":
    uvicorn.run("app:app",
                host="0.0.0.0",
                port=5000,
                log_level="info",
                reload=DEBUG)
