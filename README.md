# 📚 BILIM KUTUBXONASI — Telegram Bot

Maktab o‘quvchilari va o‘qituvchilari uchun mo‘ljallangan zamonaviy, qulay va to‘liq ishlaydigan ta’lim platformasi.

Ushbu bot o‘quvchilarga barcha fanlar bo‘yicha elektron darsliklar va kitoblarni o‘qish, bilimlarini sinash uchun interaktiv testlarni yechish, umumiy reytingda o‘z o‘rnini ko‘rish, har kuni yangi ilmiy faktlar va bilim savollariga javob berish imkoniyatini taqdim etadi.

---

## 🌟 Asosiy imkoniyatlar

### 1. 📚 Elektron kutubxona
- **10 ta asosiy maktab fanlari:** Matematika, Fizika, Kimyo, Biologiya, Tarix, Ona tili, Adabiyot, Ingliz tili, Geografiya, Informatika.
- Har bir fan bo‘yicha elektron darsliklar, PDF kitoblar va mavzuga oid materiallar katalogi.
- **🔍 Qidiruv tizimi:** Kitob nomi yoki muallifi bo‘yicha tezkor qidiruv.
- Kitoblarni bevosita Telegram orqali PDF shaklida yuklab olish va yuklab olishlar hisoblagichi.

