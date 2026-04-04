# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from ai_service import get_ai_response, ai_assistant

# Токен
TOKEN = '8694000995:AAHaw7LLlodRZTNMsxRy0lkg1POX0gJELIE'

# === AI МОДУЛЬ ===
import re
from collections import Counter

class AIAssistant:
    """Простой AI-помощник для анализа резюме и рекомендаций"""
    
    @staticmethod
    def analyze_resume(resume_text: str) -> dict:
        """Анализирует текст резюме и возвращает оценку + рекомендации"""
        resume_lower = resume_text.lower()
        
        skills_db = {
            "python": ["python", "django", "flask", "pandas", "numpy", "data science"],
            "sql": ["sql", "postgresql", "mysql", "баз данных", "database"],
            "excel": ["excel", "таблиц", "сводные", "vba"],
            "analytics": ["аналитик", "анализ", "данных", "статистик", "bi", "tableau"],
            "sales": ["продаж", "переговор", "клиент", "crm", "b2b", "b2c"],
            "hr": ["рекрут", "подбор", "hr", "кадр", "собесед"],
            "management": ["управлени", "лидер", "команд", "проект", "менедж"],
            "english": ["english", "английск", "ielts", "toefl", "b1", "b2", "c1"]
        }
        
        found_skills = {}
        for category, keywords in skills_db.items():
            found = []
            for kw in keywords:
                if kw in resume_lower:
                    found.append(kw)
            if found:
                found_skills[category] = found
        
        directions = {
            "IT/Аналитика": ["python", "sql", "analytics"],
            "Продажи": ["sales"],
            "HR": ["hr"],
            "Управление": ["management"],
            "Офисные навыки": ["excel", "english"]
        }
        
        best_direction = None
        max_score = 0
        for direction, categories in directions.items():
            score = sum(1 for cat in categories if cat in found_skills)
            if score > max_score:
                max_score = score
                best_direction = direction
        
        total_skills = len(found_skills)
        if total_skills >= 6:
            score = 85
        elif total_skills >= 4:
            score = 70
        elif total_skills >= 2:
            score = 50
        else:
            score = 30
        
        recommendations = []
        missing_skills = []
        
        if best_direction == "IT/Аналитика":
            if "python" not in found_skills:
                missing_skills.append("Python")
                recommendations.append("📚 Изучите Python — это основа для аналитики")
            if "sql" not in found_skills:
                missing_skills.append("SQL")
                recommendations.append("🗄️ Освойте SQL для работы с базами данных")
            if "analytics" not in found_skills:
                recommendations.append("📊 Пройдите курс по аналитике данных")
        elif best_direction == "Продажи":
            if "sales" not in found_skills:
                missing_skills.append("навыки продаж")
                recommendations.append("🤝 Развивайте навыки продаж и переговоров")
            recommendations.append("📈 Изучите CRM-системы")
        elif best_direction == "HR":
            if "hr" not in found_skills:
                missing_skills.append("HR")
                recommendations.append("👥 Изучите основы рекрутинга и HR")
        
        if not recommendations:
            recommendations = ["✅ У вас хороший набор навыков! Продолжайте развиваться."]
        
        suggested_vacancies = []
        if best_direction == "IT/Аналитика":
            suggested_vacancies = ["Аналитик по внедрению AI", "Направление сопровождения рабочих мест"]
        elif best_direction == "Продажи":
            suggested_vacancies = ["Стажер направление продаж и развития", "Специалист по работе с корпоративными клиентами"]
        elif best_direction == "HR":
            suggested_vacancies = ["Стажер HR", "Специалист по административно-хозяйственному обеспечению"]
        else:
            suggested_vacancies = ["Стажер направление продаж и развития", "Стажер HR"]
        
        return {
            "score": score,
            "found_skills": found_skills,
            "direction": best_direction or "Не определён",
            "recommendations": recommendations,
            "missing_skills": missing_skills,
            "suggested_vacancies": suggested_vacancies[:3]
        }
    
    @staticmethod
    def smart_match_vacancy(user_interests: str, user_skills: str) -> list:
        text = (user_interests + " " + user_skills).lower()
        scored_vacancies = []
        for vac in VACANCIES:
            vac_text = (vac['title'] + " " + " ".join(vac['requirements'])).lower()
            words = text.split()
            score = sum(1 for word in words if len(word) > 2 and word in vac_text)
            if "python" in vac_text and "python" in text:
                score += 3
            if "продаж" in vac_text and ("продаж" in text or "sales" in text):
                score += 3
            if "hr" in vac_text and ("hr" in text or "рекрут" in text):
                score += 3
            if score > 0:
                scored_vacancies.append((score, vac))
        scored_vacancies.sort(reverse=True, key=lambda x: x[0])
        return [vac for score, vac in scored_vacancies[:5]]
    
    @staticmethod
    def answer_question(question: str) -> str:
        q_lower = question.lower()
        answers = {
            "зарплата": "💰 Зарплата стажёров в МТС начинается от 50 000 ₽, специалистов — от 80 000 ₽. Зависит от направления и опыта.",
            "стажировка": "🎓 МТС предлагает оплачиваемые стажировки для студентов и выпускников. Длительность: 3-6 месяцев.",
            "как откликнуться": "📝 Выберите вакансию в разделе «Вакансии» и нажмите «Откликнуться», либо отправьте резюме на career@mts.ru",
            "собеседование": "📋 Подготовьте рассказ о себе, изучите компанию, подготовьте вопросы. Используйте наш «Чек-лист собеседования»!",
            "что учить": "🎓 В разделе «План обучения» выберите интересующее направление — AI подберёт курсы.",
            "python": "🐍 Python нужен для аналитики, автоматизации, бэкенда. Рекомендуем курс на Stepik: https://stepik.org/course/67",
            "english": "🇬🇧 Английский важен для IT и работы с документацией. Используйте Duolingo или курсы на Stepik.",
            "график": "⏰ Стажировки: гибкий график (20-40 часов). Полная занятость: 5/2, 8 часов.",
            "офис": "🏢 МТС имеет офисы по всей России. Возможна удалённая работа для некоторых позиций.",
            "карьера": "🚀 Карьерный рост: от стажёра до руководителя за 3-5 лет. МТС оплачивает обучение!"
        }
        for key, answer in answers.items():
            if key in q_lower:
                return answer + "\n\n❓ Есть ещё вопросы? Просто спросите!"
        return ("🤖 *AI-помощник МТС*\n\n"
                "Я ещё учусь, но могу помочь с вопросами о:\n"
                "• Зарплате и стажировках\n"
                "• Как откликнуться на вакансию\n"
                "• Подготовке к собеседованию\n"
                "• Что учить (Python, English)\n"
                "• Карьерном росте\n\n"
                "Или воспользуйтесь разделами меню! 👆")

ai = AIAssistant()

# Загружаем вакансии
with open('vacancies.json', 'r', encoding='utf-8') as f:
    VACANCIES = json.load(f)

