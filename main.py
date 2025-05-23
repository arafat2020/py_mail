from fastapi import FastAPI
import uvicorn
from mail import mail
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(
    level=logging.INFO,  # Or DEBUG to see even more details
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)



def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("Py Mail running on port 8000")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(mail.router)

if __name__ == "__main__":
    main()
