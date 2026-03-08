
# 🎬 AniLibria Proxy for Sonarr

[![Docker Pulls](https://img.shields.io/docker/pulls/gederfix/anilibria-proxy)](https://hub.docker.com/r/gederfix/anilibria-proxy)
[![Docker Image Size](https://img.shields.io/docker/image-size/gederfix/anilibria-proxy/latest)](https://hub.docker.com/r/gederfix/anilibria-proxy)

**AniLibria Proxy** — это Torznab-совместимый прокси-сервер для интеграции [Sonarr](https://sonarr.tv/) с [AniLibria.TOP](https://aniliberty.top).  
Автоматический поиск и загрузка аниме с любимыми озвучками через Shikimori.

---

## 🚀 Быстрый старт

### Docker Compose (рекомендуется)

Создайте `docker-compose.yml`:

```yaml
version: "3.8"

services:
  anilibria-proxy:
    image: gederfix/anilibria-proxy:latest
    container_name: anilibria-proxy
    restart: unless-stopped
    ports:
      - "5003:5001"
    environment:
      - TZ=Europe/Moscow
    volumes:
      - /etc/localtime:/etc/localtime:ro
    networks:
      - proxy
    security_opt:
      - no-new-privileges:true

networks:
  proxy:
    external: true
```

Запуск:
```bash
docker-compose up -d
```

### Docker CLI

```bash
docker run -d \
  --name anilibria-proxy \
  --restart unless-stopped \
  -p 5003:5001 \
  -e TZ=Europe/Moscow \
  -v /etc/localtime:/etc/localtime:ro \
  --security-opt no-new-privileges:true \
  gederfix/anilibria-proxy:latest
```

---

## 🔧 Настройка в Sonarr

1. **Settings → Indexers**
2. **Add Indexer → Torznab**
3. Заполните поля:

| Поле | Значение |
|------|----------|
| **URL** | `http://ip-адрес-сервера:5003/api` |
| **API Key** | `anilibria123` |
| **Categories** | `5000,5070` |

4. **Test** → **Save**

---

## ✨ Возможности

- ✅ Полноценный Torznab-интерфейс
- ✅ Интеграция с Shikimori (поиск по альтернативным названиям)
- ✅ Поддержка сезонов и эпизодов
- ✅ Тестовый режим для отладки
- ✅ Минималистичный Docker-образ
- ✅ Безопасный запуск (no-new-privileges)

---

## 📡 Проверка работы

```bash
# Тестовая страница
curl http://localhost:5003/test

# CAPS запрос
curl "http://localhost:5003/api?t=caps&apikey=anilibria123"

# Поиск аниме
curl "http://localhost:5003/api?t=search&q=One+Punch+Man&cat=5000&apikey=anilibria123"
```

---

## 🐳 Docker Hub

**Образ:** [gederfix/anilibria-proxy](https://hub.docker.com/r/gederfix/anilibria-proxy)

```bash
docker pull gederfix/anilibria-proxy:latest
```

---

## 📦 Теги

- `latest` — последняя стабильная версия

---

## 🔑 API Key

По умолчанию: **`anilibria123`**

---

## 📄 Лицензия

MIT

---

**⭐ Если проект полезен — поставьте звезду на GitHub и Docker Hub!**
```

---