# === ТЕСТ НА ПРОФОРИЕНТАЦИЮ ===
PROFESSIONAL_TEST = {
    'questions': [
        {'text': '1️⃣ Что тебе больше нравится делать?', 'options': ['📊 Анализировать данные и искать закономерности', '🤝 Общаться с людьми, помогать им', '💻 Создавать и программировать', '📈 Продавать и убеждать', '📝 Организовывать и планировать'], 'scores': {'Аналитик': 3, 'HR': 0, 'Программист': 0, 'Продажи': 0, 'Менеджер': 0}},
        {'text': '2️⃣ Какой предмет в школе/вузе тебе давался легче всего?', 'options': ['🧮 Математика/Информатика', '📖 Русский язык/Литература', '🌍 История/Обществознание', '🔬 Физика/Химия', '🗣️ Иностранный язык'], 'scores': {'Аналитик': 3, 'Программист': 3, 'Менеджер': 1, 'Продажи': 1, 'HR': 2}},
        {'text': '3️⃣ В какой обстановке ты чувствуешь себя комфортнее?', 'options': ['🖥️ За компьютером в тишине', '👥 В окружении людей, в шумной атмосфере', '🏃 В движении, в разных местах', '📚 В спокойной, структурированной обстановке', '🎨 В творческой, свободной атмосфере'], 'scores': {'Аналитик': 3, 'Программист': 3, 'Продажи': 2, 'HR': 2, 'Менеджер': 1}},
        {'text': '4️⃣ Что для тебя важнее в работе?', 'options': ['💰 Высокая зарплата', '🎯 Интересные задачи', '👨‍👩‍👧‍👦 Дружный коллектив', '⚖️ Баланс работы и жизни', '📈 Карьерный рост'], 'scores': {'Аналитик': 1, 'Программист': 2, 'Продажи': 3, 'HR': 2, 'Менеджер': 3}},
        {'text': '5️⃣ Как ты обычно решаешь проблемы?', 'options': ['🧠 Анализирую все варианты', '🤔 Советуюсь с другими', '💪 Действую быстро и решительно', '📚 Ищу готовое решение', '🎨 Придумываю что-то новое'], 'scores': {'Аналитик': 3, 'HR': 2, 'Продажи': 2, 'Менеджер': 2, 'Программист': 2}},
        {'text': '6️⃣ Какую роль ты чаще всего занимаешь в команде?', 'options': ['👑 Лидер, организую всех', '🤝 Помогаю решать конфликты', '💡 Генерирую идеи', '📊 Контролирую выполнение задач', '⚙️ Делаю техническую работу'], 'scores': {'Менеджер': 3, 'HR': 3, 'Программист': 1, 'Аналитик': 2, 'Продажи': 2}},
        {'text': '7️⃣ Что ты хочешь развивать в первую очередь?', 'options': ['🧠 Технические навыки', '🗣️ Коммуникабельность', '📈 Навыки продаж', '📊 Аналитическое мышление', '🎯 Управление проектами'], 'scores': {'Программист': 3, 'HR': 2, 'Продажи': 3, 'Аналитик': 3, 'Менеджер': 2}}
    ],
    'results': {
        'Аналитик': {'title': 'Аналитик', 'description': 'Тебе нравится работать с данными, искать закономерности и делать выводы.', 'vacancies': ['Аналитик по внедрению AI', 'Специалист по сопровождению закупок'], 'advice': 'Развивай навыки работы с Excel, SQL, Python. Изучай статистику.'},
        'Программист': {'title': 'IT-специалист/Программист', 'description': 'Тебе нравится создавать что-то новое, программировать и решать технические задачи.', 'vacancies': ['Стажёр-инженер', 'Направление сопровождения рабочих мест'], 'advice': 'Углубляй знания языков программирования, изучай алгоритмы и структуры данных.'},
        'Продажи': {'title': 'Специалист по продажам', 'description': 'У тебя отличные коммуникативные навыки, ты умеешь убеждать.', 'vacancies': ['Стажер направление продаж и развития', 'Продавец (Розничная сеть МТС)', 'Специалист по работе с корпоративными клиентами'], 'advice': 'Развивай навыки переговоров, изучай психологию продаж, CRM-системы.'},
        'HR': {'title': 'HR-специалист', 'description': 'Тебе нравится работать с людьми, помогать им развиваться и решать вопросы.', 'vacancies': ['Стажер HR', 'Специалист по административно-хозяйственному обеспечению'], 'advice': 'Изучай рекрутинг, трудовое право, HR-аналитику.'},
        'Менеджер': {'title': 'Менеджер/Руководитель', 'description': 'У тебя есть лидерские качества, ты умеешь организовывать процессы.', 'vacancies': ['Менеджер отдела недвижимости', 'Ведущий специалист по транспортному обслуживанию'], 'advice': 'Развивай навыки управления проектами, тайм-менеджмент, лидерство.'}
    }
}

INTERVIEW_CHECKLIST = """
📋 *Чек-лист подготовки к собеседованию в МТС*

*1. Исследование компании*
✅ Изучи сайт МТС и последние новости
✅ Посмотри соцсети компании (Telegram, VK)
✅ Узнай про продукты и услуги МТС
✅ Прочитай отзывы сотрудников

*2. Подготовка материалов*
✅ Распечатай резюме (2-3 экземпляра)
✅ Подготовь паспорт и другие документы
✅ Собери портфолио (если есть)
✅ Запиши контакты HR-специалиста

*3. Подготовка рассказа о себе*
✅ Составь рассказ на 2-3 минуты
✅ Расскажи про образование и опыт
✅ Объясни, почему хочешь работать в МТС
✅ Подготовь ответ: «Ваши сильные стороны»
✅ Подготовь ответ: «Ваши слабые стороны»

*4. Типичные вопросы на собеседовании*
✅ «Расскажите о вашем последнем месте работы»
✅ «Как вы справляетесь со стрессом?»
✅ «Где вы видите себя через 5 лет?»
✅ «Почему вы ушли с предыдущего места?»
✅ «Какие ваши достижения?»

*5. Вопросы работодателю (обязательно спросить!)*
✅ Какие задачи будут в первые 3 месяца?
✅ Как выглядит процесс адаптации?
✅ Какие возможности для обучения?
✅ Как часто проходят оценки эффективности?
✅ Какая корпоративная культура?

*6. Внешний вид*
✅ Одежда: деловой стиль (даже если онлайн)
✅ Прическа: аккуратная
✅ Улыбка и уверенный взгляд

*7. Технические моменты (для онлайн)*
✅ Проверь интернет-соединение
✅ Установи Zoom/Teams (заранее)
✅ Настрой камеру и микрофон
✅ Выбери спокойное место
✅ За час до собеседования проверь связь

*8. День собеседования*
✅ Приди за 10-15 минут до начала
✅ Выключи звук на телефоне
✅ Возьми с собой ручку и блокнот
✅ Будь вежлив с секретарём и HR
✅ После собеседования отправь благодарственное письмо

*💡 Бонус-советы:*
• Изучи ценности МТС (они на сайте)
• Подготовь кейс из своего опыта
• Не бойся задавать вопросы
• Будь честным и открытым
• Улыбайся! 😊
"""

def get_profession_result(scores: dict) -> dict:
    max_score = max(scores.values())
    for prof, score in scores.items():
        if score == max_score:
            return PROFESSIONAL_TEST['results'][prof]
    return PROFESSIONAL_TEST['results']['Аналитик']

RESUME_TEMPLATES = {
    "Аналитик": """
📝 *Шаблон резюме: Аналитик*

*О себе:* Люблю работать с данными, искать закономерности и делать выводы. Умею работать с Excel, SQL, Python.

*Опыт работы (пример):*
• Стажёр-аналитик — сбор и обработка данных, построение отчётов
• Участие в учебных проектах по анализу данных

*Навыки:*
• Excel (сводные таблицы, графики)
• SQL (SELECT, JOIN, GROUP BY)
• Python (pandas, numpy) — базовый уровень
• Английский язык — B1

*Достижения:* Победитель олимпиады по математике
""",
    "Программист": """
📝 *Шаблон резюме: Программист*

*О себе:* Люблю программировать и решать сложные задачи. Постоянно учусь новому.

*Опыт работы (пример):*
• Учебные проекты на Python (боты, парсеры)
• Участие в хакатонах

*Навыки:*
• Python (Django, Flask)
• Git, GitHub
• Базы данных (SQLite, PostgreSQL)
• Английский язык — чтение документации

*Портфолио:* github.com/username
""",
    "Продажи": """
📝 *Шаблон резюме: Специалист по продажам*

*О себе:* Коммуникабельный, целеустремлённый, умею находить подход к людям.

*Опыт работы (пример):*
• Консультант в магазине — помощь клиентам, работа с возражениями
• Участие в волонтёрских проектах (организация мероприятий)

*Навыки:*
• Навыки переговоров
• Работа с возражениями
• CRM-системы (изучение)
• Английский язык — A2
"""
}

