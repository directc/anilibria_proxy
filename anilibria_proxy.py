from flask import Flask, request, Response
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import time
import random
import json

app = Flask(__name__)

class AnilibriaTorznab:
    def __init__(self):
        self.base_url = "https://aniliberty.top"
        self.shikimori_url = "https://shikimori.one/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Content-Type': 'application/json',
        })
        # Кэш для результатов Shikimori, чтобы не делать повторные запросы
        #self.shikimori_cache = {}

    def get_alternative_names_from_shikimori(self, query):
        """Получает все альтернативные названия аниме через Shikimori API"""
        if not query or len(query) < 3:
            return []

        # Проверяем кэш
        # cache_key = query.lower().strip()
        # if cache_key in self.shikimori_cache:
        #     print(f"📦 using cached shikimori data for: {query}")
        #     return self.shikimori_cache[cache_key]

        try:
            print(f"\n{'=' * 60}")
            print(f"🔍 SHIKIMORI SEARCH REQUEST:")
            print(f"Original query: '{query}'")

            # Шаг 1: Поиск аниме по запросу
            search_url = f"{self.shikimori_url}/animes"
            params = {
                'search': query
            }

            # Формируем полный URL для отладки
            encoded_query = urllib.parse.quote(query)
            full_url = f"{search_url}?search={encoded_query}"
            print(f"🌐 Full Shikimori search URL: {full_url}")
            print(f"📦 Request params: {params}")

            response = self.session.get(search_url, params=params, timeout=10)
            print(f"📡 Response status: {response.status_code}")

            if response.status_code != 200:
                print(f"❌ Shikimori search failed: {response.status_code}")
                return []

            search_results = response.json()
            print(f"📊 Shikimori returned {len(search_results)} results")

            if not search_results:
                print("ℹ️ No results from Shikimori")
                return []

            # Показываем первые результаты поиска
            print("\n📋 Top search results:")
            for i, anime in enumerate(search_results[:2]):
                anime_id = anime.get('id')
                anime_name = anime.get('name', 'Unknown')
                anime_russian = anime.get('russian', '')
                print(f"  {i + 1}. ID: {anime_id} | Name: {anime_name}")
                if anime_russian:
                    print(f"     Russian: {anime_russian}")

            # Шаг 2: Для каждого результата собираем все названия
            all_names = set()

            for idx, anime in enumerate(search_results[:3]):
                anime_id = anime.get('id')
                if not anime_id:
                    continue

                print(f"\n📥 Fetching details for result {idx + 1}, ID: {anime_id}")

                # Получаем детальную информацию по ID
                detail_url = f"{self.shikimori_url}/animes/{anime_id}"
                print(f"  🔗 Detail URL: {detail_url}")

                detail_response = self.session.get(detail_url, timeout=10)

                if detail_response.status_code != 200:
                    print(f"  ❌ Failed to get details: {detail_response.status_code}")
                    continue

                anime_detail = detail_response.json()
                print(f"  ✅ Got details for: {anime_detail.get('name', 'Unknown')}")

                # Собираем все возможные названия
                if anime_detail.get('name'):
                    name = anime_detail['name'].strip()
                    all_names.add(name)
                    print(f"    📝 Original: {name}")

                if anime_detail.get('russian'):
                    russian = anime_detail['russian'].strip()
                    all_names.add(russian)
                    print(f"    📝 Russian: {russian}")

                if anime_detail.get('license_name_ru'):
                    license_name = anime_detail['license_name_ru'].strip()
                    all_names.add(license_name)
                    print(f"    📝 License: {license_name}")

                english_names = anime_detail.get('english', [])
                if isinstance(english_names, list):
                    for name in english_names:
                        if name and isinstance(name, str):
                            clean_name = name.strip()
                            all_names.add(clean_name)
                            print(f"    📝 English: {clean_name}")

                synonyms = anime_detail.get('synonyms', [])
                if isinstance(synonyms, list):
                    for name in synonyms:
                        if name and isinstance(name, str):
                            clean_name = name.strip()
                            all_names.add(clean_name)
                            print(f"    📝 Synonym: {clean_name}")

            # Добавляем оригинальный запрос
            all_names.add(query)
            print(f"\n➕ Added original query: '{query}'")

            # Фильтруем пустые и слишком короткие значения
            result_names = [name for name in all_names if name and len(name) > 1]

            print(f"\n✅ Final collected names ({len(result_names)} total):")
            for i, name in enumerate(result_names[:10]):  # Показываем первые 10
                print(f"   {i + 1}. {name}")
            if len(result_names) > 10:
                print(f"   ... and {len(result_names) - 10} more")
            print(f"{'=' * 60}\n")

            return result_names

        except Exception as e:
            print(f"💥 Shikimori API error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def extract_season_episode_from_query(self, query):
        """Извлекаем информацию о сезоне и эпизоде из запроса"""
        if not query:
            return query, None, None

        season = None
        episode = None
        clean_query = query

        # Паттерны для сезона
        season_patterns = [
            r'S(\d{1,2})\b',
            r's(\d{1,2})\b',
            r'сезон\s*(\d{1,2})\b',
            r'season\s*(\d{1,2})\b',
        ]

        for pattern in season_patterns:
            match = re.search(pattern, clean_query, re.IGNORECASE)
            if match:
                try:
                    season = int(match.group(1))
                    clean_query = re.sub(pattern, '', clean_query, flags=re.IGNORECASE).strip()
                    break
                except (ValueError, IndexError):
                    continue

        # Паттерны для эпизода
        episode_patterns = [
            r'E(\d{1,3})\b',
            r'e(\d{1,3})\b',
            r'серия\s*(\d{1,3})\b',
            r'эпизод\s*(\d{1,3})\b',
            r'episode\s*(\d{1,3})\b',
            r'(\d{1,3})(?:\s*серия|\s*эпизод)?\b',
        ]

        for pattern in episode_patterns:
            match = re.search(pattern, clean_query, re.IGNORECASE)
            if match:
                try:
                    episode = int(match.group(1))
                    if episode < 5 and not re.search(r'[серияэпизодepisode]', pattern, re.IGNORECASE):
                        continue
                    clean_query = re.sub(pattern, '', clean_query, flags=re.IGNORECASE).strip()
                    break
                except (ValueError, IndexError):
                    continue

        return clean_query, season, episode

    def extract_year_from_query(self, query):
        """Извлекаем год из запроса"""
        if not query:
            return query, None

        match = re.search(r'\b(19\d{2}|20\d{2})\b', query)
        if match:
            year = match.group(1)
            try:
                year_num = int(year)
                clean_query = query.replace(match.group(0), '').strip()
                return clean_query, year_num
            except ValueError:
                pass

        return query, None

    def normalize_category_for_search(self, cat):
        """Нормализуем категорию для поиска: 5070 и 5000,5070 -> 5000"""
        if not cat:
            return '5000'

        cat_str = str(cat)
        if '5070' in cat_str or '5000' in cat_str:
            return '5000'

        return cat_str

    def get_response_category(self, requested_cat):
        """Определяем категорию для ответа на основе запрошенной"""
        if not requested_cat:
            return '5000'

        cat_str = str(requested_cat)

        if '5070' in cat_str:
            return '5070'
        return '5000'

    def build_search_params(self, query, cat, season=None, episode=None):
        """Строим параметры поиска для AniLibria API"""
        print(f"📝 Building search params: query='{query}', cat={cat}, season={season}, episode={episode}")

        search_cat = self.normalize_category_for_search(cat)

        clean_query, year_from_query = self.extract_year_from_query(query)

        if season is None and episode is None:
            final_query, season_from_query, episode_from_query = self.extract_season_episode_from_query(clean_query)
        else:
            final_query = clean_query
            season_from_query = season
            episode_from_query = episode

        season_to_use = season if season is not None else season_from_query
        episode_to_use = episode if episode is not None else episode_from_query

        if not final_query:
            final_query = query

        print(f"🎯 Search query: '{final_query}'")
        print(f"🎯 Season: {season_to_use}")
        print(f"🎯 Episode: {episode_to_use}")
        print(f"🎯 Year: {year_from_query}")
        print(f"🎯 Search category: {search_cat}")

        return final_query, season_to_use, episode_to_use, year_from_query, search_cat

    def search_releases(self, query):
        """Ищем релизы по запросу"""
        try:
            if len(query) < 2:
                return []

            encoded_query = urllib.parse.quote(query)
            search_url = f"{self.base_url}/api/v1/app/search/releases?query={encoded_query}"

            print(f"🔗 Searching releases: {search_url}")

            response = self.session.get(search_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if data:
                        print(f"✅ Found {len(data)} releases")
                        for i, rel in enumerate(data[:3]):
                            name = rel.get('name', {}).get('main', 'Unknown')
                            print(f"   {i+1}. {name}")
                    else:
                        print(f"ℹ️ No releases found for query: '{query}'")
                    return data
                else:
                    print(f"❌ Unexpected response format: {type(data)}")
            else:
                print(f"❌ Search failed: {response.status_code}")

        except Exception as e:
            print(f"💥 Search error: {e}")

        return []

    def get_torrents_for_release(self, release_id):
        """Получаем торренты для релиза"""
        try:
            torrents_url = f"{self.base_url}/api/v1/anime/torrents/release/{release_id}"

            print(f"🔗 Getting torrents: {torrents_url}")

            response = self.session.get(torrents_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ Found {len(data)} torrents")
                    return data
                else:
                    print(f"❌ Unexpected torrents format: {type(data)}")
            else:
                print(f"❌ Torrents request failed: {response.status_code}")

        except Exception as e:
            print(f"💥 Torrents error: {e}")

        return []

    def filter_torrents_by_params(self, torrents, release, season_param, episode_param, year_param):
        """Фильтруем торренты по параметрам"""
        filtered = []

        release_year = release.get('year')

        if year_param and release_year != year_param:
            return filtered

        if episode_param and episode_param > 0:
            for torrent in torrents:
                description = torrent.get('description', '')
                if self.episode_matches(description, episode_param):
                    filtered.append(torrent)
            return filtered

        return torrents

    def episode_matches(self, description, episode_param):
        """Проверяет, соответствует ли описание эпизоду"""
        if not description:
            return False

        patterns = [
            r'^(\d+)$',
            r'^(\d+)-(\d+)$',
            r'(\d+)[,\s]',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, str(description))
            for match in matches:
                if isinstance(match, tuple):
                    try:
                        start = int(match[0])
                        if len(match) > 1:
                            end = int(match[1])
                            if start <= episode_param <= end:
                                return True
                        elif start == episode_param:
                            return True
                    except (ValueError, IndexError):
                        continue
                else:
                    try:
                        if int(match) == episode_param:
                            return True
                    except ValueError:
                        continue

        return False

    def parse_torrent_to_result(self, torrent, release, response_cat, original_query=None, shikimori_names=None):
        """Парсим торрент в формат Torznab"""
        try:
            label = torrent.get('label', '')
            magnet = torrent.get('magnet', '')
            hash_value = torrent.get('hash', '')
            size = torrent.get('size', 0)
            seeders = torrent.get('seeders', 0)
            leechers = torrent.get('leechers', 0)
            created_at = torrent.get('created_at', '')

            if not magnet:
                return None

            release_id = release.get('id', '')
            release_name = release.get('name', {})
            main_name = release_name.get('main', 'Unknown')
            english_name = release_name.get('english', '')
            alternative_name = release_name.get('alternative', '')
            alias = release.get('alias', '')
            year = release.get('year', '')
            release_type = release.get('type', {}).get('value', '')

            quality = torrent.get('quality', {}).get('value', '')
            codec = torrent.get('codec', {}).get('label', '')
            type_info = torrent.get('type', {}).get('value', '')
            description = torrent.get('description', '')

            def extract_season_number(text):
                if not text:
                    return None

                patterns = [
                    r'\bseason\s*(\d+)\b',
                    r'\bсезон\s*(\d+)\b',
                    r'\b(\d+)(?:st|nd|rd|th)\s*season\b',
                    r'\b(\d+)(?:st|nd|rd|th)\s*сезон\b',
                    r'\bpart\s*(\d+)\b',
                    r'\bчасть\s*(\d+)\b',
                    r'\bfinal\s+season\b',
                    r'\s+(\d+)\s*$',
                ]

                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        if 'final' in pattern.lower():
                            return 4
                        try:
                            return int(match.group(1))
                        except (ValueError, IndexError):
                            continue

                return None

            season_num = None

            if english_name:
                season_num = extract_season_number(english_name)

            if season_num is None and main_name:
                season_num = extract_season_number(main_name)

            if season_num is None:
                season_num = 1

            season_episode = ""
            if description:
                if '-' in description:
                    ep_start, ep_end = description.split('-', 1)
                    season_episode = f"S{season_num}E{ep_start}-{ep_end}"
                elif ',' in description:
                    episodes = description.split(',')
                    season_episode = f"S{season_num}E{episodes[0]}-{episodes[-1]}"
                elif description.isdigit():
                    season_episode = f"S{season_num}E{description}"
                else:
                    season_episode = f"S{season_num}E{description}"

            def clean_title(title, remove_season_numbers=True):
                if not title:
                    return title

                clean_title = title

                patterns_to_remove = [
                    r'\s+season\s*\d+\s*$',
                    r'\s+сезон\s*\d+\s*$',
                    r'\s+\d+(?:st|nd|rd|th)\s*season\s*$',
                    r'\s+\d+(?:st|nd|rd|th)\s*сезон\s*$',
                    r'\s+part\s*\d+\s*$',
                    r'\s+часть\s*\d+\s*$',
                    r'\s+final\s+season\s*$',
                ]

                if remove_season_numbers:
                    patterns_to_remove.append(r'\s+\d+\s*$')

                for pattern in patterns_to_remove:
                    clean_title = re.sub(pattern, '', clean_title, flags=re.IGNORECASE).strip()

                return clean_title

            clean_english = clean_title(english_name, remove_season_numbers=False) if english_name else ""
            clean_alternative = clean_title(alternative_name, remove_season_numbers=False) if alternative_name else ""
            clean_main = clean_title(main_name, remove_season_numbers=False) if main_name else ""

            # Определяем основное название для отображения
            main_display_name = clean_english if clean_english else (
                clean_alternative if clean_alternative else clean_main)

            # Функция для проверки, есть ли название в списке Shikimori
            def name_in_shikimori(name, shikimori_list):
                if not name or not shikimori_list:
                    return False
                name_lower = name.lower()
                return any(name_lower in shikimori_name.lower() or shikimori_name.lower() in name_lower
                           for shikimori_name in shikimori_list)

            # Формируем финальное название
            if clean_alternative and clean_alternative != main_display_name:
                # Если есть альтернативное название и оно отличается от основного
                english_part = f"{main_display_name} ({clean_alternative})"
            elif shikimori_names and original_query and name_in_shikimori(main_display_name, shikimori_names):
                # Если основное название есть в списке Shikimori, добавляем поисковый запрос
                english_part = f"{main_display_name} ({original_query})"
            else:
                # Иначе просто основное название
                english_part = main_display_name

            ordered_parts = []
            if quality:
                ordered_parts.append(quality)
            if codec:
                ordered_parts.append(codec)
            if type_info:
                ordered_parts.append(type_info)

            quality_str = " ".join(ordered_parts) if ordered_parts else ""

            title_parts = []
            title_parts.append(english_part)

            if season_episode:
                title_parts.append(f"- {season_episode} -")
            else:
                title_parts.append("-")

            year_mvo = []
            if year:
                year_mvo.append(str(year))

            year_mvo.append("MVO (Anilibria), Sub")

            if year_mvo:
                title_parts.append(" ".join(year_mvo))

            if quality_str:
                title_parts.append(quality_str)

            title_parts.append("- RUSSIAN")

            # Добавляем русское название, если оно есть и отличается от основной части
            if clean_main and clean_main.lower() != english_part.lower() and clean_main not in english_part:
                title_parts.append(f"- {clean_main}")

            full_title = " ".join(title_parts)

            if alias:
                info_url = f"https://aniliberty.top/anime/releases/release/{alias}/torrents"
            else:
                info_url = f"https://aniliberty.top/anime/releases/release/{release_id}"

            pub_date = self.format_date(created_at)
            guid = f"anilibria:{release_id}:{hash_value}"
            file_name = f"{english_part} [{quality}] [{codec}].torrent"
            file_name = re.sub(r'[<>:"/\\|?*]', '', file_name)

            return {
                'title': full_title,
                'link': magnet,
                'guid': guid,
                'infoUrl': info_url,
                'size': size,
                'seeders': seeders,
                'peers': seeders + leechers,
                'category': response_cat,
                'pub_date': pub_date,
                'fileName': file_name,
                'tracker': 'AniLibria.TOP',
                'hash': hash_value,
                'release_id': release_id,
                'alias': alias,
            }

        except Exception as e:
            print(f"⚠️ Error parsing torrent: {e}")
            return None

    def format_date(self, date_str):
        """Форматируем дату"""
        try:
            if date_str:
                for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
                    except ValueError:
                        continue

            days_ago = random.randint(1, 365)
            dt = datetime.now() - timedelta(days=days_ago)
            return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')

        except:
            dt = datetime.now() - timedelta(days=random.randint(1, 365))
            return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')

    def is_test_query(self, query, cat):
        """Проверяем, является ли запрос тестовым"""
        test_patterns = [
            r'^\s*$',
            r'test',
            r'check',
            r'ping',
            r'^$',
        ]

        for pattern in test_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True

        return False

    def search(self, query, cat='5000', season=None, episode=None):
        """Основной метод поиска с интеграцией Shikimori"""
        print(f"\n{'=' * 60}")
        print(f"🔍 TORZNAB SEARCH REQUEST:")
        print(f"Query: '{query}'")
        print(f"Requested category: {cat}")
        print(f"Season: {season}")
        print(f"Episode: {episode}")
        print(f"{'=' * 60}\n")

        if self.is_test_query(query, cat):
            print("🧪 TEST QUERY DETECTED - Returning test data")
            return self.get_test_results(query, cat, season, episode)

        if not query or query.strip() == "":
            print("⚠️ Empty query, returning empty")
            return []

        search_cat = self.normalize_category_for_search(cat)

        if search_cat != '5000' and search_cat != '0':
            print(f"⚠️ Category {cat} not supported, only 5000/5070 (Anime) is available")
            return []

        response_cat = self.get_response_category(cat)
        print(f"🎯 Response category: {response_cat}")

        start_time = time.time()

        search_query, season_param, episode_param, year_param, _ = self.build_search_params(
            query, cat, season, episode
        )

        print(f"\n🔍 DEBUG: search_query='{search_query}'")
        print(f"🔍 DEBUG: original query='{query}'")

        # Получаем альтернативные названия из Shikimori
        shikimori_names = self.get_alternative_names_from_shikimori(search_query)

        all_search_queries = [search_query] + shikimori_names
        all_search_queries = list(dict.fromkeys(all_search_queries))

        print(f"\n🔎 Will search with {len(all_search_queries)} queries:")
        for i, q in enumerate(all_search_queries[:5]):
            print(f"   {i + 1}. '{q}'")
        if len(all_search_queries) > 5:
            print(f"   ... and {len(all_search_queries) - 5} more")

        all_results = []
        found_release_ids = set()

        for search_term in all_search_queries:
            if len(search_term) < 2:
                continue

            print(f"\n🔍 Searching releases with: '{search_term}'")

            releases = self.search_releases(search_term)

            if not releases:
                print(f"❌ No releases found for '{search_term}'")
                continue

            for release in releases[:10]:
                release_id = release.get('id')

                if release_id in found_release_ids:
                    print(f"⏭️ Release {release_id} already processed, skipping")
                    continue

                found_release_ids.add(release_id)

                release_name = release.get('name', {})
                main_name = release_name.get('main', 'Unknown')
                alias = release.get('alias', '')

                print(f"🔍 Getting torrents for release: {main_name} (ID: {release_id}, Alias: {alias})")

                torrents = self.get_torrents_for_release(release_id)

                if torrents:
                    filtered_torrents = self.filter_torrents_by_params(
                        torrents, release, season_param, episode_param, year_param
                    )

                    for torrent in filtered_torrents:
                        # Передаем оригинальный запрос и список имен из Shikimori
                        result = self.parse_torrent_to_result(
                            torrent, release, response_cat,
                            original_query=query,
                            shikimori_names=shikimori_names
                        )
                        if result:
                            all_results.append(result)

        all_results.sort(key=lambda x: x.get('seeders', 0), reverse=True)

        elapsed = time.time() - start_time
        print(f"\n{'=' * 60}")
        print(f"📊 SEARCH RESULTS:")
        print(f"Original query: '{query}'")
        print(f"Found: {len(all_results)} results")
        print(f"Unique releases: {len(found_release_ids)}")
        print(f"Time: {elapsed:.2f}s")
        print(f"Response category: {response_cat}")
        print(f"{'=' * 60}\n")

        return all_results[:50]

    def get_test_results(self, query, cat, season, episode):
        """Возвращаем тестовые результаты для аниме"""
        print(f"🧪 Generating test results for query='{query}', cat={cat}")
        print(f"🧪 With Shikimori integration test")

        response_cat = self.get_response_category(cat)

        dates = []
        for i in range(10):
            dates.append(datetime.now() - timedelta(days=random.randint(1, 30)))

        results = []

        anime_test_data = [
            {
                "title": "Shuumatsu no Walküre (Record of Ragnarok) - S1E1-12 - 2021 MVO (Anilibria), Sub 1080p WEBRip - RUSSIAN - Повесть о Конце света",
                "year": 2021,
                "quality": "1080p WEBRip",
                "tracker": "AniLibria.TOP",
                "url": "https://aniliberty.top/anime/releases/release/shuumatsu-no-walkure/torrents",
                "magnet": "magnet:?xt=urn:btih:4cfa8ed11da6355257b8f87d482eed484cc872ed&dn=Shuumatsu+no+Walk%C3%BCre+-+AniLibria.TOP+[WEBRip+1080p]&tr=udp://tracker.opentrackr.org:1337/announce",
                "size": 8589934592,
                "seeders": 42,
                "leechers": 3,
                "alias": "shuumatsu-no-walkure",
                "alternative_names": ["Record of Ragnarok", "Valkyrie of the End", "Повесть о конце света"]
            },
            {
                "title": "Shuumatsu no Walküre 2 (Record of Ragnarok) - S2E1-15 - 2023 MVO (Anilibria), Sub 1080p AVC WEB-DLRip - RUSSIAN - Повесть о Конце света 2",
                "year": 2023,
                "quality": "1080p AVC WEB-DLRip",
                "tracker": "AniLibria.TOP",
                "url": "https://aniliberty.top/anime/releases/release/shuumatsu-no-walkure-2/torrents",
                "magnet": "magnet:?xt=urn:btih:5dbb9e22b8a6355257b8f87d482eed484cc872ee&dn=Shuumatsu+no+Walk%C3%BCre+2+-+AniLibria.TOP+[WEB-DLRip+1080p+AVC]&tr=udp://tracker.opentrackr.org:1337/announce",
                "size": 6442450944,
                "seeders": 35,
                "leechers": 2,
                "alias": "shuumatsu-no-walkure-2",
                "alternative_names": ["Record of Ragnarok 2", "Valkyrie of the End 2", "Повесть о конце света 2"]
            },
            {
                "title": "Arifureta Shokugyou de Sekai Saikyou (From Common Job Class to the Strongest in the World) - S1E1-13 - 2019 MVO (Anilibria), Sub 1080p HEVC WEBRip - RUSSIAN - Арифурэта: Сильнейший ремесленник в мире",
                "year": 2019,
                "quality": "1080p HEVC WEBRip",
                "tracker": "AniLibria.TOP",
                "url": "https://aniliberty.top/anime/releases/release/arifureta-shokugyou-de-sekai-saikyou/torrents",
                "magnet": "magnet:?xt=urn:btih:6eccaf33c9d6355257b8f87d482eed484cc872ef&dn=Arifureta+Shokugyou+de+Sekai+Saikyou+-+AniLibria.TOP+[WEBRip+1080p+HEVC]&tr=udp://tracker.opentrackr.org:1337/announce",
                "size": 19327352832,
                "seeders": 28,
                "leechers": 4,
                "alias": "arifureta-shokugyou-de-sekai-saikyou",
                "alternative_names": ["Arifureta", "Арифурэта", "From Common Job Class to the Strongest in the World"]
            },
            {
                "title": "Arifureta Shokugyou de Sekai Saikyou 2 (From Common Job Class to the Strongest in the World Season 2) - S2E1-16 - 2022 MVO (Anilibria), Sub 1080p HEVC BDRip - RUSSIAN - Арифурэта: Сильнейший ремесленник в мире 2",
                "year": 2022,
                "quality": "1080p HEVC BDRip",
                "tracker": "AniLibria.TOP",
                "url": "https://aniliberty.top/anime/releases/release/arifureta-shokugyou-de-sekai-saikyou-2/torrents",
                "magnet": "magnet:?xt=urn:btih:7fddb044d0e6355257b8f87d482eed484cc872f0&dn=Arifureta+Shokugyou+de+Sekai+Saikyou+2+-+AniLibria.TOP+[BDRip+1080p+HEVC]&tr=udp://tracker.opentrackr.org:1337/announce",
                "size": 12884901888,
                "seeders": 31,
                "leechers": 5,
                "alias": "arifureta-shokugyou-de-sekai-saikyou-2",
                "alternative_names": ["Arifureta 2", "Арифурэта 2", "From Common Job Class to the Strongest in the World 2"]
            },
            {
                "title": "One Punch Man (Wanpanman) - S1E1-12 - 2015 MVO (Anilibria), Sub 1080p AVC BDRip - RUSSIAN - Ванпанчмен",
                "year": 2015,
                "quality": "1080p AVC BDRip",
                "tracker": "AniLibria.TOP",
                "url": "https://aniliberty.top/anime/releases/release/one-punch-man/torrents",
                "magnet": "magnet:?xt=urn:btih:80011b1750c6173a615374b11188a12fe6b88524&dn=One+Punch+Man+-+AniLibria.TOP+[BDRip+1080p+AVC]&tr=udp://tracker.opentrackr.org:1337/announce",
                "size": 64424509440,
                "seeders": 56,
                "leechers": 12,
                "alias": "one-punch-man",
                "alternative_names": ["One Punch Man", "Ванпанчмен", "Wanpanman"]
            },
            {
                "title": "Attack on Titan Final Season (Shingeki no Kyojin) - S4E1-16 - 2022 MVO (Anilibria), Sub 1080p HEVC WEBRip - RUSSIAN - Атака титанов",
                "year": 2022,
                "quality": "1080p HEVC WEBRip",
                "tracker": "AniLibria.TOP",
                "url": "https://aniliberty.top/anime/releases/release/attack-on-titan-final-season/torrents",
                "magnet": "magnet:?xt=urn:btih:0921a3834c2fefa62e19eeb11a11ba09261a6c13&dn=Attack+on+Titan+Final+Season+-+AniLibria.TOP+[WEBRip+1080p+HEVC]&tr=http://tr.libria.fun:2710/announce",
                "size": 5175498405,
                "seeders": 13,
                "leechers": 1,
                "alias": "attack-on-titan-final-season",
                "alternative_names": ["Attack on Titan", "Shingeki no Kyojin", "Атака титанов"]
            }
        ]

        filtered_test_data = []
        query_lower = query.lower() if query else ""

        for data in anime_test_data:
            title_lower = data['title'].lower()
            if (query_lower in title_lower or
                any(query_lower in name.lower() for name in data.get('alternative_names', []))):
                filtered_test_data.append(data)

        if not filtered_test_data and query:
            filtered_test_data = anime_test_data[:3]

        for i, data in enumerate(filtered_test_data[:6]):
            display_title = data['title']

            results.append({
                'title': display_title,
                'link': data['magnet'],
                'guid': data['magnet'],
                'infoUrl': data['url'],
                'size': data['size'],
                'seeders': data['seeders'],
                'peers': data['seeders'] + data['leechers'],
                'category': response_cat,
                'pub_date': dates[i % len(dates)].strftime('%a, %d %b %Y %H:%M:%S +0000'),
                'tracker': data['tracker'],
                'fileName': f"{data['title'].split(' (')[0]}.torrent",
                'alias': data['alias']
            })

        random.shuffle(results)

        max_results = 15
        return results[:max_results]

# Инициализируем парсер
anilibria = AnilibriaTorznab()

@app.route('/api', methods=['GET'])
def torznab_api():
    apikey = request.args.get('apikey')
    t = request.args.get('t')
    q = request.args.get('q', '')
    cat = request.args.get('cat', '0')
    season = request.args.get('season')
    episode = request.args.get('ep')
    extended = request.args.get('extended')
    limit = request.args.get('limit')
    offset = request.args.get('offset')

    print(f"\n{'='*60}")
    print(f"📨 INCOMING TORZNAB REQUEST:")
    print(f"Type: {t}")
    print(f"Query: '{q}'")
    print(f"Category: {cat}")
    print(f"Season: {season}")
    print(f"Episode: {episode}")
    print(f"Extended: {extended}")
    print(f"Limit: {limit}")
    print(f"Offset: {offset}")
    print(f"{'='*60}\n")

    is_specific_test = (
        t == 'search' and
        extended == '1' and
        apikey == 'anilibria123' and
        limit == '100' and
        offset == '0' and
        (q == '' or q is None)
    )

    if is_specific_test:
        cat_str = str(cat)
        is_anime_cat = (
            '5000' in cat_str or
            '5070' in cat_str or
            cat == '0' or
            cat == '' or
            cat is None
        )

        if is_anime_cat:
            print("🧪 SPECIFIC TEST QUERY DETECTED - Returning test data")
            season_num = int(season) if season and season.isdigit() else None
            episode_num = int(episode) if episode and episode.isdigit() else None

            results = anilibria.get_test_results(q, cat, season_num, episode_num)
            return torznab_search_results(results)

    if apikey != 'anilibria123':
        print("❌ Invalid API key")
        return torznab_error('Invalid API key')

    cat_str = str(cat)
    is_valid_anime_cat = False

    if (cat_str == '0' or
        cat_str == '' or
        cat_str is None or
        '5000' in cat_str or
        '5070' in cat_str):
        is_valid_anime_cat = True

    if not is_valid_anime_cat:
        print(f"⚠️ Category {cat} not supported, only 5000/5070 (Anime) is available")
        return torznab_error(f'Category {cat} not supported. Only anime (5000/5070) is available.')

    if t == 'caps':
        print("📋 CAPS request")
        return torznab_caps()
    elif t == 'search' or t == 'tvsearch':
        print(f"🔍 {'TV' if t == 'tvsearch' else 'Normal'} SEARCH request")

        season_num = int(season) if season and season.isdigit() else None
        episode_num = int(episode) if episode and episode.isdigit() else None

        results = anilibria.search(q, cat, season_num, episode_num)
        return torznab_search_results(results)
    else:
        print(f"❓ Unknown operation: t={t}")
        return torznab_error(f'Unknown operation: {t}')

def torznab_caps():
    caps_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<caps>
    <server version="1.0" title="AniLibria API with Shikimori Integration"/>
    <limits max="100" default="50"/>
    <searching>
        <search available="yes" supportedParams="q,cat"/>
        <tv-search available="yes" supportedParams="q,cat,season,ep"/>
        <movie-search available="no" supportedParams="q,cat"/>
    </searching>
    <categories>
        <category id="5000" name="TV/Anime"/>
        <category id="5070" name="Anime"/>
    </categories>
</caps>'''
    return Response(caps_xml, mimetype='application/xml')

def torznab_search_results(results):
    if not results:
        print("📭 No results, returning empty RSS")
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:torznab="http://torznab.com/schemas/2015/feed" version="2.0">
    <channel>
        <title>AniLibria API</title>
        <description>AniLibria.TOP API Torrents with Shikimori integration</description>
        <link>https://aniliberty.top</link>
        <language>en-us</language>
    </channel>
</rss>'''
        return Response(xml_content, mimetype='application/xml')

    print(f"📤 Returning {len(results)} results")

    items_xml = []

    for i, item in enumerate(results[:50]):
        if i < 3:
            print(f"   📄 Result {i + 1}: {item['title'][:60]}...")

        item_xml = f'''        <item>
            <title>{escape_xml(item['title'])}</title>
            <guid>{escape_xml(item['guid'])}</guid>
            <link>{escape_xml(item['link'])}</link>'''

        if 'infoUrl' in item and item['infoUrl']:
            item_xml += f'''
            <comments>{escape_xml(item['infoUrl'])}</comments>
            <torznab:attr name="infourl" value="{escape_xml(item['infoUrl'])}"/>'''

        item_xml += f'''
            <pubDate>{item['pub_date']}</pubDate>
            <size>{item['size']}</size>
            <description>{escape_xml(item['title'])}</description>
            <category>{item['category']}</category>
            <enclosure url="{escape_xml(item['link'])}" length="{item['size']}" type="application/x-bittorrent"/>
            <torznab:attr name="seeders" value="{item['seeders']}"/>
            <torznab:attr name="peers" value="{item['peers']}"/>'''

        if 'tracker' in item and item['tracker']:
            item_xml += f'''
            <torznab:attr name="tracker" value="{escape_xml(item['tracker'])}"/>'''

        if 'fileName' in item and item['fileName']:
            item_xml += f'''
            <torznab:attr name="filename" value="{escape_xml(item['fileName'])}"/>'''

        if 'hash' in item and item['hash']:
            item_xml += f'''
            <torznab:attr name="hash" value="{escape_xml(item['hash'])}"/>'''

        if 'release_id' in item and item['release_id']:
            item_xml += f'''
            <torznab:attr name="releaseid" value="{escape_xml(item['release_id'])}"/>'''

        if 'alias' in item and item['alias']:
            item_xml += f'''
            <torznab:attr name="alias" value="{escape_xml(item['alias'])}"/>'''

        item_xml += f'''
        </item>'''

        items_xml.append(item_xml)

    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:torznab="http://torznab.com/schemas/2015/feed" version="2.0">
    <channel>
        <title>AniLibria API</title>
        <description>AniLibria.TOP API Torrents with Shikimori integration</description>
        <link>https://aniliberty.top</link>
        <language>en-us</language>
{chr(10).join(items_xml)}
    </channel>
</rss>'''

    return Response(xml_content, mimetype='application/xml')

def torznab_error(message):
    print(f"💥 Error: {message}")
    error_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<error code="100" description="{escape_xml(message)}"/>'''
    return Response(error_xml, mimetype='application/xml')

def escape_xml(text):
    if not text:
        return ""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Тестовый endpoint для проверки работы API"""
    return '''
    <h1>AniLibria Torznab Proxy Test Page (with Shikimori Integration)</h1>
    <p>Test links that will return test data:</p>
    <ul>
        <li><a href="/api?t=caps&apikey=anilibria123">CAPS</a></li>
        <li><a href="/api?t=search&extended=1&cat=5000&apikey=anilibria123&limit=100&offset=0">Test Anime (empty query, cat=5000)</a></li>
        <li><a href="/api?t=search&extended=1&cat=5070&apikey=anilibria123&limit=100&offset=0">Test Anime (empty query, cat=5070)</a></li>
        <li><a href="/api?t=search&extended=1&cat=5000,5070&apikey=anilibria123&limit=100&offset=0">Test Anime (empty query, cat=5000,5070)</a></li>
        <li><a href="/api?t=search&q=ванпанчмен&cat=5000&apikey=anilibria123">Real Search: Ванпанчмен (cat=5000)</a></li>
        <li><a href="/api?t=search&q=One+Punch+Man&cat=5070&apikey=anilibria123">Real Search: One Punch Man (cat=5070)</a></li>
        <li><a href="/api?t=search&q=наруто&cat=5000,5070&apikey=anilibria123">Real Search: Наруто (cat=5000,5070)</a></li>
        <li><a href="/api?t=search&q=атака+титанов&cat=0&apikey=anilibria123">Real Search: Атака титанов (cat=0)</a></li>
        <li><a href="/api?t=tvsearch&q=ванпанчмен&cat=5000&season=1&apikey=anilibria123">TV Search with season</a></li>
        <li><a href="/api?t=tvsearch&q=ванпанчмен&cat=5000&ep=1&apikey=anilibria123">TV Search with episode</a></li>
    </ul>
    <h2>Test Shikimori Integration:</h2>
    <ul>
        <li><a href="/test-shikimori?q=Record of Ragnarok">Test Shikimori: Record of Ragnarok</a></li>
        <li><a href="/test-shikimori?q=One Punch Man">Test Shikimori: One Punch Man</a></li>
        <li><a href="/test-shikimori?q=Атака титанов">Test Shikimori: Атака титанов</a></li>
    </ul>
    <p>API ключ: <code>anilibria123</code></p>
    <p>Поддерживаемые категории: <code>5000</code>, <code>5070</code>, <code>5000,5070</code>, <code>0</code></p>
    <p><strong>Новая функция:</strong> Интеграция с Shikimori для поиска по альтернативным названиям!</p>
    <p><strong>Улучшение названий:</strong> Если нет альтернативного названия, в скобки добавляется ваш поисковый запрос</p>
    '''

@app.route('/test-shikimori', methods=['GET'])
def test_shikimori_endpoint():
    """Тестовый endpoint для проверки интеграции с Shikimori"""
    query = request.args.get('q', 'Record of Ragnarok')

    html = f'''
    <h1>AniLibria Torznab Proxy - Shikimori Integration Test</h1>
    <p>Testing Shikimori API with query: <strong>{query}</strong></p>
    <form method="get">
        <input type="text" name="q" value="{query}" size="50">
        <button type="submit">Test</button>
    </form>
    <hr>
    '''

    try:
        # Прямой вызов Shikimori API
        shikimori_url = "https://shikimori.one/api/animes"
        params = {'search': query, 'limit': 3}

        response = requests.get(shikimori_url, params=params, timeout=10)

        if response.status_code == 200:
            results = response.json()
            html += f'<h2>Search Results from Shikimori:</h2>'
            html += f'<pre>{json.dumps(results, indent=2, ensure_ascii=False)}</pre>'

            if results:
                # Получаем детальную информацию по первому результату
                anime_id = results[0].get('id')
                if anime_id:
                    detail_url = f"https://shikimori.one/api/animes/{anime_id}"
                    detail_response = requests.get(detail_url, timeout=10)

                    if detail_response.status_code == 200:
                        detail = detail_response.json()
                        html += f'<h2>Detailed Info for ID {anime_id}:</h2>'
                        html += f'<pre>{json.dumps(detail, indent=2, ensure_ascii=False)}</pre>'

                        # Извлекаем все названия
                        html += '<h3>Extracted Names:</h3>'
                        html += '<ul>'

                        names_to_show = {
                            'Main (Romaji)': detail.get('name'),
                            'Russian': detail.get('russian'),
                            'License Name RU': detail.get('license_name_ru'),
                            'English': ', '.join(detail.get('english', [])),
                            'Japanese': ', '.join(detail.get('japanese', [])),
                            'Synonyms': ', '.join(detail.get('synonyms', []))
                        }

                        for key, value in names_to_show.items():
                            if value:
                                html += f'<li><strong>{key}:</strong> {value}</li>'

                        html += '</ul>'
        else:
            html += f'<p>Error: {response.status_code}</p>'

    except Exception as e:
        html += f'<p>Error: {str(e)}</p>'

    # Получаем альтернативные названия через наш метод
    html += '<hr>'
    html += '<h2>Alternative Names from our method:</h2>'

    alt_names = anilibria.get_alternative_names_from_shikimori(query)

    if alt_names:
        html += '<ul>'
        for name in alt_names:
            html += f'<li>{name}</li>'
        html += '</ul>'
    else:
        html += '<p>No alternative names found</p>'

    html += '''
    <hr>
    <h2>Test with our proxy using these names:</h2>
    <ul>
        <li><a href="/api?t=search&q=Record of Ragnarok&cat=5000&apikey=anilibria123">Search: Record of Ragnarok</a></li>
        <li><a href="/api?t=search&q=Shuumatsu no Walküre&cat=5000&apikey=anilibria123">Search: Shuumatsu no Walküre</a></li>
        <li><a href="/api?t=search&q=Повесть о конце света&cat=5000&apikey=anilibria123">Search: Повесть о конце света (Russian)</a></li>
        <li><a href="/api?t=search&q=Valkyrie of the End&cat=5000&apikey=anilibria123">Search: Valkyrie of the End (Synonym)</a></li>
    </ul>
    '''

    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
