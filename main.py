from dotenv import load_dotenv

load_dotenv()

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