FAQ_TEXT = """
❓ *Часто задаваемые вопросы*

*1. Как откликнуться на вакансию?*
→ Нажмите на вакансию → кнопка «Откликнуться» → выберите способ

*2. Есть ли стажировки для студентов?*
→ Да! В разделе «Все вакансии» есть позиции «Стажер»

*3. Можно ли работать удалённо?*
→ Некоторые позиции предполагают удалёнку. Уточняйте в вакансии

*4. Какая зарплата у стажёров?*
→ От 50 000 ₽ (зависит от направления)

*5. Нужно ли знать английский?*
→ Для IT-направлений желательно, для остальных — плюс

*6. Как подготовиться к собеседованию?*
→ Используйте раздел «Чек-лист собеседования»

*7. Есть ли обучение за счёт компании?*
→ Да, МТС оплачивает курсы для сотрудников

*Вопрос не из списка?* Напишите нам: career@mts.ru
"""

CAREER_PATHS = {
    'Аналитик по внедрению AI': {'skills': ['Python', 'SQL', 'Машинное обучение', 'Статистика', 'Английский'], 'plan': {'1 месяц': [{'name': 'Основы Python', 'url': 'https://stepik.org/course/67'}, {'name': 'Введение в SQL', 'url': 'https://stepik.org/course/51562'}], '3 месяца': [{'name': 'Библиотеки pandas и numpy', 'url': 'https://stepik.org/course/835'}, {'name': 'Основы статистики', 'url': 'https://stepik.org/course/76'}], '6 месяцев': [{'name': 'Машинное обучение', 'url': 'https://stepik.org/course/4852'}, {'name': 'Kaggle проекты', 'url': 'https://www.kaggle.com/'}]}, 'certificates': ['Data Science от Yandex', 'Аналитик данных от Stepik'], 'salary_after': 'от 120 000 ₽'},
    'Стажер направление продаж и развития': {'skills': ['Коммуникабельность', 'Навыки переговоров', 'Excel', 'CRM'], 'plan': {'1 месяц': [{'name': 'Основы продаж', 'url': 'https://www.coursera.org/learn/sales-training'}, {'name': 'Эффективная коммуникация', 'url': 'https://stepik.org/course/120722'}], '3 месяца': [{'name': 'Мастер переговоров', 'url': 'https://www.youtube.com/watch?v=ZVu7yqDkZ4A'}, {'name': 'Работа в CRM', 'url': ''}], '6 месяцев': [{'name': 'Управление клиентским опытом', 'url': ''}, {'name': 'Английский для бизнеса', 'url': 'https://www.duolingo.com/'}]}, 'certificates': ['Продажи от Google Digital Garage', 'Клиентоориентированность'], 'salary_after': 'от 60 000 ₽ + бонусы'},
    'Стажер HR': {'skills': ['Рекрутинг', 'Оценка персонала', 'Трудовое право', 'HR-метрики'], 'plan': {'1 месяц': [{'name': 'Основы HR', 'url': 'https://netology.ru/programs/hr-generalist'}, {'name': 'Поиск кандидатов', 'url': ''}], '3 месяца': [{'name': 'Собеседования и оценка', 'url': ''}, {'name': 'HR-аналитика', 'url': ''}], '6 месяцев': [{'name': 'Кадровое делопроизводство', 'url': ''}, {'name': 'Английский для HR', 'url': 'https://www.duolingo.com/'}]}, 'certificates': ['HR Generalist от Нетологии', 'Рекрутинг от Skillbox'], 'salary_after': 'от 65 000 ₽'},
}

def get_detailed_plan(vacancy_title: str) -> str:
    for title, path in CAREER_PATHS.items():
        if title.lower() in vacancy_title.lower():
            result = f"*🎓 План обучения для позиции: {title}*\n\n*💰 Ожидаемая зарплата:* {path['salary_after']}\n\n*📚 Необходимые навыки:*\n" + "\n".join([f"• {skill}" for skill in path['skills']]) + "\n\n*📅 План развития:*\n"
            for period, items in path['plan'].items():
                result += f"\n*{period}:*\n"
                for item in items:
                    if item['url']:
                        result += f"  • [{item['name']}]({item['url']})\n"
                    else:
                        result += f"  • {item['name']}\n"
            result += f"\n*🏆 Рекомендуемые сертификаты:*\n" + "\n".join([f"• {cert}" for cert in path['certificates']]) + "\n\n*💡 Совет:* Начни с первого месяца и уделяй 30-60 минут в день!"
            return result
    return None

AGE_FILTER = {'Стажер': (16, 25), 'Стажёр': (16, 25), 'Продавец': (18, 60), 'Юрист': (22, 60), 'Специалист': (20, 60), 'Менеджер': (23, 60), 'Аналитик': (21, 60), 'Ведущий': (25, 60)}
EDUCATION_FILTER = {'Стажер': ['школьник', 'студент колледжа', 'студент вуза'], 'Стажёр': ['школьник', 'студент колледжа', 'студент вуза'], 'Продавец': ['школьник', 'студент колледжа', 'студент вуза', 'выпускник'], 'Юрист': ['студент вуза', 'выпускник'], 'Специалист': ['студент вуза', 'выпускник'], 'Аналитик': ['студент вуза', 'выпускник'], 'Инженер': ['студент вуза', 'выпускник']}

LEARNING_RESOURCES = {
    'Python': [{'name': 'Курс «Python для начинающих» (Stepik)', 'url': 'https://stepik.org/course/67'}, {'name': 'YouTube: Тимофей Хирьянов', 'url': 'https://www.youtube.com/playlist?list=PLRDzFCPr95fK7tr47883DFUbm4GeOjjc0'}],
    'SQL': [{'name': 'Курс «SQL для начинающих» (Stepik)', 'url': 'https://stepik.org/course/51562'}, {'name': 'Интерактивный тренажёр SQL', 'url': 'https://sql-academy.org/ru/training'}],
    'Excel': [{'name': 'Курс «Excel для работы» (Stepik)', 'url': 'https://stepik.org/course/85'}, {'name': 'Продвинутый Excel', 'url': 'https://stepik.org/course/800'}],
    'Soft Skills': [{'name': 'Курс «Коммуникация» (Stepik)', 'url': 'https://stepik.org/course/120722'}, {'name': 'Курс «Тайм-менеджмент» (Coursera)', 'url': 'https://www.coursera.org/learn/time-management'}],
    'Английский': [{'name': 'Duolingo (бесплатно)', 'url': 'https://www.duolingo.com/'}, {'name': 'YouTube: English with Lucy', 'url': 'https://www.youtube.com/@EnglishwithLucy'}]
}

STATS_FILE = 'stats.json'
FAVORITES_FILE = 'favorites.json'

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'users': [], 'diagnostics': []}

def save_stats(stats):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def check_age_match(vacancy_title: str, age: int) -> bool:
    for key, (min_age, max_age) in AGE_FILTER.items():
        if key in vacancy_title:
            return min_age <= age <= max_age
    return True

