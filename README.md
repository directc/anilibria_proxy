📺 AniLibria Proxy for Sonarr

AniLibria Proxy — это Torznab-совместимый прокси-сервер, который позволяет интегрировать Sonarr с торрент-трекером AniLibria.TOP.
Сервис автоматически преобразует API AniLibria в формат, понятный Sonarr, и обогащает поиск данными из Shikimori для нахождения аниме по альтернативным названиям.

✨ Возможности
🔍 Полноценный Torznab-интерфейс — Sonarr видит AniLibria как обычный индексер

🎯 Поиск по названиям — русские, английские, оригинальные и альтернативные названия

🔄 Интеграция с Shikimori — автоматическое получение всех вариантов названий аниме

📺 Поддержка сезонов и эпизодов — парсинг S1, E5, "сезон 2", "серия 13" и т.д.

📊 Фильтрация по качеству — 1080p, 720p, WEBRip, BDRip, HEVC, AVC

🧪 Тестовый режим — встроенные тестовые данные для проверки интеграции

🔧 Настройка в Sonarr
Settings → Indexers

Add Indexer → Torznab

Заполните поля:

Поле	Значение
URL	http://your-server:5001/api
API Key	anilibria123
Categories	5000,5070 (или 0 для всех)
Test — если всё ок, сохраняйте

📡 API Endpoints
Torznab API (/api)
Параметр	Описание	Пример
t	Тип запроса (caps, search, tvsearch)	t=caps
q	Поисковый запрос	q=One+Punch+Man
cat	Категории (5000, 5070)	cat=5000,5070
season	Номер сезона	season=1
ep	Номер эпизода	ep=5
apikey	Ключ API (anilibria123)	apikey=anilibria123
Тестовые эндпоинты
/test — главная тестовая страница со всеми примерами

/test-shikimori?q=Record of Ragnarok — проверка интеграции с Shikimori

Проверка Torznab
Протестируйте разные типы запросов:

bash
# Получение возможностей индексера
curl "http://localhost:5001/api?t=caps&apikey=anilibria123"

# Поиск аниме
curl "http://localhost:5001/api?t=search&q=One+Punch+Man&cat=5000&apikey=anilibria123"

# TV-поиск с сезоном и эпизодом
curl "http://localhost:5001/api?t=tvsearch&q=ванпанчмен&cat=5000&season=1&ep=5&apikey=anilibria123"

# Тестовый режим (возвращает демо-данные)
curl "http://localhost:5001/api?t=search&extended=1&cat=5000&apikey=anilibria123&limit=100&offset=0"

⚙️ Требования
Python 3.9 или выше

Flask 2.0+

requests

Доступ к интернету (для AniLibria и Shikimori API)

requirements.txt
text
flask>=2.0.0
requests>=2.25.0
