import requests
import os

TOPIC = os.environ["NTFY_TOPIC"]

data = requests.get("https://finans.truncgil.com/today.json").json()

gram_altin = data["gram-altin"]
alis = gram_altin["Alış"]
satis = gram_altin["Satış"]

mesaj = f"Gram Altın\nAlış: {alis} TL\nSatış: {satis} TL"

requests.post(
    f"https://ntfy.sh/{TOPIC}",
    data=mesaj.encode("utf-8"),
    headers={"Title": "Altin Fiyati"}
)