def check_education_match(vacancy_title: str, education: str) -> bool:
    education_lower = education.lower()
    for key, allowed in EDUCATION_FILTER.items():
        if key in vacancy_title:
            return any(edu in education_lower for edu in allowed)
    return True

def filter_vacancies(age: int, education: str) -> list:
    filtered = []
    for vac in VACANCIES:
        if check_age_match(vac['title'], age) and check_education_match(vac['title'], education):
            filtered.append(vac)
    return filtered

def get_learning_plan(skills: str) -> str:
    skills_lower = skills.lower()
    recommendations = []
    topics = []
    if 'python' in skills_lower or 'программировани' in skills_lower:
        topics.append('Python')
    if 'sql' in skills_lower or 'баз' in skills_lower:
        topics.append('SQL')
    if 'excel' in skills_lower or 'таблиц' in skills_lower:
        topics.append('Excel')
    if 'продаж' in skills_lower:
        topics.append('Soft Skills')
    if 'hr' in skills_lower or 'рекрут' in skills_lower:
        topics.append('Soft Skills')
    topics.append('Английский')
    topics = list(set(topics))
    for topic in topics[:3]:
        if topic in LEARNING_RESOURCES:
            recommendations.append(f"\n*📚 {topic}:*")
            for resource in LEARNING_RESOURCES[topic][:2]:
                if resource['url']:
                    recommendations.append(f"  • [{resource['name']}]({resource['url']})")
                else:
                    recommendations.append(f"  • {resource['name']}")
    if not recommendations:
        recommendations = ["\n*📚 Базовые рекомендации:*", "  • [Курс «Коммуникация»](https://stepik.org/course/120722)", "  • [Английский на Duolingo](https://www.duolingo.com/)", "  • [Excel для начинающих](https://stepik.org/course/85)"]
    return '\n'.join(recommendations)

# === ОСНОВНЫЕ ФУНКЦИИ БОТА ===

