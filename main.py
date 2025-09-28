# main.py  — Mineral Water (Maden Suyu) Products API (MVP)
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Literal, List
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Soda Analiz - Mineral Water API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ---- Veri Modeli ----
class Composition(BaseModel):
    # Tüm birimler mg/L (pH birimsiz)
    na: Optional[float] = None       # Sodyum
    k: Optional[float] = None        # Potasyum
    ca: Optional[float] = None       # Kalsiyum
    mg: Optional[float] = None       # Magnezyum
    hco3: Optional[float] = None     # Bikarbonat
    so4: Optional[float] = None      # Sülfat
    cl: Optional[float] = None       # Klorür
    no3: Optional[float] = None      # Nitrat
    f: Optional[float] = None        # Florür
    tds: Optional[float] = None      # Toplam Çözünmüş Madde
    ph: Optional[float] = None       # pH (0-14)

class Product(BaseModel):
    id: str
    name: str                        # Ürün adı (etiketteki)
    brand: str                       # Marka (Beypazarı, Akmina, Kızılay, Uludağ...)
    source: Optional[str] = None     # Kaynak/şişeleme noktası (örn. "Erzincan")
    volumeMl: Optional[int] = None   # Şişe hacmi (ml)
    packSize: Optional[int] = None   # Paket adedi (ör. 6'lı)
    carbonated: Optional[bool] = True  # Doğal CO2/karbonlu mu
    composition: Composition
    imageUrl: Optional[str] = None
    isActive: bool = True
    createdAt: str
    updatedAt: str

# ---- MOCK Ürünler (gerçek etiketlerle DEĞİŞTİRİLECEK) ----
# NOT: Aşağıdaki değerler yalnızca geliştirici testleri içindir.
PRODUCTS: List[Product] = [
    Product(
        id="beypazari-200-6",
        name="Doğal Maden Suyu 200ml (6'lı)",
        brand="Beypazarı",
        source="Beypazarı / Ankara",
        volumeMl=200, packSize=6, carbonated=True,
        composition=Composition(
            na=350.0, k=30.0, ca=100.0, mg=60.0, hco3=1800.0,
            so4=120.0, cl=80.0, no3=2.0, f=0.8, tds=2300.0, ph=6.3
        ),
        imageUrl=None, isActive=True,
        createdAt="2025-09-24T10:00:00Z", updatedAt="2025-09-27T18:00:00Z",
    ),
    Product(
        id="akmina-200-6",
        name="Doğal Maden Suyu 200ml (6'lı)",
        brand="Akmina",
        source="Afyon",
        volumeMl=200, packSize=6, carbonated=True,
        composition=Composition(
            na=20.0, k=5.0, ca=60.0, mg=25.0, hco3=450.0,
            so4=40.0, cl=15.0, no3=1.0, f=0.2, tds=700.0, ph=7.2
        ),
        imageUrl=None, isActive=True,
        createdAt="2025-09-23T09:00:00Z", updatedAt="2025-09-27T18:00:00Z",
    ),
    Product(
        id="kizilay-erzincan-200-6",
        name="Erzincan Doğal Maden Suyu 200ml (6'lı)",
        brand="Kızılay",
        source="Erzincan",
        volumeMl=200, packSize=6, carbonated=True,
        composition=Composition(
            na=10.0, k=2.0, ca=220.0, mg=65.0, hco3=1800.0,
            so4=35.0, cl=10.0, no3=0.5, f=0.1, tds=2200.0, ph=6.5
        ),
        imageUrl=None, isActive=True,
        createdAt="2025-09-20T12:00:00Z", updatedAt="2025-09-26T15:45:10Z",
    ),
    Product(
        id="uludag-200-6",
        name="Uludağ Doğal Maden Suyu 200ml (6'lı)",
        brand="Uludağ",
        source="Bursa",
        volumeMl=200, packSize=6, carbonated=True,
        composition=Composition(
            na=30.0, k=4.0, ca=80.0, mg=35.0, hco3=600.0,
            so4=50.0, cl=20.0, no3=1.0, f=0.3, tds=900.0, ph=6.9
        ),
        imageUrl=None, isActive=True,
        createdAt="2025-09-22T10:00:00Z", updatedAt="2025-09-22T10:00:00Z",
    ),
    Product(
        id="sirma-200-6",
        name="Sırma Doğal Maden Suyu 200ml (6'lı)",
        brand="Sırma",
        source="Sakarya",
        volumeMl=200, packSize=6, carbonated=True,
        composition=Composition(
            na=8.0, k=1.5, ca=50.0, mg=20.0, hco3=400.0,
            so4=20.0, cl=8.0, no3=0.8, f=0.1, tds=600.0, ph=7.4
        ),
        imageUrl=None, isActive=True,
        createdAt="2025-09-10T08:00:00Z", updatedAt="2025-09-20T08:00:00Z",
    ),
]

