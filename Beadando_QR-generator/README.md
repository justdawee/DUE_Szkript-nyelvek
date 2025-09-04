# QR Generátor + Olvasó

Hallgató: Lukács Dávid Roland   
Monogram: HHC62Y

## Rövid leírás
Asztali alkalmazás, amely szövegből QR kódot generál és PNG-be ment, valamint képfájlból QR kódot beolvas és megjeleníti a dekódolt szöveget. Előzményt naplóz JSON-ben.

## Modulok
- Grafikai: tkinter
- Bemutatandó: OpenCV (cv2)
  - Példák: cv2.imread, cv2.cvtColor, cv2.QRCodeDetector().detectAndDecode
- Kiegészítő: qrcode (qrcode.make), Pillow (képmegjelenítés)
- Tanult: pathlib, datetime (ab_qr.py)

## Saját elemek
- Saját modul: `ab_qr.py`
- Saját osztály: `ABHistory`
- Saját függvény: `ab_timestamp()`

## Eseménykezelés
- Gombok: Generálás, Mentés, Megnyitás, Előzmény megnyitása
- Billentyűk: Enter = generálás, Ctrl+S = mentés, Ctrl+O = megnyitás
- Vászon méretezésre újrarajzolás

## Fájlkezelés
- JSON napló (`data/history.json`)
- PNG mentés (`out/AB_qr_<timestamp>.png`)

## Indítás
```
pip install -r requirements.txt
python main.py
```

## Fájlok
- `main.py` – GUI és logika
- `ab_qr.py` – saját modul (ABHistory, ab_timestamp)
- `requirements.txt` – csomagok
- `data/history.json` – előzmények
- `out/` – mentett képek
