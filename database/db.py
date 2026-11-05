"""
Ma'lumotlar bazasi va jadvallarni initsializatsiya qilish moduli.
SQLite va aiosqlite asinxron kutubxonasidan foydalanadi.
"""

import aiosqlite
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from config import DB_PATH

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_db():
    """Ma'lumotlar bazasiga ulanish uchun asinxron context manager."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db():
    """Barcha jadvallarni yaratadi va boshlang'ich ma'lumotlarni yuklaydi."""
    async with get_db() as db:
        # 1. Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                username TEXT,
                grade TEXT DEFAULT 'Ko''rsatilmagan',
                total_score INTEGER DEFAULT 0,
                tests_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Fanlar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                code TEXT NOT NULL UNIQUE,
                icon TEXT DEFAULT '📖',
                is_active INTEGER DEFAULT 1
            )
        """)

        # 3. Kitoblar va darsliklar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                author TEXT DEFAULT 'Noma''lum',
                grade TEXT DEFAULT 'Barcha sinflar',
                description TEXT DEFAULT '',
                file_id TEXT,
                file_url TEXT,
                downloads_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        """)

        # 4. Test savollari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_option TEXT NOT NULL, -- 'A', 'B', 'C', 'D'
                explanation TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        """)

        # 5. Test natijalari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                score INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        """)

        # 6. Kunlik ilmiy faktlar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE SET NULL
            )
        """)

        # 7. Kunlik bilim savollari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_option TEXT NOT NULL,
                points INTEGER DEFAULT 5,
                date_str TEXT NOT NULL UNIQUE, -- 'YYYY-MM-DD'
                is_active INTEGER DEFAULT 1
            )
        """)

        # 8. Kunlik savolga javoblar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                daily_question_id INTEGER NOT NULL,
                answered_option TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (daily_question_id) REFERENCES daily_questions (id) ON DELETE CASCADE,
                UNIQUE (user_id, daily_question_id)
            )
        """)

        # 9. Admin bilan bog'lanish xabarlari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                is_replied INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)

        await db.commit()

        # Boshlang'ich ma'lumotlarni kiritish
        await seed_initial_data(db)


async def seed_initial_data(db: aiosqlite.Connection):
    """Baza bo'sh bo'lsa, namunaviy fanlar, testlar, kitoblar va faktlarni kiritadi."""
    cursor = await db.execute("SELECT COUNT(*) as cnt FROM subjects")
    row = await cursor.fetchone()
    if row and row["cnt"] > 0:
        return  # Ma'lumotlar allaqachon mavjud

    logger.info("Boshlang'ich ma'lumotlar (fanlar, testlar, kitoblar) bazaga yuklanmoqda...")

    # 1. Fanlar
    initial_subjects = [
        ("Matematika", "math", "📐"),
        ("Fizika", "physics", "⚡"),
        ("Kimyo", "chemistry", "🧪"),
        ("Biologiya", "biology", "🌿"),
        ("Tarix", "history", "🏛"),
        ("Ona tili", "uzbek_lang", "✍️"),
        ("Adabiyot", "literature", "📜"),
        ("Ingliz tili", "english", "🇬🇧"),
        ("Geografiya", "geography", "🌍"),
        ("Informatika", "informatics", "💻")
    ]

    for name, code, icon in initial_subjects:
        await db.execute(
            "INSERT INTO subjects (name, code, icon) VALUES (?, ?, ?)",
            (name, code, icon)
        )
    await db.commit()

    # Fan ID larini olish
    subject_map = {}
    async with await db.execute("SELECT id, code FROM subjects") as c:
        async for r in c:
            subject_map[r["code"]] = r["id"]

    # 2. Namunaviy Kitoblar
    initial_books = [
        # Matematika
        (subject_map["math"], "Algebra - 7-sinf", "Sh. Alimov", "7-sinf", "Umumiy o'rta ta'lim maktablarining 7-sinfi uchun darslik."),
        (subject_map["math"], "Geometriya - 8-sinf", "A. Rahimov", "8-sinf", "Planimetriya asoslari va teoremalar."),
        (subject_map["math"], "Matematika - 5-sinf", "M. Mirzaxmedov", "5-sinf", "Boshlang'ich algebra va arifmetika asoslari."),
        # Fizika
        (subject_map["physics"], "Fizika - 9-sinf", "P. Habibullayev", "9-sinf", "Mexanika, kinematika va dinamika qonuniyatlari."),
        (subject_map["physics"], "Fizika - 10-sinf", "A. Qosimov", "10-sinf", "Molekulyar fizika va termodinamika asoslari."),
        # Kimyo
        (subject_map["chemistry"], "Kimyo - 8-sinf", "I. Asqarov", "8-sinf", "Anorganik kimyo asoslari, davriy jadval."),
        (subject_map["chemistry"], "Kimyo - 9-sinf", "N. To'xtayev", "9-sinf", "Metall va metallmaslar kimyosi."),
        # Biologiya
        (subject_map["biology"], "Botanika - 6-sinf", "O. Pratov", "6-sinf", "O'simliklar dunyosi va ularning tuzilishi."),
        (subject_map["biology"], "Zoologiya - 7-sinf", "J. Mavlonov", "7-sinf", "Hayvonot olami, umurtqali va umurtqasizlar."),
        (subject_map["biology"], "Odam va uning salomatligi - 8-sinf", "B. Aminov", "8-sinf", "Inson anatomiyasi va fiziologiyasi."),
        # Tarix
        (subject_map["history"], "O'zbekiston tarixi - 8-sinf", "A. Muhammadjonov", "8-sinf", "O'rta asrlarda O'zbekiston tarixi, Temuriylar davri."),
        (subject_map["history"], "Jahon tarixi - 9-sinf", "U. Jo'rayev", "9-sinf", "Yangi davr jahon tarixi voqealari."),
        # Ona tili
        (subject_map["uzbek_lang"], "Ona tili - 7-sinf", "N. Mahmudov", "7-sinf", "Morfologiya, fe'l va so'z turkumlari."),
        (subject_map["uzbek_lang"], "Ona tili - 9-sinf", "A. Nurmonov", "9-sinf", "Qo'shma gap sintaksisi va tinish belgilari."),
        # Adabiyot
        (subject_map["literature"], "Adabiyot - 8-sinf", "S. Ahmedov", "8-sinf", "Mumtoz va zamonaviy o'zbek adabiyoti durdonalari."),
        (subject_map["literature"], "O'tkan kunlar", "Abdulla Qodiriy", "Barcha sinflar", "O'zbek adabiyotining ilk romani."),
        # Ingliz tili
        (subject_map["english"], "English - Guess What! 5-sinf", "Cambridge / O'zbekiston", "5-sinf", "Ingliz tili boshlang'ich grammatikasi va leksika."),
        (subject_map["english"], "English Grammar in Use", "Raymond Murphy", "Barcha sinflar", "Ingliz tili grammatikasini o'rganish uchun qo'llanma."),
        # Geografiya
        (subject_map["geography"], "Materiklar va okeanlar tabiiy geografiyasi - 7-sinf", "P. G'ulomov", "7-sinf", "Yer shari tabiiy zonalari va qit'alari."),
        # Informatika
        (subject_map["informatics"], "Informatika va AT - 8-sinf", "B. Boltayev", "8-sinf", "Algoritmlash va Python dasturlash tili asoslari.")
    ]

    for sub_id, title, author, grade, desc in initial_books:
        await db.execute(
            """INSERT INTO books (subject_id, title, author, grade, description)
               VALUES (?, ?, ?, ?, ?)""",
            (sub_id, title, author, grade, desc)
        )

    # 3. Test savollari
    initial_questions = [
        # Matematika
        (subject_map["math"], "Tenglamani yeching: 2x + 8 = 20", "x = 4", "x = 6", "x = 8", "x = 10", "B", "2x = 20 - 8 => 2x = 12 => x = 6"),
        (subject_map["math"], "To'g'ri to'rtburchakning bo'yi 8 sm, eni 5 sm. Uning yuzini toping.", "13 sm²", "26 sm²", "40 sm²", "30 sm²", "C", "S = a * b = 8 * 5 = 40 sm²"),
        (subject_map["math"], "Tub sonni aniqlang:", "9", "15", "17", "21", "C", "17 faqat 1 ga va o'ziga bo'linadi, shuning uchun tub son."),
        (subject_map["math"], "7 ning kvadrati (7²) nechaga teng?", "14", "49", "42", "56", "B", "7 * 7 = 49"),
        (subject_map["math"], "Uchburchakning ichki burchaklari yig'indisi necha gradusga teng?", "90°", "180°", "270°", "360°", "B", "Har qanday uchburchak ichki burchaklari yig'indisi doimo 180° ga teng."),

        # Fizika
        (subject_map["physics"], "Tezlikning xalqaro birliklar sistemasidagi (SI) o'lchov birligi nima?", "km/soat", "m/s", "sm/s", "m/min", "B", "SI sistemasida tezlik metr taqsim sekund (m/s) da o'lchanadi."),
        (subject_map["physics"], "Nyutonning 2-qonuni formulasini ko'rsating:", "F = m * a", "E = m * c²", "P = F / S", "v = s / t", "A", "Nyutonning ikkinchi qonuni: Kuch jism massasi bilan tezlanishining ko'paytmasiga teng."),
        (subject_map["physics"], "Suvning qaynash harorati normal bosimda necha gradus Selsiy?", "90°C", "100°C", "120°C", "80°C", "B", "Normal atmosfera bosimida toza suv 100°C da qaynaydi."),
        (subject_map["physics"], "Elektr tok kuchining o'lchov birligi nima?", "Volt", "Om", "Amper", "Vatt", "C", "Tok kuchi Amper (A) da o'lchanadi."),
        (subject_map["physics"], "Yorug'likning vakuumdagi tezligi taxminan qanchaga teng?", "300 000 km/s", "150 000 km/s", "30 000 km/s", "1 000 000 km/s", "A", "Yorug'lik tezligi vakuumda ~300 000 km/s."),

        # Kimyo
        (subject_map["chemistry"], "Suvning kimyoviy formulasi qaysi?", "CO2", "H2O", "NaCl", "CH4", "B", "Suv vodorod va kisloroddan tashkil topgan: H2O."),
        (subject_map["chemistry"], "Osh tuzining kimyoviy formulasi nima?", "NaCl", "KCl", "NaOH", "HCl", "A", "Osh tuzi natriy xloriddir (NaCl)."),
        (subject_map["chemistry"], "Davriy jadvalda eng yengil element qaysi?", "Geliy (He)", "Kislorod (O)", "Vodorod (H)", "Uglerod (C)", "C", "Vodorod atom massasi 1 ga teng eng yengil element."),
        (subject_map["chemistry"], "Kislorodning valentligi nechaga teng?", "I", "II", "III", "IV", "B", "Kislorod deyarli barcha birikmalarda II valentli."),
        (subject_map["chemistry"], "Fotosintez jarayonida o'simliklar qaysi gazni yutadi?", "Kislorod", "Azot", "Karbonat angidrid", "Vodorod", "C", "O'simliklar karbonat angidrid (CO2) yutib, kislorod chiqaradi."),

        # Biologiya
        (subject_map["biology"], "Tirik organizmlarning eng kichik tuzilish birligi nima?", "Organ", "To'qima", "Hujayra", "Molekula", "C", "Barcha tirik mavjudotlarning tuzilish va hayot faoliyati birligi hujayradir."),
        (subject_map["biology"], "O'simliklarga yashil rang beruvchi pigment nima deb ataladi?", "Globin", "Xlorofill", "Melanin", "Karotin", "B", "Xloroplastlardagi xlorofill pigmenti yashil rang beradi."),
        (subject_map["biology"], "Odam yuragi necha kamerali?", "2 ta", "3 ta", "4 ta", "5 ta", "C", "Inson yuragi 4 kamerali: 2 ta bo'lmacha va 2 ta qorincha."),
        (subject_map["biology"], "Qizil qon tanachalari nima deb ataladi?", "Leykotsitlar", "Eritrotsitlar", "Trombotsitlar", "Fagotsitlar", "B", "Eritrotsitlar qonga qizil rang beradi va kislorod tashiydi."),
        (subject_map["biology"], "Inson tanasidagi eng katta ichki a'zo qaysi?", "Yurak", "O'pka", "Jigar", "Buyrak", "C", "Jigar inson tanasidagi eng yirik ichki a'zodir."),

        # Tarix
        (subject_map["history"], "Amir Temur nechanchi yilda tavallud topgan?", "1336-yil", "1342-yil", "1370-yil", "1405-yil", "A", "Amir Temur 1336-yil 9-aprelda Xo'ja Ilg'or qishlog'ida tug'ilgan."),
        (subject_map["history"], "Buyuk ipak yo'li qaysi mamlakatdan boshlangan?", "Hindiston", "Xitoy", "Misr", "Rim", "B", "Buyuk ipak yo'li qadimgi Xitoyning Chanan shahridan boshlangan."),
        (subject_map["history"], "Mirzo Ulug'bek rasadxonasi qaysi shaharda qurilgan?", "Buxoro", "Samarqand", "Xiva", "Toshkent", "B", "Ulug'bek rasadxonasi Samarqandda 1424-1428 yillarda barpo etilgan."),
        (subject_map["history"], "Qadimgi Misr hukmdorlari nima deb atalgan?", "Xon", "Shoh", "Fir'avn", "Imperator", "C", "Qadimgi Misrda oliy hukmdor Fir'avn deb atalgan."),
        (subject_map["history"], "Al-Xorazmiy qaysi fanning asoschisi hisoblanadi?", "Geografiya", "Algebra", "Biologiya", "Fizika", "B", "Al-Xorazmiy 'Al-Jabr' asari bilan algebraga asos solgan."),

        # Ona tili
        (subject_map["uzbek_lang"], "O'zbek tilida nechta unli tovush bor?", "5 ta", "6 ta", "8 ta", "10 ta", "B", "O'zbek tilida 6 ta unli tovush mavjud: a, o, i, u, o', e."),
        (subject_map["uzbek_lang"], "Ot so'z turkumi qanday so'roqlarga javob bo'ladi?", "Qanday? Qanaqa?", "Kim? Nima? Qayer?", "Nechta? Qancha?", "Nima qildi?", "B", "Ot shaxs, narsa-buyum va joy nomini bildiradi: Kim? Nima? Qayer?"),
        (subject_map["uzbek_lang"], "Qaysi so'z imloviy jihatdan to'g'ri yozilgan?", "Mawzu", "Mavzu", "Movzu", "Mavzi", "B", "To'g'ri yozilishi: 'Mavzu'."),
        (subject_map["uzbek_lang"], "'Baland' so'zining antonimi nima?", "Katta", "Past", "Uzoq", "Keng", "B", "Baland so'ziga zid ma'noli so'z: Past."),
        (subject_map["uzbek_lang"], "Qaysi gap turida bir nechta ega va kesim qatnashadi?", "Sodda gap", "Qo'shma gap", "So'z-gap", "To'liqsiz gap", "B", "Qo'shma gap ikki yoki undan ortiq sodda gaplardan tuziladi."),

        # Adabiyot
        (subject_map["literature"], "O'zbek adabiyotining birinchi romani qaysi?", "Mehrobdan chayon", "O'tkan kunlar", "Kecha va kunduz", "Shum bola", "B", "Abdulla Qodiriyning 'O'tkan kunlar' asari (1922-1926) o'zbek adabiyotidagi ilk romandir."),
        (subject_map["literature"], "'Xamsa' asarini turkiy tilda birinchi bo'lib kim yaratgan?", "Nizomiy Ganjaviy", "Alisher Navoiy", "Zahiriddin Bobur", "Lutfiy", "B", "Alisher Navoiy 1483-1485 yillarda ilk bor turkiy tilda 'Xamsa' yaratgan."),
        (subject_map["literature"], "'Boburnoma' asarining muallifi kim?", "Alisher Navoiy", "Zahiriddin Muhammad Bobur", "Mashrab", "Ogahiy", "B", "Zahiriddin Muhammad Boburning shoh asari 'Boburnoma'dir."),
        (subject_map["literature"], "'Dunyoning ishlari' qissasining muallifi kim?", "O'tkir Hoshimov", "Said Ahmad", "Erkin Vohidov", "Abdulla Oripov", "A", "'Dunyoning ishlari' asari O'tkir Hoshimov qalamiga mansub."),
        (subject_map["literature"], "O'zbekiston Respublikasi Davlat madhiyasi matni muallifi kim?", "Erkin Vohidov", "Abdulla Oripov", "Muhammad Yusuf", "Zulfiya", "B", "Madhiyamiz matnini O'zbekiston Qahramoni Abdulla Oripov yozgan."),

        # Ingliz tili
        (subject_map["english"], "Choose the correct pronoun: '... is my best friend.'", "He", "Him", "His", "Her", "A", "Ega vazifasida bosh kelishikdagi olmosh keladi: 'He is my best friend.'"),
        (subject_map["english"], "What is the past tense of the verb 'go'?", "Goed", "Gone", "Went", "Going", "C", "'Go' fe'lining o'tgan zamon shakli - 'went'."),
        (subject_map["english"], "Translate to Uzbek: 'Knowledge is power.'", "Vaqt - bu boylik.", "Bilim - bu kuch.", "Mehnat - baxt keltirar.", "Daftar va qalam.", "B", "'Knowledge is power' - 'Bilim bu kuch' degani."),
        (subject_map["english"], "Choose the plural form of 'child':", "Childs", "Children", "Childrens", "Childes", "B", "'Child' so'zining ko'plik shakli noto'g'ri o'zgaradi: 'children'."),
        (subject_map["english"], "Which article is used before vowels (a, e, i, o, u)?", "A", "An", "The", "No article", "B", "Unli tovush bilan boshlangan so'zlar oldidan 'an' noaniq artikli qo'yiladi."),

        # Geografiya
        (subject_map["geography"], "Dunyo bo'yicha eng katta materik qaysi?", "Afrika", "Shimoliy Amerika", "Yevrosiyo", "Avstraliya", "C", "Yevrosiyo Yer yuzidagi eng yirik quruqlik materigidir."),
        (subject_map["geography"], "O'zbekiston poytaxti qaysi shahar?", "Samarqand", "Buxoro", "Toshkent", "Namangan", "C", "O'zbekiston Respublikasining poytaxti - Toshkent shahri."),
        (subject_map["geography"], "Dunyodagi eng chuqur ko'l qaysi?", "Kaspiy dengizi", "Baykal ko'li", "Viktoriya", "Orol dengizi", "B", "Baykal ko'li dunyodagi eng chuqur chuchuk suvli ko'ldir (1642 m)."),
        (subject_map["geography"], "Yer sharining eng baland cho'qqisi nima deb ataladi?", "Monblan", "Elbrus", "Everest (Jomolungma)", "Kilianjaro", "C", "Everest (Jomolungma) dengiz sathidan 8848 metr baland."),
        (subject_map["geography"], "O'zbekiston qaysi daryolar oralig'ida joylashgan?", "Nil va Kongo", "Amudaryo va Sirdaryo", "Volga va Don", "Gang va Hind", "B", "O'zbekiston Amudaryo va Sirdaryo daryolari havzasida joylashgan."),

        # Informatika
        (subject_map["informatics"], "Axborotning eng kichik o'lchov birligi nima?", "Bayt", "Bit", "Kilobayt", "Megabayt", "B", "Bit (0 yoki 1) axborotning eng kichik elementar o'lchov birligidir."),
        (subject_map["informatics"], "1 Bayt necha bitga teng?", "4 bit", "8 bit", "16 bit", "1024 bit", "B", "1 Bayt = 8 bit."),
        (subject_map["informatics"], "Python tilida konsolga ma'lumot chiqarish buyrug'i qaysi?", "input()", "print()", "write()", "echo()", "B", "Python-da ma'lumotni ekranga chiqarish uchun print() funksiyasi ishlatiladi."),
        (subject_map["informatics"], "Kompyuterning 'miyasi' deb qaysi qurilma aytiladi?", "Monitor", "Qattiq disk (HDD)", "Protsessor (CPU)", "Operativ xotira (RAM)", "C", "Protsessor (CPU) barcha hisoblash va boshqaruv amallarini bajaradi."),
        (subject_map["informatics"], "Klaviatura qanday qurilma hisoblanadi?", "Chiqarish qurilmasi", "Kiritish qurilmasi", "Saqlash qurilmasi", "Tarmoq qurilmasi", "B", "Klaviatura kompyuterga matn va buyruqlarni kirituvchi asosiy qurilmadir.")
    ]

    for sub_id, q_text, op_a, op_b, op_c, op_d, corr, expl in initial_questions:
        await db.execute(
            """INSERT INTO questions (subject_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (sub_id, q_text, op_a, op_b, op_c, op_d, corr, expl)
        )

    # 4. Kunlik ilmiy faktlar
    initial_facts = [
        (subject_map["math"], "Nol (0) sonining kelib chiqishi", "Nol soni ilk bor qadimgi hind va sharq allomalari, jumladan Muhammad al-Xorazmiy tomonidan fanga chuqur kiritilgan bo'lib, butun matematika tizimini tubdan o'zgartirgan."),
        (subject_map["physics"], "Yorug'likning Quyoshdan Yerga yetib kelishi", "Quyosh nurlari Yer yuzasiga yetib kelishi uchun taxminan 8 daqiqa 20 soniya vaqt sarflaydi. Demak, biz hozir ko'rayotgan quyosh nuri 8 daqiqa oldin chiqqan!"),
        (subject_map["biology"], "Inson yuragining qudrati", "Inson yuragi bir kunda o'rtacha 100 000 martadan ortiq uradi va 7 500 litrdan ortiq qonni butun tanaga haydab beradi."),
        (subject_map["chemistry"], "Osh tuzi qiziq fakt", "Osh tuzi (NaCl) portlovchi va suv bilan tez reaksiyaga kirishuvchi Natriy (Na) metalli hamda zaharli Xlor (Cl) gazining birikmasidan hosil bo'ladi, lekin inson hayoti uchun zarurdir!"),
        (subject_map["informatics"], "Dunyodagi ilk dasturchi ayol", "Tarixdagi birinchi dasturchi sifatida Ada Lavleys (1815–1852) e'tirof etiladi. U Charlz Bebbijning hisoblash mashinasi uchun ilk algoritmni yozgan.")
    ]

    for sub_id, title, content in initial_facts:
        await db.execute(
            "INSERT INTO daily_facts (subject_id, title, content) VALUES (?, ?, ?)",
            (sub_id, title, content)
        )

    # 5. Kunlik savol
    today_str = datetime.now().strftime("%Y-%m-%d")
    await db.execute(
        """INSERT OR IGNORE INTO daily_questions 
           (question_text, option_a, option_b, option_c, option_d, correct_option, points, date_str, is_active)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
        (
            "Qaysi sayyora Quyosh sistemasidagi eng katta sayyora hisoblanadi?",
            "Mars",
            "Yupiter",
            "Saturn",
            "Venera",
            "B",
            5,
            today_str
        )
    )

    await db.commit()
    logger.info("Boshlang'ich ma'lumotlar muvaffaqiyatli yuklandi.")