# Sıralama için izinli kolonlar
ALLOWED_SORT = {"brand", "name", "composition.na", "composition.mg", "composition.ca", "composition.hco3", "composition.tds", "composition.ph"}

# PROFIL ÖN AYARLAR (DEMO) — Gerektiğinde konfigürasyona taşınır
# Not: Sağlık tavsiyesi değildir; uygulama içinde doktor onayı uyarısı koyacağız.
PROFILE_FILTERS = {
    "sodiumRestricted": {"maxNa": 20.0},          # Düşük sodyum örneği
    "bicarbonateRich": {"minHCO3": 600.0},        # Bikarbonatı yüksek
    "magnesiumRich": {"minMg": 50.0},             # Mg göreceli yüksek
    "calciumRich": {"minCa": 150.0},              # Ca göreceli yüksek
    "lowNitrate": {"maxNO3": 10.0},               # Nitrat düşük
}

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}

@app.get("/products")
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    q: Optional[str] = Query(None, description="Ad/marka arama"),
    brand: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    carbonated: Optional[bool] = Query(None),

    # Kompozisyon filtreleri (mg/L ve pH)
    minNa: Optional[float] = Query(None), maxNa: Optional[float] = Query(None),
    minK: Optional[float] = Query(None),  maxK: Optional[float] = Query(None),
    minCa: Optional[float] = Query(None), maxCa: Optional[float] = Query(None),
    minMg: Optional[float] = Query(None), maxMg: Optional[float] = Query(None),
    minHCO3: Optional[float] = Query(None), maxHCO3: Optional[float] = Query(None),
    minSO4: Optional[float] = Query(None), maxSO4: Optional[float] = Query(None),
    minCL: Optional[float] = Query(None),  maxCL: Optional[float] = Query(None),
    minNO3: Optional[float] = Query(None), maxNO3: Optional[float] = Query(None),
    minF: Optional[float] = Query(None),   maxF: Optional[float] = Query(None),
    minTDS: Optional[float] = Query(None), maxTDS: Optional[float] = Query(None),
    minPH: Optional[float] = Query(None),  maxPH: Optional[float] = Query(None),

    profile: Optional[Literal["sodiumRestricted","bicarbonateRich","magnesiumRich","calciumRich","lowNitrate"]] = Query(None),
    sort_by: str = Query("brand", alias="sortBy"),
    sort_dir: Literal["asc", "desc"] = Query("asc", alias="sortDir"),
):
    # Profil geldiyse ilgili eşikleri uygula (kullanıcı sınırlarla override edebilir)
    if profile:
        preset = PROFILE_FILTERS.get(profile, {})
        for k, v in preset.items():
            if locals().get(k) is None:
                locals()[k] = v  # type: ignore

    # Aralıkların tutarlılığı
    def check_range(lo, hi, name):
        if lo is not None and hi is not None and lo > hi:
            raise HTTPException(status_code=400, detail={"code":"INVALID_RANGE","message":f"{name} min cannot exceed max","field":name})
    check_range(minNa, maxNa, "Na"); check_range(minK, maxK, "K")
    check_range(minCa, maxCa, "Ca"); check_range(minMg, maxMg, "Mg")
    check_range(minHCO3, maxHCO3, "HCO3"); check_range(minSO4, maxSO4, "SO4")
    check_range(minCL, maxCL, "CL"); check_range(minNO3, maxNO3, "NO3")
    check_range(minF, maxF, "F"); check_range(minTDS, maxTDS, "TDS")
    check_range(minPH, maxPH, "PH")

    items = PRODUCTS.copy()

    # Basit arama
    if q:
        ql = q.lower()
        items = [p for p in items if ql in p.name.lower() or ql in p.brand.lower() or (p.source and ql in p.source.lower())]

    # Eşitlik filtreleri
    if brand:
        items = [p for p in items if p.brand.lower() == brand.lower()]
    if source:
        items = [p for p in items if p.source and p.source.lower() == source.lower()]
    if carbonated is not None:
        items = [p for p in items if p.carbonated == carbonated]

    # Kompozisyon filtreleri (None değerleri atlanır)
    def within(val: Optional[float], lo: Optional[float], hi: Optional[float]) -> bool:
        if val is None: 
            return False  # analiz yoksa ele
        if lo is not None and val < lo: 
            return False
        if hi is not None and val > hi: 
            return False
        return True

    def filt(p: Product) -> bool:
        c = p.composition
        return all([
            within(c.na,  minNa,  maxNa),
            within(c.k,   minK,   maxK),
            within(c.ca,  minCa,  maxCa),
            within(c.mg,  minMg,  maxMg),
            within(c.hco3,minHCO3,maxHCO3),
            within(c.so4, minSO4, maxSO4),
            within(c.cl,  minCL,  maxCL),
            within(c.no3, minNO3, maxNO3),
            within(c.f,   minF,   maxF),
            within(c.tds, minTDS, maxTDS),
            within(c.ph,  minPH,  maxPH),
        ])

    # Kompozisyon parametresi gelmediyse hepsini geçir, geldiyse filtre uygula
    any_comp_param = any(v is not None for v in [minNa,maxNa,minK,maxK,minCa,maxCa,minMg,maxMg,minHCO3,maxHCO3,minSO4,maxSO4,minCL,maxCL,minNO3,maxNO3,minF,maxF,minTDS,maxTDS,minPH,maxPH])
    if any_comp_param or profile:
        items = [p for p in items if filt(p)]

    # Sıralama
    if sort_by not in ALLOWED_SORT:
        raise HTTPException(status_code=400, detail={"code":"INVALID_PARAM","message":"sortBy must be one of: " + ", ".join(sorted(ALLOWED_SORT)), "field":"sortBy"})
    reverse = sort_dir == "desc"

    def sort_key(p: Product):
        if sort_by.startswith("composition."):
            field = sort_by.split(".",1)[1]
            val = getattr(p.composition, field, None)
            # None'ları sona at
            return (val is None, val)
        return getattr(p, sort_by, None)
    items.sort(key=sort_key, reverse=reverse)

    # Sayfalama
    total_items = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = items[start:end]
    total_pages = (total_items + page_size - 1) // page_size

    return {
        "items": [p.dict() for p in page_items],
        "pagination": {"page": page, "pageSize": page_size, "totalItems": total_items, "totalPages": total_pages},
        "sort": {"by": sort_by, "dir": sort_dir},
        "filters": {
            "q": q, "brand": brand, "source": source, "carbonated": carbonated,
            "profile": profile,
            "minNa": minNa, "maxNa": maxNa, "minK": minK, "maxK": maxK,
            "minCa": minCa, "maxCa": maxCa, "minMg": minMg, "maxMg": maxMg,
            "minHCO3": minHCO3, "maxHCO3": maxHCO3, "minSO4": minSO4, "maxSO4": maxSO4,
            "minCL": minCL, "maxCL": maxCL, "minNO3": minNO3, "maxNO3": maxNO3,
            "minF": minF, "maxF": maxF, "minTDS": minTDS, "maxTDS": maxTDS,
            "minPH": minPH, "maxPH": maxPH,
        },
    }

