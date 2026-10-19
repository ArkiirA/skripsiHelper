from fastapi import FastAPI

app = FastAPI(title="SkripsiHelper API", version="0.1.0")


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "SkripsiHelper API", "version": "0.1.0"}
