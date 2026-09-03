import requests
import re
import os
import json
from datetime import datetime

TOPIC = os.environ["NTFY_TOPIC"]
STATE_FILE = "last_price.json"

# 1) Harem Altin sayfasini cek
url = "https://anlikaltinfiyatlari.com/altin/harem-altin"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
resp = requests.get(url, headers=headers, timeout=15)
html = resp.text

# "kapalicarsi/gram-altin" linkinin gectigi satirdaki alis/satis degerlerini bul
# Turkce "i/ı" karakter sorunu olmasin diye link adresine (URL) gore ariyoruz
match = re.search(
    r"kapalicarsi/gram-altin.{0,300}?(\d{3,5}\.\d{2}).{0,100}?(\d{3,5}\.\d{2})",
    html, re.S | re.I
)

if not match:
    requests.post(
        f"https://ntfy.sh/{TOPIC}",
        data="Fiyat okunamadi, site yapisi degismis olabilir.".encode("utf-8"),
        headers={"Title": "Altin Bot Hata"}
    )
    raise SystemExit("Parse edilemedi")

alis = float(match.group(1))
satis = float(match.group(2))

# 2) Onceki fiyati oku (varsa)
onceki = None
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        try:
            onceki = json.load(f).get("satis")
        except Exception:
            onceki = None

# 3) Trend hesapla
if onceki is not None:
    fark = satis - onceki
    if fark > 0:
        yon = f"Yukselis (+{fark:.2f} TL)"
    elif fark < 0:
        yon = f"Dusus ({fark:.2f} TL)"
    else:
        yon = "Degisim yok"
    trend_satir = f"\n{yon}\n30dk once satis: {onceki:.2f} TL"
else:
    trend_satir = "\n(Ilk olcum, henuz karsilastirma yok)"

mesaj = f"Harem Gram Altin\nAlis: {alis:.2f} TL\nSatis: {satis:.2f} TL{trend_satir}"

requests.post(
    f"https://ntfy.sh/{TOPIC}",
    data=mesaj.encode("utf-8"),
    headers={"Title": "Altin Fiyati"}
)

# 4) Yeni fiyati kaydet (bir sonraki calistirma icin)
with open(STATE_FILE, "w") as f:
    json.dump({"satis": satis, "alis": alis, "zaman": datetime.utcnow().isoformat()}, f)
