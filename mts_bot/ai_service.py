# ai_service.py - расширенная AI-модель
import re
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# === БАЗА ЗНАНИЙ МТС ===
COMPANY_INFO = {
    "name": "МТС",
    "full_name": "ПАО «Мобильные ТелеСистемы»",
    "founded": 1993,
    "employees": "более 60 000",
    "rating": "4.2/5 на hh.ru",
    "benefits": [
        "Официальное трудоустройство с первого дня",
        "ДМС со стоматологией",
        "Корпоративная мобильная связь",
        "Годовые премии до 30% от зарплаты",
        "Обучение и курсы за счёт компании",
        "Гибкий график и гибридный формат",
        "Корпоративная пенсионная программа",
        "Скидки на продукты МТС"
    ]
}

SALARY_DATA = {
    "стажёр": (50000, 70000),
    "стажер": (50000, 70000),
    "специалист": (80000, 120000),
    "ведущий специалист": (120000, 180000),
    "аналитик": (100000, 200000),
    "инженер": (90000, 150000),
    "продавец": (50000, 100000),
    "менеджер": (150000, 250000),
    "hr": (70000, 120000),
    "юрист": (80000, 150000)
}

INTERNSHIP_INFO = {
    "duration": "3-6 месяцев",
    "salary": "от 50 000 ₽",
    "schedule": "20-40 часов в неделю (гибко)",
    "requirements": [
        "Студент или выпускник последних 2 лет",
        "Базовые знания в выбранной сфере",
        "Желание учиться и развиваться"
    ],
    "benefits": [
        "Оплачиваемая стажировка",
        "Наставник из числа топ-специалистов",
        "Реальные задачи, а не учебные",
        "Возможность трудоустройства после",
        "Доступ к корпоративному обучению"
    ]
}

INTERVIEW_TIPS = {
    "do": [
        "Изучи сайт МТС и последние новости за неделю",
        "Подготовь 3-5 вопросов работодателю",
        "Расскажи о своих достижениях цифрами",
        "Будь честным про свои скиллы",
        "Оденься в деловом стиле (даже онлайн)"
    ],
    "dont": [
        "Не опаздывай (приди за 10 минут)",
        "Не говори плохо о прошлых работодателях",
        "Не используй слова-паразиты",
        "Не перебивай интервьюера",
        "Не спрашивай про зарплату в первую минуту"
    ],
    "common_questions": [
        "Расскажите о себе",
        "Почему вы хотите работать в МТС?",
        "Какие ваши сильные и слабые стороны?",
        "Где вы видите себя через 5 лет?",
        "Почему нам стоит выбрать вас?"
    ]
}

SKILLS_MAP = {
    "python": {"category": "IT", "difficulty": "medium", "resources": ["Stepik курс 67", "YouTube: Хирьянов"]},
    "sql": {"category": "IT", "difficulty": "easy", "resources": ["Stepik курс 51562", "SQL Academy"]},
    "excel": {"category": "office", "difficulty": "easy", "resources": ["Stepik курс 85", "YouTube: Excel для начинающих"]},
    "english": {"category": "soft", "difficulty": "medium", "resources": ["Duolingo", "English with Lucy"]},
    "продажи": {"category": "business", "difficulty": "medium", "resources": ["Coursera: Sales Training", "Книга «Стратегия голубого океана»"]},
    "hr": {"category": "business", "difficulty": "medium", "resources": ["Нетология: HR Generalist", "Skillbox: Рекрутинг"]},
    "маркетинг": {"category": "business", "difficulty": "medium", "resources": ["Яндекс: Основы маркетинга", "Google Digital Garage"]},
    "аналитика": {"category": "IT", "difficulty": "hard", "resources": ["Stepik: Аналитика данных", "Kaggle"]},
    "management": {"category": "soft", "difficulty": "hard", "resources": ["Coursera: Управление проектами", "Книга «7 навыков»"]}
}