async def start(update: Update, context):
    user_id = update.effective_user.id
    stats = load_stats()
    if user_id not in stats['users']:
        stats['users'].append(user_id)
        save_stats(stats)
    
    keyboard = [
        [KeyboardButton("📋 Вакансии"), KeyboardButton("🎯 Профориентация")],
        [KeyboardButton("📈 Карьерный трек"), KeyboardButton("📚 Обучение")],
        [KeyboardButton("🧠 AI-помощник"), KeyboardButton("📊 Моя статистика")],
        [KeyboardButton("❓ Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = ("🚀 *Привет! Я карьерный помощник МТС!*\n\n"
            "Я помогу тебе найти стажировку, подготовиться к собеседованию и построить карьеру в МТС.\n\n"
            "*📋 Что я умею:*\n\n"
            "• 📋 *Вакансии* — все актуальные позиции в МТС\n"
            "• 🎯 *Профориентация* — тест и диагностика, чтобы определить твоё направление\n"
            "• 📈 *Карьерный трек* — план развития от стажёра до руководителя\n"
            "• 📚 *Обучение* — курсы, чек-лист собеседования, шаблоны резюме\n"
            "• 🧠 *AI-помощник* — ответит на любой вопрос о карьере в МТС\n"
            "• 📊 *Моя статистика* — твои достижения и прогресс\n"
            "• ❓ *Помощь* — FAQ и информация о боте\n\n"
            "👇 *Просто нажми на кнопку ниже или напиши свой вопрос!*")
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_vacancies(update: Update, context):
    query = update.callback_query
    await query.answer()
    text = "*📋 Все вакансии МТС:*\n\n"
    keyboard = []
    for i, vac in enumerate(VACANCIES):
        text += f"{i+1}. *{vac['title']}*\n"
        if vac['requirements']:
            text += f"   📌 {vac['requirements'][0][:60]}...\n"
        text += "\n"
        keyboard.append([InlineKeyboardButton(f"📌 {vac['title'][:30]}", callback_data=f"vacancy_{i}")])
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    await query.edit_message_text(text[:4000], parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_vacancy_detail(update: Update, context):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split('_')[1])
    vac = VACANCIES[idx]
    text = f"*{vac['title']}*\n\n*📋 Требования:*\n" + "\n".join([f"• {req}" for req in vac['requirements']]) + "\n\n*💼 Обязанности:*\n" + "\n".join([f"• {resp}" for resp in vac['responsibilities']])
    favorites = load_favorites()
    user_id = query.from_user.id
    is_favorite = str(idx) in favorites.get(str(user_id), [])
    fav_text = "⭐ В избранном" if is_favorite else "☆ Добавить в избранное"
    keyboard = [[InlineKeyboardButton(fav_text, callback_data=f"favorite_{idx}")], [InlineKeyboardButton("📝 Откликнуться", callback_data=f"apply_{idx}")], [InlineKeyboardButton("🎓 План обучения", callback_data="learning_plan_menu")], [InlineKeyboardButton("🔙 Назад", callback_data="vacancies")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def toggle_favorite(update: Update, context):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split('_')[1])
    user_id = str(query.from_user.id)
    favorites = load_favorites()
    if user_id not in favorites:
        favorites[user_id] = []
    if str(idx) in favorites[user_id]:
        favorites[user_id].remove(str(idx))
        await query.answer("Удалено из избранного")
    else:
        favorites[user_id].append(str(idx))
        await query.answer("Добавлено в избранное")
    save_favorites(favorites)
    await show_vacancy_detail(update, context)

async def show_favorites(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    favorites = load_favorites()
    if user_id not in favorites or not favorites[user_id]:
        keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
        await query.edit_message_text("⭐ *У вас пока нет избранных вакансий*\n\nДобавьте их, открыв вакансию и нажав 'Добавить в избранное'", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    text = "⭐ *Ваши избранные вакансии:*\n\n"
    keyboard = []
    for idx in favorites[user_id]:
        idx = int(idx)
        vac = VACANCIES[idx]
        text += f"• *{vac['title']}*\n"
        keyboard.append([InlineKeyboardButton(f"📌 {vac['title'][:30]}", callback_data=f"vacancy_{idx}")])
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    await query.edit_message_text(text[:4000], parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def search_vacancies(update: Update, context):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    await query.edit_message_text("🔎 *Введите ключевые слова для поиска*\n\nНапример: Python, продажи, HR, инженер\n\nИли нажмите 'Главное меню' для возврата", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    context.user_data['search_mode'] = True

async def handle_search(update: Update, context):
    if not context.user_data.get('search_mode'):
        return False
    keyword = update.message.text.lower()
    context.user_data['search_mode'] = False
    found = []
    for i, vac in enumerate(VACANCIES):
        text = (vac['title'] + ' ' + ' '.join(vac['requirements'])).lower()
        if keyword in text:
            found.append((i, vac))
    if found:
        text = f"🔍 *Найдено {len(found)} вакансий по запросу '{keyword}':*\n\n"
        keyboard = []
        for i, vac in found[:10]:
            text += f"• *{vac['title']}*\n"
            keyboard.append([InlineKeyboardButton(f"📌 {vac['title'][:30]}", callback_data=f"vacancy_{i}")])
        keyboard.append([InlineKeyboardButton("🔍 Попробовать снова", callback_data="search")])
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
        await update.message.reply_text(text[:4000], parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [[InlineKeyboardButton("🔍 Попробовать снова", callback_data="search")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
        await update.message.reply_text(f"❌ По запросу '{keyword}' ничего не найдено.\n\nПопробуйте другие ключевые слова.", reply_markup=InlineKeyboardMarkup(keyboard))
    return True

async def diagnostic(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data['step'] = 'age'
    await query.edit_message_text("*🎯 Карьерная диагностика*\n\nОтветь на вопросы, и я подберу вакансии с учётом твоего возраста и образования:\n\n1️⃣ *Сколько тебе лет?* (напиши число)\n\nИли нажми 'Главное меню' для возврата", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def handle_diagnostic(update: Update, context):
    if not update.message or not update.message.text:
        return True
    step = context.user_data.get('step')
    if not step:
        return False
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Пожалуйста, напишите ответ.")
        return True
    if step == 'age':
        try:
            numbers = re.findall(r'\d+', text)
            if not numbers:
                raise ValueError
            age = int(numbers[0])
            if age < 14 or age > 100:
                await update.message.reply_text("❌ Пожалуйста, введите возраст от 14 до 100 лет.\n\nПримеры: `18`, `25`, `мне 30`", parse_mode='Markdown')
                return True
            context.user_data['age'] = age
            context.user_data['step'] = 'education'
            await update.message.reply_text("2️⃣ *Какое у тебя образование?*\n\nВарианты:\n• школьник\n• студент колледжа\n• студент вуза\n• выпускник\n\nНапиши свой вариант:", parse_mode='Markdown')
        except Exception:
            await update.message.reply_text("❌ Не понял возраст.\n\nНапиши число, например:\n• `18`\n• `25`\n• `мне 30`", parse_mode='Markdown')
            return True
    elif step == 'education':
        context.user_data['education'] = text
        context.user_data['step'] = 'interests'
        await update.message.reply_text("3️⃣ *Что тебе интересно?*\n\nНапиши сферы или навыки:\nНапример: Python, продажи, маркетинг, HR, аналитика...", parse_mode='Markdown')
    elif step == 'interests':
        context.user_data['interests'] = text
        context.user_data['step'] = None
        filtered = filter_vacancies(context.user_data['age'], context.user_data['education'])
        stats = load_stats()
        stats['diagnostics'].append({'user_id': update.effective_user.id, 'age': context.user_data['age'], 'education': context.user_data['education'], 'interests': text, 'filtered_count': len(filtered), 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        save_stats(stats)
        response = f"*🎉 Результаты диагностики*\n\n📊 *Твой профиль:*\n• Возраст: {context.user_data['age']} лет\n• Образование: {context.user_data['education']}\n• Интересы: {text}\n\n"
        if filtered:
            response += f"🔍 *Найдено {len(filtered)} подходящих вакансий:*\n\n"
            for i, vac in enumerate(filtered[:5]):
                response += f"{i+1}. *{vac['title']}*\n"
                if vac['requirements']:
                    response += f"   {vac['requirements'][0][:80]}...\n\n"
            if len(filtered) > 5:
                response += f"*...и ещё {len(filtered) - 5} вакансий*\n\n"
        else:
            response += "⚠️ *К сожалению, нет вакансий, точно подходящих под твои параметры.*\nНо посмотри все вакансии — возможно, что-то заинтересует!\n\n"
        response += "📌 *Что делать дальше:*\n• Посмотри все вакансии\n• Сохрани понравившиеся в избранное\n• Изучи план обучения"
        keyboard = [[InlineKeyboardButton("🔍 Посмотреть все вакансии", callback_data="vacancies")], [InlineKeyboardButton("🎓 План обучения", callback_data="learning_plan_menu")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    return True

async def learning_plan_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data['learning_mode'] = True
    await query.edit_message_text("*🎓 План обучения МТС*\n\nРасскажи, какие навыки ты хочешь развить, и я подберу курсы.\n\n📝 *Напиши:*\n• Python, SQL, Excel — для IT и аналитики\n• продажи, HR, маркетинг — для бизнеса\n• инженерия — для технических специальностей\n\nПример: *«Хочу выучить Python и английский»*\n\nИли нажми 'Главное меню' для возврата", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def handle_learning_plan(update: Update, context):
    if not context.user_data.get('learning_mode'):
        return False
    skills = update.message.text
    context.user_data['learning_mode'] = False
    plan = get_learning_plan(skills)
    keyboard = [[InlineKeyboardButton("🔍 Посмотреть вакансии", callback_data="vacancies")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    await update.message.reply_text(f"*🎓 Твой план обучения*\n\nНа основе твоих интересов: *{skills}*\n{plan}\n\n*💡 Совет:* Начни с одного курса и уделяй 30 минут в день!", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    return True

async def apply_vacancy(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data in ["apply_menu", "apply_chat", "apply_email"]:
        return
    if data.startswith("apply_"):
        try:
            idx = int(data.split('_')[1])
        except (IndexError, ValueError):
            await query.edit_message_text("❌ Ошибка: неверный формат данных", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))
            return
        vac = VACANCIES[idx]
        context.user_data['apply_vacancy'] = idx
        await query.edit_message_text(f"📝 *Отклик на вакансию: {vac['title']}*\n\nНапишите в ответном сообщении:\n1. Ваше имя\n2. Телефон\n3. Кратко о себе\n\nПример: Иван Иванов, +7-999-123-45-67, студент 3 курса", parse_mode='Markdown')
        context.user_data['apply_mode'] = True

async def handle_apply(update: Update, context):
    if not context.user_data.get('apply_mode'):
        return False
    text = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    idx = context.user_data.get('apply_vacancy')
    vac = VACANCIES[idx] if idx is not None else None
    apply_data = {'user_id': user_id, 'username': username, 'vacancy': vac['title'] if vac else "Unknown", 'message': text, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    with open('applications.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps(apply_data, ensure_ascii=False) + '\n')
    context.user_data['apply_mode'] = False
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    await update.message.reply_text("✅ *Ваш отклик отправлен!*\n\nHR-специалист свяжется с вами.\n\nСпасибо за интерес к МТС!", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    return True

async def navigator(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("*🧭 Карьерный навигатор МТС*\n\n*IT-трек:* Стажёр → Инженер → Ведущий инженер → Team Lead\n\n*Бизнес-трек:* Стажёр → Аналитик → Руководитель отдела\n\n*Клиентский трек:* Продавец → Специалист → Руководитель офиса\n\n🎓 *Для роста:* Используй раздел «План обучения»\n📈 *Для детального плана:* Используй раздел «Карьерный трек»", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def resume_templates_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("*📝 Выберите профессию для шаблона резюме:*", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📊 Аналитик", callback_data="resume_analyst")], [InlineKeyboardButton("💻 Программист", callback_data="resume_programmer")], [InlineKeyboardButton("🤝 Продажи", callback_data="resume_sales")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def show_resume_template(update: Update, context):
    query = update.callback_query
    await query.answer()
    template_type = query.data.split('_')[1]
    templates = {'analyst': RESUME_TEMPLATES["Аналитик"], 'programmer': RESUME_TEMPLATES["Программист"], 'sales': RESUME_TEMPLATES["Продажи"]}
    text = templates.get(template_type, RESUME_TEMPLATES["Аналитик"])
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Другой шаблон", callback_data="resume_templates")], [InlineKeyboardButton("📝 Откликнуться", callback_data="apply_menu")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def show_faq(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(FAQ_TEXT, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Чек-лист", callback_data="checklist")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def show_checklist(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(INTERVIEW_CHECKLIST, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎓 План обучения", callback_data="learning_plan_menu")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def user_dashboard(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    stats = load_stats()
    favorites = load_favorites()
    diagnostics_count = sum(1 for d in stats.get('diagnostics', []) if d.get('user_id') == user_id)
    favorites_count = len(favorites.get(str(user_id), []))
    text = f"📊 *Ваша статистика*\n\n👤 *Пользователь:* {update.effective_user.first_name}\n\n📝 *Пройдено диагностик:* {diagnostics_count}\n⭐ *Вакансий в избранном:* {favorites_count}\n\n---\n*Совет:* Пройдите диагностику, чтобы получить персональные рекомендации!"
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Пройти диагностику", callback_data="diagnostic")], [InlineKeyboardButton("⭐ Моё избранное", callback_data="favorites")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def about(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("*ℹ️ О проекте*\n\n🤖 *AI-карьерный помощник МТС*\n\n*Возможности:*\n• 🔍 Просмотр всех вакансий\n• 🎯 Диагностика с фильтрацией\n• 🔎 Умный поиск\n• ⭐ Избранное\n• 🎓 План обучения с курсами\n• 📈 Карьерный трек с планом\n• 📊 Карьерный навигатор\n\n*Версия:* 3.0\n*Контакты:* career@mts.ru", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def career_track_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    text = "*📈 Карьерный трек: выбери вакансию*\n\nЯ составлю для тебя подробный план обучения:\n• Какие навыки нужны\n• Что учить по месяцам\n• Какие сертификаты получить\n• Ожидаемую зарплату\n\n*Выбери интересующую позицию:*"
    keyboard = []
    for i, vac in enumerate(VACANCIES):
        if any(track in vac['title'] for track in CAREER_PATHS.keys()):
            keyboard.append([InlineKeyboardButton(f"📌 {vac['title'][:35]}", callback_data=f"track_{i}")])
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_career_track(update: Update, context):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split('_')[1])
    vac = VACANCIES[idx]
    plan = get_detailed_plan(vac['title'])
    if plan:
        await query.edit_message_text(plan, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад к трекам", callback_data="career_track")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))
    else:
        await query.edit_message_text(f"*📈 Для позиции '{vac['title']}'*\n\nК сожалению, у нас пока нет детального плана.\nНо ты можешь:\n• Посмотреть требования в разделе «Все вакансии»\n• Использовать раздел «План обучения»\n• Сохранить вакансию в избранное", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад к трекам", callback_data="career_track")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def start_prof_test(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data['prof_test'] = {'current_question': 0, 'scores': {'Аналитик': 0, 'Программист': 0, 'Продажи': 0, 'HR': 0, 'Менеджер': 0}}
    await show_question(update, context)

async def show_question(update: Update, context):
    test_data = context.user_data.get('prof_test')
    if not test_data:
        return
    q_idx = test_data['current_question']
    questions = PROFESSIONAL_TEST['questions']
    if q_idx >= len(questions):
        result = get_profession_result(test_data['scores'])
        text = f"*🎉 Результаты профориентации!*\n\n*Ваш тип:* {result['title']}\n\n*Описание:* {result['description']}\n\n*💼 Подходящие вакансии в МТС:*\n" + "\n".join([f"• {vac}" for vac in result['vacancies']]) + f"\n\n*📚 Рекомендации:* {result['advice']}\n\nХотите посмотреть эти вакансии?"
        keyboard = [[InlineKeyboardButton("🔍 Посмотреть вакансии", callback_data="vacancies")], [InlineKeyboardButton("🔄 Пройти тест заново", callback_data="prof_test")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
        if update.callback_query:
            await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data['prof_test'] = None
        return
    q = questions[q_idx]
    text = f"*🧠 Профориентационный тест*\n\n{q['text']}\n\n"
    keyboard = [[InlineKeyboardButton(option, callback_data=f"prof_answer_{i}")] for i, option in enumerate(q['options'])]
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_prof_answer(update: Update, context):
    query = update.callback_query
    await query.answer()
    answer_idx = int(query.data.split('_')[2])
    test_data = context.user_data.get('prof_test')
    if not test_data:
        await query.edit_message_text("Тест не найден. Начните заново.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))
        return
    q_idx = test_data['current_question']
    question = PROFESSIONAL_TEST['questions'][q_idx]
    scores_map = question['scores']
    for prof, points in scores_map.items():
        if points > 0:
            test_data['scores'][prof] += points
    test_data['current_question'] += 1
    await show_question(update, context)

async def select_vacancy_for_apply(update: Update, context):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split('_')[2])
    vac = VACANCIES[idx]
    context.user_data['apply_vacancy'] = idx
    pending = context.user_data.get('pending_apply')
    context.user_data['pending_apply'] = None
    if pending == 'chat':
        text = f"📱 *Отклик через чат*\n\n*Вы откликаетесь на вакансию:* {vac['title']}\n\nНапишите в ответном сообщении:\n1. Ваше имя и фамилию\n2. Ваш телефон\n3. Ссылку на резюме\n\nПример: Иван Иванов, +7-999-123-45-67"
        context.user_data['apply_mode'] = True
        await query.edit_message_text(text, parse_mode='Markdown')
    elif pending == 'email':
        text = f"📧 *Отклик по почте*\n\n*Вакансия:* {vac['title']}\n\nОтправьте резюме на:\n`career@mts.ru`\n\nВ теме письма: *«Отклик на вакансию»*"
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✉️ Скопировать email", callback_data="copy_email")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))
    else:
        await show_vacancy_detail(update, context)

async def apply_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📝 *Отклик на вакансию*\n\nВыберите способ:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📱 Написать в чат", callback_data="apply_chat")], [InlineKeyboardButton("📧 Отправить на почту", callback_data="apply_email")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def apply_chat(update: Update, context):
    query = update.callback_query
    await query.answer()
    if context.user_data.get('apply_vacancy') is None:
        text = "📱 *Отклик через чат*\n\nСначала выберите вакансию, на которую хотите откликнуться:\n\n"
        keyboard = [[InlineKeyboardButton(f"📌 {vac['title'][:35]}", callback_data=f"select_vacancy_{i}")] for i, vac in enumerate(VACANCIES[:10])]
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
        context.user_data['pending_apply'] = 'chat'
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    idx = context.user_data.get('apply_vacancy')
    vac = VACANCIES[idx]
    text = f"📱 *Отклик через чат*\n\n*Вы откликаетесь на вакансию:* {vac['title']}\n\nНапишите в ответном сообщении:\n1. Ваше имя и фамилию\n2. Ваш телефон\n3. Ссылку на резюме\n\nПример: Иван Иванов, +7-999-123-45-67"
    context.user_data['apply_mode'] = True
    await query.edit_message_text(text, parse_mode='Markdown')

async def apply_email(update: Update, context):
    query = update.callback_query
    await query.answer()
    if context.user_data.get('apply_vacancy') is None:
        text = "📧 *Отклик по почте*\n\nСначала выберите вакансию, на которую хотите откликнуться:\n\n"
        keyboard = [[InlineKeyboardButton(f"📌 {vac['title'][:35]}", callback_data=f"select_vacancy_{i}")] for i, vac in enumerate(VACANCIES[:10])]
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
        context.user_data['pending_apply'] = 'email'
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    idx = context.user_data.get('apply_vacancy')
    vac = VACANCIES[idx]
    text = f"📧 *Отклик по почте*\n\n*Вакансия:* {vac['title']}\n\nОтправьте резюме на:\n`career@mts.ru`\n\nВ теме письма укажите: *«Отклик на вакансию»*\n\nВ письме укажите:\n• Ваше имя и телефон\n• Желаемую позицию\n\nМы ответим в течение 3 рабочих дней!"
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✉️ Скопировать email", callback_data="copy_email")], [InlineKeyboardButton("🔙 Назад", callback_data="apply_menu")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def copy_email(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📧 *Email для отклика:*\n\n`career@mts.ru`\n\nВы можете скопировать этот адрес и отправить резюме.\n\nХорошего дня!", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def ai_analyze_resume(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data['ai_mode'] = 'analyze_resume'
    await query.edit_message_text("🤖 *AI-анализ резюме*\n\nОтправьте текст вашего резюме в ответном сообщении.\n\nAI проанализирует:\n• Ваши сильные стороны\n• Какие навыки подтянуть\n• Какие вакансии вам подходят\n\nПример: *«Я студент 3 курса, знаю Python, Excel, английский B1»*", parse_mode='Markdown')

async def ai_recommend_vacancies(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data['ai_mode'] = 'recommend_vacancies'
    await query.edit_message_text("🤖 *AI-рекомендации вакансий*\n\nНапишите о своих интересах и навыках.\n\nПример: *«Мне нравится анализировать данные, учу Python, хочу работать в IT»*", parse_mode='Markdown')

async def ai_chat(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data['ai_mode'] = 'chat'
    await query.edit_message_text("🤖 *AI-помощник МТС*\n\nЗадайте любой вопрос о карьере в МТС.\n\nПримеры вопросов:\n• Какая зарплата у стажёров?\n• Как подготовиться к собеседованию?\n• Что учить, чтобы стать аналитиком?", parse_mode='Markdown')

async def handle_ai_mode(update: Update, context):
    mode = context.user_data.get('ai_mode')
    if not mode:
        return False
    user_input = update.message.text
    await update.message.chat.send_action(action="typing")
    if mode == 'analyze_resume':
        result = ai.analyze_resume(user_input)
        response = f"🤖 *Результаты AI-анализа резюме*\n\n"
        if result['score'] >= 70:
            response += f"✅ *Оценка:* {result['score']}/100 — Хорошо!\n\n"
        elif result['score'] >= 50:
            response += f"📊 *Оценка:* {result['score']}/100 — Неплохо, есть куда расти\n\n"
        else:
            response += f"⚠️ *Оценка:* {result['score']}/100 — Требуется доработка\n\n"
        response += f"*🎯 Рекомендуемое направление:* {result['direction']}\n\n*📚 Рекомендации:*\n" + "\n".join([f"• {rec}" for rec in result['recommendations'][:3]])
        keyboard = [[InlineKeyboardButton("🔍 Посмотреть вакансии", callback_data="vacancies")], [InlineKeyboardButton("🎓 План обучения", callback_data="learning_plan_menu")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    elif mode == 'recommend_vacancies':
        recommended = ai.smart_match_vacancy(user_input, "")
        if recommended:
            response = f"🤖 *AI-рекомендации вакансий*\n\nНа основе ваших интересов:\n*«{user_input[:100]}»*\n\n*💼 Вам могут подойти:*\n"
            keyboard = []
            for vac in recommended[:5]:
                response += f"\n• *{vac['title']}*\n"
                for i, v in enumerate(VACANCIES):
                    if v.get('title') == vac['title']:
                        keyboard.append([InlineKeyboardButton(f"📌 {vac['title'][:30]}", callback_data=f"vacancy_{i}")])
                        break
        else:
            response = "🤖 *Не удалось подобрать вакансии*\n\nПопробуйте указать больше деталей."
            keyboard = []
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    elif mode == 'chat':
        answer = ai_assistant.get_response(user_input, user_id=update.effective_user.id)
        await update.message.reply_text(answer, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))
    context.user_data['ai_mode'] = None
    return True

async def ai_menu(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🧠 *AI-помощник МТС*\n\nИскусственный интеллект поможет вам:\n• 📄 Проанализировать резюме\n• 🎯 Подобрать подходящие вакансии\n• 💬 Ответить на вопросы о карьере\n\nВыберите действие:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤖 Анализ резюме", callback_data="ai_analyze")], [InlineKeyboardButton("🎯 Рекомендации вакансий", callback_data="ai_recommend")], [InlineKeyboardButton("💬 AI-помощник", callback_data="ai_chat")], [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]))

async def main_menu(update: Update, context):
    """Возврат в главное меню из инлайн-кнопок"""
    query = update.callback_query
    await query.answer()
    
    from telegram import ReplyKeyboardMarkup, KeyboardButton
    
    user_id = update.effective_user.id
    stats = load_stats()
    if user_id not in stats['users']:
        stats['users'].append(user_id)
        save_stats(stats)
    
    keyboard = [
        [KeyboardButton("📋 Вакансии"), KeyboardButton("🎯 Профориентация")],
        [KeyboardButton("📈 Карьерный трек"), KeyboardButton("📚 Обучение")],
        [KeyboardButton("🧠 AI-помощник"), KeyboardButton("📊 Моя статистика")],
        [KeyboardButton("❓ Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = (
        "🚀 *Привет! Я карьерный помощник МТС!*\n\n"
        "Я помогу тебе найти стажировку, подготовиться к собеседованию и построить карьеру в МТС.\n\n"
        "*📋 Что я умею:*\n\n"
        "• 📋 *Вакансии* — все актуальные позиции в МТС\n"
        "• 🎯 *Профориентация* — тест и диагностика, чтобы определить твоё направление\n"
        "• 📈 *Карьерный трек* — план развития от стажёра до руководителя\n"
        "• 📚 *Обучение* — курсы, чек-лист собеседования, шаблоны резюме\n"
        "• 🧠 *AI-помощник* — ответит на любой вопрос о карьере в МТС\n"
        "• 📊 *Моя статистика* — твои достижения и прогресс\n"
        "• ❓ *Помощь* — FAQ и информация о боте\n\n"
        "👇 *Просто нажми на кнопку ниже или напиши свой вопрос!*"
    )
    
    # Отправляем новое сообщение
    await query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    # Удаляем старое сообщение с инлайн-кнопками
    try:
        await query.message.delete()
    except:
        pass

# === ОБРАБОТЧИКИ ДЛЯ КНОПОК КЛАВИАТУРЫ ===

async def vacancies_menu_callback(update: Update, context):
    keyboard = [[InlineKeyboardButton("🔍 Все вакансии", callback_data="vacancies")], [InlineKeyboardButton("🔎 Поиск вакансий", callback_data="search")], [InlineKeyboardButton("📝 Откликнуться", callback_data="apply_menu")], [InlineKeyboardButton("⭐ Избранное", callback_data="favorites")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    await update.message.reply_text("*📋 Работа с вакансиями*\n\nВыберите действие:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def career_menu_callback(update: Update, context):
    keyboard = [[InlineKeyboardButton("🎯 Диагностика", callback_data="diagnostic")], [InlineKeyboardButton("🧠 Тест профориентации", callback_data="prof_test")], [InlineKeyboardButton("📊 Карьерный навигатор", callback_data="navigator")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    await update.message.reply_text("*🎯 Профориентация*\n\nПомогу тебе определиться с направлением:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def career_track_callback(update: Update, context):
    text = "*📈 Карьерный трек: выбери вакансию*\n\nЯ составлю для тебя подробный план обучения:\n• Какие навыки нужны\n• Что учить по месяцам\n• Какие сертификаты получить\n• Ожидаемую зарплату\n\n*Выбери интересующую позицию:*"
    keyboard = []
    for i, vac in enumerate(VACANCIES):
        if any(track in vac['title'] for track in CAREER_PATHS.keys()):
            keyboard.append([InlineKeyboardButton(f"📌 {vac['title'][:35]}", callback_data=f"track_{i}")])
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def learning_menu_callback(update: Update, context):
    keyboard = [[InlineKeyboardButton("🎓 План обучения", callback_data="learning_plan_menu")], [InlineKeyboardButton("📋 Чек-лист собеседования", callback_data="checklist")], [InlineKeyboardButton("📝 Шаблоны резюме", callback_data="resume_templates")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    await update.message.reply_text("*📚 Обучение и развитие*\n\nЧто тебя интересует?", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def ai_menu_callback(update: Update, context):
    keyboard = [[InlineKeyboardButton("🤖 Анализ резюме", callback_data="ai_analyze")], [InlineKeyboardButton("🎯 Рекомендации вакансий", callback_data="ai_recommend")], [InlineKeyboardButton("💬 AI-помощник", callback_data="ai_chat")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    await update.message.reply_text("🧠 *AI-помощник МТС*\n\nИскусственный интеллект поможет вам:\n• 📄 Проанализировать резюме\n• 🎯 Подобрать подходящие вакансии\n• 💬 Ответить на вопросы о карьере\n\nВыберите действие:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def dashboard_callback(update: Update, context):
    user_id = update.effective_user.id
    stats = load_stats()
    favorites = load_favorites()
    diagnostics_count = sum(1 for d in stats.get('diagnostics', []) if d.get('user_id') == user_id)
    favorites_count = len(favorites.get(str(user_id), []))
    text = f"📊 *Ваша статистика*\n\n👤 *Пользователь:* {update.effective_user.first_name}\n\n📝 *Пройдено диагностик:* {diagnostics_count}\n⭐ *Вакансий в избранном:* {favorites_count}\n\n---\n*Совет:* Пройдите диагностику, чтобы получить персональные рекомендации!"
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]))

async def help_menu_callback(update: Update, context):
    keyboard = [[InlineKeyboardButton("❓ FAQ", callback_data="faq")], [InlineKeyboardButton("ℹ️ О программе", callback_data="about")], [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    await update.message.reply_text("*❓ Помощь*\n\nЧем могу помочь?", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def main_menu_callback(update: Update, context):
    """Возврат в главное меню с подробным описанием кнопок"""
    from telegram import ReplyKeyboardMarkup, KeyboardButton
    
    user_id = update.effective_user.id
    stats = load_stats()
    if user_id not in stats['users']:
        stats['users'].append(user_id)
        save_stats(stats)
    
    keyboard = [
        [KeyboardButton("📋 Вакансии"), KeyboardButton("🎯 Профориентация")],
        [KeyboardButton("📈 Карьерный трек"), KeyboardButton("📚 Обучение")],
        [KeyboardButton("🧠 AI-помощник"), KeyboardButton("📊 Моя статистика")],
        [KeyboardButton("❓ Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = (
        "🚀 *Привет! Я карьерный помощник МТС!*\n\n"
        "Я помогу тебе найти стажировку, подготовиться к собеседованию и построить карьеру в МТС.\n\n"
        "*📋 Что я умею:*\n\n"
        "• 📋 *Вакансии* — все актуальные позиции в МТС\n"
        "• 🎯 *Профориентация* — тест и диагностика, чтобы определить твоё направление\n"
        "• 📈 *Карьерный трек* — план развития от стажёра до руководителя\n"
        "• 📚 *Обучение* — курсы, чек-лист собеседования, шаблоны резюме\n"
        "• 🧠 *AI-помощник* — ответит на любой вопрос о карьере в МТС\n"
        "• 📊 *Моя статистика* — твои достижения и прогресс\n"
        "• ❓ *Помощь* — FAQ и информация о боте\n\n"
        "👇 *Просто нажми на кнопку ниже или напиши свой вопрос!*"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

# === ЗАПУСК ===
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    
    app.add_handler(CallbackQueryHandler(show_vacancies, pattern="^vacancies$"))
    app.add_handler(CallbackQueryHandler(show_vacancy_detail, pattern="^vacancy_"))
    app.add_handler(CallbackQueryHandler(toggle_favorite, pattern="^favorite_"))
    app.add_handler(CallbackQueryHandler(show_favorites, pattern="^favorites$"))
    app.add_handler(CallbackQueryHandler(search_vacancies, pattern="^search$"))
    app.add_handler(CallbackQueryHandler(diagnostic, pattern="^diagnostic$"))
    app.add_handler(CallbackQueryHandler(learning_plan_menu, pattern="^learning_plan_menu$"))
    app.add_handler(CallbackQueryHandler(navigator, pattern="^navigator$"))
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    
    app.add_handler(CallbackQueryHandler(start_prof_test, pattern="^prof_test$"))
    app.add_handler(CallbackQueryHandler(handle_prof_answer, pattern="^prof_answer_"))
    app.add_handler(CallbackQueryHandler(show_checklist, pattern="^checklist$"))
    
    app.add_handler(CallbackQueryHandler(apply_menu, pattern="^apply_menu$"))
    app.add_handler(CallbackQueryHandler(apply_chat, pattern="^apply_chat$"))
    app.add_handler(CallbackQueryHandler(apply_email, pattern="^apply_email$"))
    app.add_handler(CallbackQueryHandler(copy_email, pattern="^copy_email$"))
    app.add_handler(CallbackQueryHandler(apply_vacancy, pattern="^apply_"))
    app.add_handler(CallbackQueryHandler(select_vacancy_for_apply, pattern="^select_vacancy_"))
    
    app.add_handler(CallbackQueryHandler(career_track_menu, pattern="^career_track$"))
    app.add_handler(CallbackQueryHandler(show_career_track, pattern="^track_"))
    
    app.add_handler(CallbackQueryHandler(resume_templates_menu, pattern="^resume_templates$"))
    app.add_handler(CallbackQueryHandler(show_resume_template, pattern="^resume_"))
    app.add_handler(CallbackQueryHandler(show_faq, pattern="^faq$"))
    app.add_handler(CallbackQueryHandler(user_dashboard, pattern="^dashboard$"))
    app.add_handler(CallbackQueryHandler(ai_menu, pattern="^ai_menu$"))
    app.add_handler(CallbackQueryHandler(ai_analyze_resume, pattern="^ai_analyze$"))
    app.add_handler(CallbackQueryHandler(ai_recommend_vacancies, pattern="^ai_recommend$"))
    app.add_handler(CallbackQueryHandler(ai_chat, pattern="^ai_chat$"))
    
    app.add_handler(MessageHandler(filters.Regex('^📋 Вакансии$'), vacancies_menu_callback))
    app.add_handler(MessageHandler(filters.Regex('^🎯 Профориентация$'), career_menu_callback))
    app.add_handler(MessageHandler(filters.Regex('^📈 Карьерный трек$'), career_track_callback))
    app.add_handler(MessageHandler(filters.Regex('^📚 Обучение$'), learning_menu_callback))
    app.add_handler(MessageHandler(filters.Regex('^🧠 AI-помощник$'), ai_menu_callback))
    app.add_handler(MessageHandler(filters.Regex('^📊 Моя статистика$'), dashboard_callback))
    app.add_handler(MessageHandler(filters.Regex('^❓ Помощь$'), help_menu_callback))
    app.add_handler(MessageHandler(filters.Regex('^🏠 Главное меню$'), main_menu_callback))
    
    async def message_handler(update: Update, context):
        user_text = update.message.text
        if context.user_data.get('search_mode'):
            await handle_search(update, context)
        elif context.user_data.get('apply_mode'):
            await handle_apply(update, context)
        elif context.user_data.get('learning_mode'):
            await handle_learning_plan(update, context)
        elif context.user_data.get('step'):
            await handle_diagnostic(update, context)
        elif context.user_data.get('ai_mode'):
            await handle_ai_mode(update, context)
        else:
            await update.message.chat.send_action(action="typing")
            answer = ai_assistant.get_response(user_text, user_id=update.effective_user.id)
            await update.message.reply_text(answer, parse_mode='Markdown')
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()