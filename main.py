from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # geliştirme için açık
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/hello")
def hello():
    return {"message": "Soda Analiz Backend çalışıyor 🚀"}

# --- yeni: mock ürün listesi
PRODUCTS = [
    {"id": 1, "brand": "Saka",     "name": "Doğal Maden Suyu", "na_mg_l": 80,  "mg_mg_l": 45},
    {"id": 2, "brand": "Kızılay",  "name": "Afyonkarahisar",   "na_mg_l": 20,  "mg_mg_l": 70},
    {"id": 3, "brand": "Beypazarı","name": "Soda",             "na_mg_l": 150, "mg_mg_l": 35},
]

@app.get("/products")
def products():
    return PRODUCTS