### 2. 📝 Test tizimi
- Har bir fan bo‘yicha alohida test sinovlari.
- **10 ta, 20 ta va 30 talik** test variantlari.
- 4 ta javob varianti (A, B, C, D) va bitta to‘g‘ri javob.
- Test davomida joriy savol ko‘rsatkichi va istalgan vaqtda testni to‘xtatish imkoniyati.
- Test yakunlangach: to‘g‘ri va noto‘g‘ri javoblar soni, foiz ko‘rsatkichi, ballar va baholash mezonlari (A'lo, Yaxshi, Qoniqarli).
- To‘plangan ballar darhol foydalanuvchi profiliga va reyting tizimiga qo‘shiladi.

### 3. 🏆 O‘quvchilar reytingi
- **🏆 Umumiy Top-10:** Barcha vaqtlar davomidagi eng bilimdon o‘quvchilar.
- **📅 Haftalik Top-10:** Oxirgi 7 kun davomida eng yaxshi natija ko‘rsatganlar.
- **⚡️ Eng faol o‘quvchilar:** Eng ko‘p test yechgan o‘quvchilar ro‘yxati.
- **📍 Shaxsiy o‘rin:** O‘quvchining jami foydalanuvchilar orasidagi aniq o‘rni va balli.

### 4. 💡 Kunlik bilim
- **🔬 Bugungi ilmiy fakt:** Har kuni yangi, qiziqarli ilmiy faktlar.
- **❓ Kunlik bilim savoli:** Har kuni bitta savol. To‘g‘ri javob bergan o‘quvchiga **+5 ball** beriladi.
- **📚 Fanlar bo‘yicha faktlar:** Fanlar kesimida qiziqarli ilmiy ma'lumotlar.

### 5. 👤 Mening profilim
- O‘quvchining ismi va familiyasi.
- Sinf ma'lumoti (masalan: *9-sinf*).
- Ishlangan testlar soni va to‘plangan jami ballar.
- Umumiy reytingdagi o‘rni.
- Ism va sinfni xohlagan paytda tahrirlash imkoniyati.

### 6. 📩 Admin bilan bog‘lanish
- Foydalanuvchilar savol, taklif yoki murojaatlarini to‘g‘ridan-to‘g‘ri bot orqali yuborishlari mumkin.
- Barcha murojaatlar administratorlarning shaxsiy Telegramiga ma'lumotlari bilan yetkaziladi.

### 7. ⚙️ Administrator paneli (Faqat ruxsat berilgan adminlar uchun)
- **📊 To‘liq statistika:** Foydalanuvchilar, kitoblar, savollar, ishlangan testlar va yuklab olingan kitoblar soni.
- **📚 Yangi kitob va PDF yuklash:** Fanni tanlash, kitob nomi, muallifi, sinfi, tavsifi va PDF faylni yuborish.
- **📝 Test savoli qo‘shish:** Fanni tanlash, savol matni, 4 ta variant, to‘g‘ri variant va yechim izohini kiritish.
- **🗑 Test savollarini o‘chirish:** Fanning mavjud savollarini ko‘rish va o‘chirish.
- **💡 Kunlik fakt va savol qo‘shish:** Botga yangi ilmiy ma'lumotlar va kunlik savollarni kiritish.
- **📢 Barchaga xabar yuborish (Broadcast):** Barcha bot a'zolariga e'lon yoki post yo‘llash.

---

## 📁 Loyiha arxitekturasi

```text
bilim_kutubxonasi/
│
├── .env                  # Maxfiy sozlamalar (BOT_TOKEN, ADMIN_IDS)
├── .env.example          # Sozlamalar namunasi
├── requirements.txt      # Kerakli Python kutubxonalari
├── README.md             # To'liq hujjatlashtirish va qo'llanma
├── main.py               # Asosiy ishga tushirish fayli
├── config.py             # Sozlamalarni o'qish va tekshirish
│
├── database/             # Ma'lumotlar bazasi (SQLite + aiosqlite)
│   ├── __init__.py
│   ├── db.py             # Jadvallar yaratish va boshlang'ich ma'lumotlarni kiritish (seeding)
│   └── models.py         # CRUD operatsiyalari va so'rovlar
│
├── keyboards/            # Tugmalar moduli
│   ├── __init__.py
│   ├── default_keyboards.py # ReplyKeyboardMarkup (Asosiy menyu)
│   └── inline_keyboards.py  # InlineKeyboardMarkup (Fanlar, testlar, reyting)
│
├── handlers/             # Bot buyruqlari va xabarlar
│   ├── __init__.py       # Routerlarni birlashtirish
│   ├── common.py         # /start, /help, profil boshqaruvi
│   ├── library.py        # Kutubxona va kitob qidirish
│   ├── quiz.py           # Test tizimi va ball hisoblash
│   ├── rating.py         # Reytinglar va shaxsiy o'rin
│   ├── daily.py          # Kunlik faktlar va savollar
│   ├── contact.py        # Admin bilan bog'lanish
│   └── admin.py          # Administrator boshqaruv paneli
│
├── states/               # FSM holatlari
│   ├── __init__.py
│   └── bot_states.py     # Qidiruv, profil, admin kiritish holatlari
│
└── utils/                # Yordamchi funksiyalar
    ├── __init__.py
    └── helpers.py        # Formatlash, admin tekshiruvi, baholash
```

---

## 🚀 O‘rnatish va ishga tushirish

### 1-qadam: Kerakli kutubxonalarni o‘rnatish
Terminal yoki konsolda quyidagi buyruqni bajaring:

```bash
pip install -r requirements.txt
```

### 2-qadam: Telegram Bot Tokenini olish
1. Telegramda [@BotFather](https://t.me/BotFather) ga kiring.
2. `/newbot` buyrug‘ini yuboring.
3. Bot nomini kiriting (masalan: `Bilim Kutubxonasi`).
4. Bot uchun username tanlang (masalan: `bilim_kutubxona_bot`).
5. BotFather bergan **HTTP API Token**ni nusxalab oling.

### 3-qadam: O‘z Telegram ID raqamingizni aniqlash
1. Telegramda [@userinfobot](https://t.me/userinfobot) botiga kiring va `/start` bosing.
2. U sizning `Id` raqamingizni beradi (masalan: `123456789`).

### 4-qadam: `.env` faylini sozlash
Loyihadagi `.env` faylini oching va o‘z ma'lumotlaringizni kiriting:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
DATABASE_PATH=database/bilim_kutubxonasi.db
```

*(Agar bir nechta admin bo‘lsa, ID larni vergul bilan ajrating: `123456789,987654321`)*

### 5-qadam: Botni ishga tushirish
Konsolda quyidagi buyruqni bering:

```bash
python main.py
```

Bot ilk marta ishga tushganda ma'lumotlar bazasini (`bilim_kutubxonasi.db`) avtomatik yaratadi, 10 ta fanni, 20 ta namunaviy kitobni, 50 ta sifatli test savolini va kunlik ilmiy faktlarni yuklaydi.

---

## 🛠 Administrator sifatida foydalanish

1. `.env` faylidagi `ADMIN_IDS` ro‘yxatiga o‘z Telegram ID raqamingizni yozganingizdan so‘ng, botda `/start` buyrug‘ini bosing.
2. Asosiy menyuda siz uchun qo‘shimcha **⚙️ Admin panel** tugmasi paydo bo‘ladi (yoki `/admin` buyrug‘ini yuborishingiz mumkin).
3. Admin panel orqali quyidagi amallarni bajarasiz:
   - **Kitob yuklash:** Fanni tanlang, kitob ma'lumotlarini kiriting va PDF faylni yuboring.
   - **Test savollari kiritish:** Fanni tanlang, savol matni va 4 ta variantni kiriting, to‘g‘ri javobni tugma orqali belgilang.
   - **Statistika:** Barcha foydalanuvchilar, testlar va yuklab olingan kitoblar hisobotini ko‘ring.
   - **Broadcast:** Barcha o‘quvchilarga e'lon tarqating.

---

## 💡 Texnologiyalar
- **Python 3.10+**
- **Aiogram 3.x** — zamonaviy asinxron Telegram Bot kutubxonasi
- **Aiosqlite** — asinxron SQLite ma'lumotlar bazasi drayveri
- **Python-dotenv** — maxfiy konfiguratsiyalarni boshqarish
