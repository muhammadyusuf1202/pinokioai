# PinokioAI 🤖

Groq.com ga o'xshash AI platforma — Python/Flask + SQLite

## Tezkor ishga tushirish

```bash
# 1. O'rnatish
pip install -r requirements.txt

# 2. Ishga tushirish
python app.py

# 3. Brauzerda ochish
# http://localhost:5000
```

## Loyiha tuzilmasi

```
pinokioai/
├── app.py              # Flask app + DB models + routes
├── requirements.txt
├── templates/
│   ├── base.html       # Umumiy layout + nav
│   ├── landing.html      # Bosh sahifa (Groq style)
│   ├── register.html   # Ro'yxatdan o'tish
│   ├── login.html      # Kirish
│   └── dashboard.html  # Foydalanuvchi paneli
└── static/
    ├── css/main.css    # Barcha dizayn
    └── js/main.js      # Animatsiyalar
```

## Sahifalar

| Sahifa | URL | Tavsif |
|--------|-----|--------|
| Bosh sahifa | `/` | Hero + Stats + Features + Pricing |
| Ro'yxat | `/register` | Yangi hisob yaratish |
| Kirish | `/login` | Mavjud hisob |
| Dashboard | `/dashboard` | Foydalanuvchi paneli |
| API | `/api/stats` | JSON stats endpoint |

## DB (SQLite)
- Fayl: `instance/pinokioai.db`
- Model: `User` (id, username, email, password_hash, plan, created_at)
