import uvicorn

if __name__ == "__main__":
    # Load environment variables from a .env file if present
    # Run the FastAPI application
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, log_level="info")
