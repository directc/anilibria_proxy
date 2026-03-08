🚀 AniLibria Proxy
Умный прокси-парсер для интеграции AniLibria с Sonarr
Автоматический поиск, парсинг и загрузка аниме с любимыми озвучками

🔥 Зачем это нужно?

Sonarr — отличный инструмент для сериалов, но с аниме беда. А AniLibria — лучший источник аниме с профессиональной озвучкой, но у него нет интеграции с Sonarr.
AniLibria Proxy решает эту проблему:
🔄 Парсит API AniLibria в реальном времени
🔍 Отдаёт результаты в формате, понятном Sonarr (Torznab)
📦 Работает как полноценный Indexer в Sonarr

✨ Возможности
Функция	Описание
🔎 Поиск по названию	Ищет аниме на русском из Anilibria.top
🧩 Torznab API	Полная совместимость с Sonarr
⚡ Кэширование	Не долбит API AniLibria лишний раз

🔧 Настройка в Sonarr
Settings → Indexers
Add Indexer → Torznab
Параметры:
Поле	Значение
URL	http://localhost:5000/torznab (или IP своего сервера)
API Path	/torznab
API Key	оставь пустым (или укажи, если настроишь)
Categories	2000,2010,2020 (TV, Anime Series, Anime)
Save — готово! 🎉
