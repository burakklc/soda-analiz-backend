from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Geliştirme için CORS'u açıyoruz (web'de fetch yapabilmek için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # prod'da domainini yaz
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/hello")
def hello():
    return {"message": "Soda Analiz Backend çalışıyor 🚀"}