@app.get("/products/{product_id}")
def get_product(product_id: str):
    for p in PRODUCTS:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="product not found")

@app.get("/profiles")
def get_profiles():
    """
    Müşteri profilleri için hazır eşikler (mg/L). FE bu listeyi seçenek olarak gösterebilir.
    """
    return {
        "profiles": [
            {
                "key": "sodiumRestricted",
                "label": "Düşük Sodyum",
                "criteria": {"maxNa": 20.0},
                "note": "Hipertansiyon vb. için düşük Na tercih edilir. (Tıbbi tavsiye değildir.)"
            },
            {
                "key": "bicarbonateRich",
                "label": "Bikarbonatı Yüksek",
                "criteria": {"minHCO3": 600.0},
                "note": "Sindirim ve mide için tercih edilebilir. (Tıbbi tavsiye değildir.)"
            },
            {
                "key": "magnesiumRich",
                "label": "Magnezyumu Yüksek",
                "criteria": {"minMg": 50.0},
                "note": "Mg alımı odaklı seçim. (Tıbbi tavsiye değildir.)"
            },
            {
                "key": "calciumRich",
                "label": "Kalsiyumu Yüksek",
                "criteria": {"minCa": 150.0},
                "note": "Ca alımı odaklı seçim. (Tıbbi tavsiye değildir.)"
            },
            {
                "key": "lowNitrate",
                "label": "Düşük Nitrat",
                "criteria": {"maxNO3": 10.0},
                "note": "Nitrat limitini düşük tutar. (Tıbbi tavsiye değildir.)"
            }
        ]
    }