# === ОСНОВНОЙ AI-КЛАСС ===
class MTSCareerAI:
    """Улучшенный AI-помощник для карьеры в МТС"""
    
    def __init__(self):
        self.context = {}  # Храним контекст диалога
        self.user_profiles = {}  # Профили пользователей
    
    def _thoughtful_response(self, prompt: str, intent: str) -> str:
        """Вдумчивый ответ с анализом"""
        
        # 1. Анализируем сложность вопроса
        words = len(prompt.split())
        has_numbers = bool(re.search(r'\d+', prompt))
        has_comparison = any(word in prompt.lower() for word in ["или", "vs", "лучше", "хуже"])
        
        # 2. Формируем «мысль» AI
        thinking = []
        
        if words > 10:
            thinking.append("🤔 *Хороший вопрос, давай разберёмся детально...*")
        
        if has_comparison:
            thinking.append("⚖️ *Сравниваю варианты, чтобы дать объективный ответ...*")
        
        if intent == "salary" and has_numbers:
            thinking.append("📊 *Учитываю твой опыт и регион...*")
        
        thinking_text = "\n".join(thinking) + "\n\n" if thinking else ""
        
        # 3. Получаем основной ответ
        main_answer = self._handle_intent(intent, prompt, None)
        
        # 4. Добавляем «размышления» в конец
        reflection = self._add_reflection(intent, prompt)
        
        return thinking_text + main_answer + reflection
    
    def _add_reflection(self, intent: str, prompt: str) -> str:
        """Добавляет вдумчивый комментарий"""
        
        reflections = {
            "salary": "\n\n💭 *Моё мнение:* Для старта в МТС стажировка — лучший вход. А через 6 месяцев можно просить повышение.",
            "internship": "\n\n💭 *Совет:* Не жди идеального момента — откликайся сейчас. 70% стажёров остаются в МТС после стажировки.",
            "interview": "\n\n💭 *Секрет:* Самый частый провал — невнимание к компании. Изучи сайт МТС за час до собеседования.",
            "skills": "\n\n💭 *Моя рекомендация:* Начни с одного навыка (например, Python), а не распыляйся на всё сразу.",
            "career_growth": "\n\n💭 *Важно:* В МТС растут те, кто берёт ответственность. Не бойся дополнительных задач."
        }
        
        return reflections.get(intent, "")
    
    def get_response(self, prompt: str, user_id: int = None) -> str:
        """Главный метод для получения ответа с поддержкой контекста"""
        
        # Сохраняем вопрос пользователя в историю
        if user_id:
            if user_id not in self.context:
                self.context[user_id] = []
            self.context[user_id].append({"role": "user", "content": prompt})
            # Оставляем только последние 10 сообщений
            if len(self.context[user_id]) > 10:
                self.context[user_id] = self.context[user_id][-10:]

            # ========== УНИВЕРСАЛЬНАЯ ПРОВЕРКА КОНТЕКСТА ==========
            if len(self.context[user_id]) > 2:
                # Находим последний вопрос пользователя и тему
                last_question = ""
                last_topic = None
                for msg in reversed(self.context[user_id][-6:]):
                    if msg.get("role") == "user":
                        last_question = msg.get("content", "")
                        last_topic = msg.get("topic", self._detect_intent(last_question))
                        break
                
                # Определяем тему текущего вопроса
                current_topic = self._detect_intent(prompt.lower())
                
                # Если текущий вопрос — уточнение (короткий или начинается с "а", "но", "и")
                is_clarification = (
                    len(prompt.split()) < 5 or 
                    prompt.lower().startswith(("а ", "но ", "и ", "ведь ", "тогда "))
                )
                
                # Если это уточнение и есть предыдущая тема — отвечаем в контексте
                if is_clarification and last_topic and last_topic not in ["greeting", "feedback", "default"]:
                    # Специальные комбинации вопрос-уточнение
                    if "зарплат" in prompt.lower() or "сколько" in prompt.lower():
                        if last_topic == "internship":
                            return self._salary_internship_response()
                        elif last_topic == "salary":
                            return self._salary_clarification_response(last_question)
                    
                    if "удален" in prompt.lower() or "дистанц" in prompt.lower() or "из дома" in prompt.lower():
                        if last_topic == "vacancies":
                            return self._remote_clarification_response()
                        elif last_topic == "company":
                            return self._remote_company_response()
                    
                    if "как" in prompt.lower() and "отклик" in prompt.lower():
                        if last_topic == "vacancies":
                            return self._apply_clarification_response()
                    
                    # Универсальный ответ в контексте
                    return self._context_aware_response(prompt, last_topic, last_question)
        
        prompt_lower = prompt.lower()
        
        # Определяем намерение пользователя
        intent = self._detect_intent(prompt_lower)
        
        # Получаем ответ
        response = self._thoughtful_response(prompt, intent)
        
        # Сохраняем тему ответа в историю
        if user_id and self.context[user_id]:
            self.context[user_id][-1]["topic"] = intent
        
        # Добавляем форматирование
        response = self._enhance_response(response, intent)
        
        # Сохраняем ответ в историю
        if user_id:
            self.context[user_id].append({"role": "assistant", "content": response, "topic": intent})
        
        return response
    
    def _detect_intent(self, text: str) -> str:
        """Определяет, что хочет пользователь"""
        intents = {
            # Сначала самые конкретные
            "internship": r"(стажировк|стажёр|стажер|студент.*без опыта|начинающ|практик)",
            "salary": r"(зарплат|сколько.*платят|доход|оклад|деньги|зп|зарплата)",
            "remote": r"(удален|remote|из дома|на дому|дистанцион)",
            "interview": r"(собесед|интервью|вопросы.*собесед|подготовк.*собесед|как.*пройти)",
            "vacancies": r"(ваканс|подойдет|какие.*ваканс|куда.*можно|работа.*мтс)",
            "skills": r"(что учить|какие навыки|что нужно знать|обучение|курсы)",
            "python": r"(python|питон|программиров|код|it|айти)",
            "english": r"(англ|english|язык|foreign)",
            "how_to_apply": r"(откликн|резюме|подать|устроит|как отправить)",
            "career_growth": r"(карьер|рост|повышен|развити|перспектив|трек)",
            "feedback": r"(спасибо|отлично|класс|супер|молодец|хорош)",
            "age": r"(возраст|лет|год)",
            "education": r"(образование|школьник|студент|выпускник|вуз|колледж)",
            "greeting": r"(привет|здравствуй|добрый день|доброе утро|hello|hi|ку)",
            "company": r"(мтс|компания|отзыв.*компани|хороша.*компани|стоит.*работать|работать.*мтс)",
            "default": r".*"
        }
        
        for intent, pattern in intents.items():
            if re.search(pattern, text, re.IGNORECASE):
                return intent
        return "default"
    
    def _handle_intent(self, intent: str, prompt: str, user_id: Optional[int] = None) -> str:
        """Обрабатывает намерение и возвращает ответ"""
        
        if intent == "greeting":
            return self._greeting(prompt)
        
        elif intent == "company":
            return self._company_info()
        
        elif intent == "salary":
            return self._salary_info(prompt)
        
        elif intent == "internship":
            return self._internship_info()
        
        elif intent == "remote":
            return self._remote_info()
        
        elif intent == "interview":
            return self._interview_info(prompt)
        
        elif intent == "vacancies":
            return self._vacancies_info(prompt)
        
        elif intent == "skills":
            return self._skills_info(prompt)
        
        elif intent == "python":
            return self._python_info()
        
        elif intent == "english":
            return self._english_info()
        
        elif intent == "how_to_apply":
            return self._how_to_apply()
        
        elif intent == "career_growth":
            return self._career_growth()
        
        elif intent == "feedback":
            return self._feedback()
        
        elif intent in ["age", "education"]:
            return self._personal_info(intent, prompt)
        
        else:
            return self._fallback_response(prompt)
    
    # === ОТДЕЛЬНЫЕ МЕТОДЫ ДЛЯ КАЖДОГО НАМЕРЕНИЯ ===
    
    def _greeting(self, prompt: str) -> str:
        greetings = [
            "Привет! 👋 Я AI-помощник МТС по карьере.\n\nРасскажу про вакансии, стажировки, зарплаты и помогу подготовиться к собеседованию.\n\nЧто тебя интересует?",
            "Здравствуй! 🌟 Рада видеть тебя в МТС.\n\nХочешь узнать про стажировки? Или посмотреть вакансии? Просто спроси!",
            "Приветствую! 🚀 Готов помочь с карьерой в МТС.\n\nЗадай любой вопрос: от зарплаты до карьерного роста."
        ]
        return random.choice(greetings)
    
    def _company_info(self) -> str:
        benefits = "\n".join([f"  ✅ {b}" for b in COMPANY_INFO["benefits"]])
        
        return (f"🏢 *{COMPANY_INFO['full_name']}*\n\n"
                f"📅 Основана: {COMPANY_INFO['founded']} год\n"
                f"👥 Сотрудников: {COMPANY_INFO['employees']}\n"
                f"⭐ Рейтинг на hh.ru: {COMPANY_INFO['rating']}\n\n"
                f"*✨ Почему выбирают МТС:*\n{benefits}\n\n"
                f"💡 МТС — не только связь. Мы лидеры в AI, Big Data, финтехе и облачных технологиях!")
    
    def _salary_info(self, prompt: str) -> str:
        # Ищем ключевую позицию в вопросе
        position = None
        for key in SALARY_DATA.keys():
            if key in prompt.lower():
                position = key
                break
        
        if position and position in SALARY_DATA:
            min_sal, max_sal = SALARY_DATA[position]
            return (f"💰 *Зарплата в МТС: {position.capitalize()}*\n\n"
                    f"📊 Диапазон: *{min_sal:,} - {max_sal:,} ₽*\n\n"
                    f"✨ *Дополнительно:*\n"
                    f"• Ежеквартальные бонусы (до 30%)\n"
                    f"• ДМС с первого дня\n"
                    f"• Оплата мобильной связи\n"
                    f"• Корпоративное обучение")
        
        # Общая информация
        return ("💰 *Зарплаты в МТС:*\n\n"
                "• 🎓 *Стажёры:* 50 000 - 70 000 ₽\n"
                "• 👨‍💻 *Специалисты:* 80 000 - 120 000 ₽\n"
                "• 🚀 *Ведущие специалисты:* 120 000 - 180 000 ₽\n"
                "• 📈 *Менеджеры:* 150 000 - 250 000 ₽\n\n"
                "➕ *Плюс:* премии, ДМС, обучение, корпоративная связь\n\n"
                "🔍 *Уточните конкретную позицию, и скажу точнее!*")
    
    def _internship_info(self) -> str:
        requirements = "\n".join([f"• {r}" for r in INTERNSHIP_INFO["requirements"]])
        benefits = "\n".join([f"• {b}" for b in INTERNSHIP_INFO["benefits"]])
        
        return (f"🎓 *Стажировки в МТС*\n\n"
                f"⏰ Длительность: {INTERNSHIP_INFO['duration']}\n"
                f"💰 Оплата: {INTERNSHIP_INFO['salary']}\n"
                f"📅 График: {INTERNSHIP_INFO['schedule']}\n\n"
                f"*📋 Требования:*\n{requirements}\n\n"
                f"*✨ Что даёт стажировка:*\n{benefits}\n\n"
                f"👉 Актуальные направления: продажи, HR, IT, аналитика, юриспруденция")
    
    def _interview_info(self, prompt: str) -> str:
        do_tips = "\n".join([f"  ✅ {tip}" for tip in INTERVIEW_TIPS["do"]])
        dont_tips = "\n".join([f"  ❌ {tip}" for tip in INTERVIEW_TIPS["dont"]])
        questions = "\n".join([f"  • {q}" for q in INTERVIEW_TIPS["common_questions"]])
        
        return (f"📋 *Как успешно пройти собеседование в МТС*\n\n"
                f"*✅ ЧТО ДЕЛАТЬ:*\n{do_tips}\n\n"
                f"*❌ ЧЕГО ИЗБЕГАТЬ:*\n{dont_tips}\n\n"
                f"*🎯 Типичные вопросы:*\n{questions}\n\n"
                f"*💡 Бонус:* Подготовь 3-5 вопросов работодателю про задачи, команду, развитие!\n\n"
                f"👉 Хочешь полный чек-лист? Напиши «чек-лист»!")
    
    def _vacancies_info(self, prompt: str) -> str:
        return ("📋 *Где посмотреть вакансии МТС:*\n\n"
                "1️⃣ *В этом боте* — нажми кнопку «📋 Вакансии»\n"
                "2️⃣ *На hh.ru* — поиск «МТС»\n"
                "3️⃣ *На сайте* — career.mts.ru\n\n"
                "*🔥 Сейчас особенно востребованы:*\n"
                "• Аналитики (в т.ч. AI)\n"
                "• Разработчики Python\n"
                "• Специалисты по продажам\n"
                "• HR-специалисты\n\n"
                "👉 Нажми «📋 Вакансии», чтобы увидеть все!")
    
    def _skills_info(self, prompt: str) -> str:
        return ("📚 *Что учить для работы в МТС:*\n\n"
                "*🖥️ IT и аналитика:*\n"
                "  • Python + pandas/numpy\n"
                "  • SQL\n"
                "  • Excel (продвинутый)\n\n"
                "*💼 Бизнес-направления:*\n"
                "  • Навыки продаж и переговоров\n"
                "  • CRM-системы\n"
                "  • Английский язык (B1+)\n\n"
                "*👥 HR и управление:*\n"
                "  • Рекрутинг\n"
                "  • Трудовое право\n"
                "  • HR-аналитика\n\n"
                "👉 Напиши конкретный навык (например, «Python»), и я дам курсы!")
    
    def _python_info(self) -> str:
        return ("🐍 *Python в МТС*\n\n"
                "*Где используется:*\n"
                "• Аналитика данных\n"
                "• Искусственный интеллект (AI)\n"
                "• Автоматизация процессов\n"
                "• Бэкенд-разработка\n\n"
                "*🎓 Бесплатные курсы:*\n"
                "• [Python для начинающих (Stepik)](https://stepik.org/course/67)\n"
                "• [YouTube: Тимофей Хирьянов](https://www.youtube.com/playlist?list=PLRDzFCPr95fK7tr47883DFUbm4GeOjjc0)\n\n"
                "*📊 Практика:*\n"
                "• LeetCode — задачи\n"
                "• Kaggle — работа с данными\n\n"
                "💡 Совет: уделяй 30-60 минут в день — через 3 месяца будешь уверенным пользователем!")
    
    def _english_info(self) -> str:
        return ("🇬🇧 *Английский язык для карьеры в МТС*\n\n"
                "*Зачем нужен:*\n"
                "• Чтение технической документации\n"
                "• Работа с зарубежными технологиями\n"
                "• Участие в международных проектах\n"
                "• Карьерный рост (позиции Senior+)\n\n"
                "*🎓 Бесплатные ресурсы:*\n"
                "• [Duolingo](https://www.duolingo.com/) — с нуля до B1\n"
                "• [YouTube: English with Lucy](https://www.youtube.com/@EnglishwithLucy)\n"
                "• [BBC Learning English](https://www.bbc.co.uk/learningenglish)\n\n"
                "*Целевой уровень:* B1 (Intermediate) для старта, B2 для продвинутых позиций")
    
    def _how_to_apply(self) -> str:
        return ("📝 *Как откликнуться на вакансию в МТС*\n\n"
                "*Способы:*\n"
                "1️⃣ *Через бота* — нажми «📋 Вакансии» → выбери вакансию → «Откликнуться»\n"
                "2️⃣ *По почте* — отправь резюме на career@mts.ru\n"
                "3️⃣ *На hh.ru* — найди вакансию и нажми «Откликнуться»\n\n"
                "*Что указать в отклике:*\n"
                "• ФИО и телефон\n"
                "• Желаемую позицию\n"
                "• Кратко о себе и опыте (1-2 предложения)\n"
                "• Ссылку на резюме (или файл)\n\n"
                "📌 *Совет:* Всегда прикрепляй резюме — даже если не просят!")
    
    def _career_growth(self) -> str:
        return ("🚀 *Карьерный рост в МТС*\n\n"
                "*Типичный путь развития:*\n"
                "🎓 Стажёр → 👨‍💻 Специалист → 📈 Ведущий специалист → 👔 Руководитель → 🎯 Директор\n\n"
                "*Примерные сроки:*\n"
                "• До специалиста: 6-12 месяцев\n"
                "• До ведущего специалиста: 2-3 года\n"
                "• До руководителя: 4-6 лет\n\n"
                "*Что даёт МТС для роста:*\n"
                "• ✅ Оплачиваемые курсы и сертификации\n"
                "• ✅ Наставничество от лидеров\n"
                "• ✅ Горизонтальный переход в другие отделы\n"
                "• ✅ Программы MBA для топ-сотрудников\n\n"
                "👉 Нажми «📈 Карьерный трек» для детального плана по твоей специальности!")
    
    def _feedback(self) -> str:
        feedbacks = [
            "Рада помочь! 😊 Обращайся, если будут ещё вопросы!",
            "Всегда пожалуйста! 🌟 Удачи в карьере в МТС!",
            "Спасибо! 🙌 Если захочешь посмотреть вакансии или пройти диагностику — я здесь!",
            "Пожалуйста! 🚀 Не стесняйся спрашивать ещё!"
        ]
        return random.choice(feedbacks)
    
    def _personal_info(self, intent: str, prompt: str) -> str:
        if intent == "age":
            return ("📊 *Возрастные ограничения в МТС*\n\n"
                    "• Стажировки: с 16 лет (школьники) или с 18 лет (студенты/выпускники)\n"
                    "• Работа в рознице: с 18 лет\n"
                    "• Офисные позиции: с 18 лет\n\n"
                    "👉 Хочешь пройти диагностику? Нажми «🎯 Профориентация» → «Диагностика»")
        else:
            return ("🎓 *Требования к образованию в МТС*\n\n"
                    "• Школьники → стажировки (16+)\n"
                    "• Студенты колледжей → стажировки, розница\n"
                    "• Студенты вузов → стажировки, все позиции\n"
                    "• Выпускники → любые позиции\n\n"
                    "👉 Пройди диагностику, чтобы увидеть подходящие вакансии именно для тебя!")
    
    def _remote_info(self) -> str:
        return ("🏠 *Удалённая работа в МТС*\n\n"
                "Многие позиции поддерживают гибридный формат.\n\n"
                "*Полностью удалённо можно работать:*\n"
                "• Специалист по работе с корпоративными клиентами\n"
                "• Техническая поддержка\n"
                "• Некоторые IT-позиции (разработка, аналитика)\n\n"
                "*Гибридный формат (2-3 дня в офисе):*\n"
                "• Большинство офисных позиций\n"
                "• HR, маркетинг, продажи\n\n"
                "👉 Уточняй формат работы в конкретной вакансии!\n\n"
                "💡 Совет: При отклике можно уточнить у HR возможность удалёнки.")
    
    def _fallback_response(self, prompt: str) -> str:
        return ("🤔 *Я ещё учусь, но вот что могу:*\n\n"
                "📌 *Попробуй спросить:*\n"
                "• «Расскажи о МТС»\n"
                "• «Какая зарплата у стажёров?»\n"
                "• «Как пройти собеседование?»\n"
                "• «Что учить для Python?»\n"
                "• «Как откликнуться на вакансию?»\n\n"
                "Или воспользуйся кнопками меню! 👆\n\n"
                "Если я не понял — перефразируй вопрос 😊")
    
    def _enhance_response(self, response: str, intent: str) -> str:
        """Добавляет эмодзи и форматирование"""
        # Если ответ уже хорошо оформлен, не трогаем
        if response.startswith("*") or "```" in response:
            return response
        
        # Добавляем предложение спросить ещё
        if intent not in ["greeting", "feedback", "default"]:
            response += "\n\n❓ *Ещё вопросы?* Просто спроси!"
        
        return response
        
    def _context_aware_response(self, prompt: str, last_topic: str, last_question: str) -> str:
        """Универсальный ответ с учётом контекста"""
        
        context_responses = {
            "internship": "🔍 *Уточняю про стажировки:*\n\n" + self._internship_info(),
            "salary": "💰 *Уточняю про зарплаты:*\n\n" + self._salary_info(last_question),
            "vacancies": "📋 *Уточняю про вакансии:*\n\n" + self._vacancies_info(prompt),
            "interview": "📋 *Уточняю про собеседование:*\n\n" + self._interview_info(prompt),
            "skills": "📚 *Уточняю про обучение:*\n\n" + self._skills_info(prompt),
            "python": "🐍 *Уточняю про Python:*\n\n" + self._python_info(),
            "english": "🇬🇧 *Уточняю про английский:*\n\n" + self._english_info(),
            "how_to_apply": "📝 *Уточняю про отклик:*\n\n" + self._how_to_apply(),
            "career_growth": "🚀 *Уточняю про карьерный рост:*\n\n" + self._career_growth(),
            "remote": "🏠 *Уточняю про удалённую работу:*\n\n" + self._remote_info(),
        }
        
        if last_topic in context_responses:
            return context_responses[last_topic]
        
        return f"📌 *Продолжая тему {last_topic}:*\n\n{self._handle_intent(last_topic, prompt, None)}"

    def _salary_clarification_response(self, last_question: str) -> str:
        """Ответ на уточнение о зарплате"""
        return ("💰 *Уточняю про зарплату:*\n\n"
                "Вы спрашивали о зарплате. Давайте конкретнее:\n"
                "• Для *стажёров*: 50 000 - 70 000 ₽\n"
                "• Для *специалистов*: 80 000 - 120 000 ₽\n"
                "• Для *ведущих специалистов*: 120 000 - 180 000 ₽\n\n"
                "👉 Напишите конкретную позицию, и я скажу точнее!")

    def _apply_clarification_response(self) -> str:
        """Ответ на уточнение об отклике"""
        return ("📝 *Уточняю про отклик на вакансию:*\n\n"
                "Способы откликнуться:\n"
                "1️⃣ Через бота — нажми «📋 Вакансии» → выбери вакансию\n"
                "2️⃣ По почте — career@mts.ru\n"
                "3️⃣ На hh.ru\n\n"
                "👉 Хотите откликнуться прямо сейчас?")

    def _remote_company_response(self) -> str:
        """Ответ на вопрос об удалёнке в контексте компании"""
        return ("🏠 *Удалённая работа в МТС:*\n\n"
                "МТС поддерживает гибридный формат работы.\n\n"
                "*Где можно удалённо:*\n"
                "• Техническая поддержка\n"
                "• Некоторые IT-позиции\n"
                "• Специалисты по работе с клиентами\n\n"
                "👉 Уточняйте формат в конкретной вакансии!")
    
    # === АНАЛИЗ РЕЗЮМЕ ===
    def analyze_resume(self, resume_text: str) -> Dict:
        """Расширенный анализ резюме"""
        resume_lower = resume_text.lower()
        
        # Поиск навыков с весами
        skills_found = {}
        for skill, info in SKILLS_MAP.items():
            if skill in resume_lower:
                skills_found[skill] = info
        
        # Определение направления
        direction_scores = {
            "IT/Аналитика": 0,
            "Продажи": 0,
            "HR": 0,
            "Маркетинг": 0,
            "Управление": 0
        }
        
        for skill in skills_found:
            if skill in ["python", "sql", "аналитика"]:
                direction_scores["IT/Аналитика"] += 2
            elif skill in ["продажи"]:
                direction_scores["Продажи"] += 2
            elif skill in ["hr"]:
                direction_scores["HR"] += 2
            elif skill in ["маркетинг"]:
                direction_scores["Маркетинг"] += 2
            elif skill in ["management"]:
                direction_scores["Управление"] += 2
            elif skill in ["excel", "english"]:
                for d in direction_scores:
                    direction_scores[d] += 1
        
        best_direction = max(direction_scores, key=direction_scores.get)
        if direction_scores[best_direction] == 0:
            best_direction = "Не определён"
        
        # Оценка резюме (0-100)
        score = min(100, 30 + len(skills_found) * 10)
        
        # Рекомендации
        recommendations = []
        if "python" not in skills_found and best_direction == "IT/Аналитика":
            recommendations.append("📚 Изучи Python — основа для аналитики в МТС")
        if "sql" not in skills_found and best_direction == "IT/Аналитика":
            recommendations.append("🗄️ Освой SQL для работы с базами данных")
        if "excel" not in skills_found:
            recommendations.append("📊 Прокачай Excel — нужен везде")
        if "english" not in skills_found:
            recommendations.append("🇬🇧 Подтяни английский до B1 — откроет больше вакансий")
        
        if not recommendations:
            recommendations.append("✅ Отличный набор навыков! Ты готов к собеседованию!")
        
        return {
            "score": score,
            "direction": best_direction,
            "skills_found": list(skills_found.keys()),
            "recommendations": recommendations,
            "missing_skills": [s for s in SKILLS_MAP.keys() if s not in skills_found and direction_scores[best_direction] > 0][:5]
        }


    def smart_match_vacancy(self, user_interests: str, user_skills: str) -> list:
        """Умное сопоставление вакансий с интересами и навыками пользователя"""
        text = (user_interests + " " + user_skills).lower()
        
        # Импортируем вакансии (нужно передавать извне или загрузить)
        # Для простоты вернём базовые рекомендации
        recommendations = []
        
        if "python" in text or "аналитик" in text or "данные" in text:
            recommendations.append({"title": "Аналитик по внедрению AI", "requirements": ["Python", "SQL", "Аналитика"]})
        if "продаж" in text or "клиент" in text:
            recommendations.append({"title": "Стажер направление продаж и развития", "requirements": ["Коммуникабельность", "Навыки продаж"]})
        if "hr" in text or "рекрут" in text or "кадр" in text:
            recommendations.append({"title": "Стажер HR", "requirements": ["Рекрутинг", "Работа с людьми"]})
        if "инженер" in text or "кабель" in text or "сети" in text:
            recommendations.append({"title": "Стажёр-инженер по эксплуатации линейно-кабельных сооружений", "requirements": ["Техническое мышление", "Чтение схем"]})
        
        return recommendations

# === СОЗДАЁМ ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР ===
ai_assistant = MTSCareerAI()

# === ДЛЯ СБРОСА РЕЖИМОВ ===
def reset_ai_context(user_id: int = None):
    """Сбрасывает контекст AI для пользователя"""
    if user_id and user_id in ai_assistant.context:
        ai_assistant.context[user_id] = []
    return True


# === СОВМЕСТИМОСТЬ С СТАРЫМ КОДОМ ===
async def get_ai_response(prompt: str) -> str:
    """Обёртка для совместимости со старым кодом"""
    return ai_assistant.get_response(prompt)