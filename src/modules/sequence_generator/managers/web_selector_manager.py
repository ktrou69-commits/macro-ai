"""
Менеджер веб-селекторов для расширенной веб-автоматизации
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class WebSelectorManager:
    """Менеджер веб-селекторов для автоматизации популярных сайтов"""
    
    def __init__(self):
        self.web_selectors = {}
        self.web_patterns = {}
        self.web_commands = {}
        self.site_keywords = {}
        self._load_web_selectors()
    
    def _load_web_selectors(self):
        """Загрузка конфигурации веб-селекторов"""
        try:
            config_path = Path(__file__).parent.parent / "resources" / "advanced_web_selectors.yaml"
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                self.web_selectors = config.get('advanced_web_selectors', {})
                self.web_patterns = config.get('web_patterns', {})
                self.web_commands = config.get('web_commands', {})
                
                # Создаем индекс ключевых слов для быстрого поиска
                self._build_keywords_index()
                
                logger.info(f"✅ Загружено {len(self.web_selectors)} веб-сайтов с селекторами")
            else:
                logger.warning("⚠️ Конфигурация advanced_web_selectors.yaml не найдена")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки advanced_web_selectors.yaml: {e}")
    
    def _build_keywords_index(self):
        """Построение индекса ключевых слов для сайтов"""
        self.site_keywords = {}
        
        for site_name, site_info in self.web_selectors.items():
            keywords = site_info.get('keywords', [])
            domain = site_info.get('domain', '')
            
            # Добавляем домен как ключевое слово
            if domain:
                keywords.append(domain)
                keywords.append(domain.replace('.com', '').replace('.org', '').replace('.net', ''))
            
            # Индексируем все ключевые слова
            for keyword in keywords:
                if keyword.lower() not in self.site_keywords:
                    self.site_keywords[keyword.lower()] = []
                self.site_keywords[keyword.lower()].append(site_name)
    
    def identify_site_from_url(self, url: str) -> Optional[str]:
        """Определение сайта по URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Убираем www. и поддомены
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Поиск по точному совпадению домена
            for site_name, site_info in self.web_selectors.items():
                site_domain = site_info.get('domain', '').lower()
                if domain == site_domain or domain.endswith('.' + site_domain):
                    return site_name
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось определить сайт из URL {url}: {e}")
            return None
    
    def identify_site_from_keywords(self, text: str) -> List[str]:
        """Определение сайтов по ключевым словам в тексте"""
        text_lower = text.lower()
        matching_sites = []
        
        for keyword, sites in self.site_keywords.items():
            if keyword in text_lower:
                matching_sites.extend(sites)
        
        # Убираем дубликаты и сортируем по релевантности
        unique_sites = list(set(matching_sites))
        return unique_sites
    
    def get_site_selectors(self, site_name: str) -> Dict[str, str]:
        """Получение селекторов для сайта"""
        site_info = self.web_selectors.get(site_name, {})
        return site_info.get('selectors', {})
    
    def get_selector(self, site_name: str, element_name: str) -> Optional[str]:
        """Получение конкретного селектора"""
        selectors = self.get_site_selectors(site_name)
        return selectors.get(element_name)
    
    def find_selector_by_description(self, site_name: str, description: str) -> Optional[Tuple[str, str]]:
        """Поиск селектора по описанию"""
        selectors = self.get_site_selectors(site_name)
        description_lower = description.lower()
        
        # Поиск по имени селектора
        for selector_name, selector_xpath in selectors.items():
            if description_lower in selector_name.lower():
                return selector_name, selector_xpath
        
        # Поиск по ключевым словам в названии
        keywords_map = {
            'поиск': ['search', 'find'],
            'кнопка': ['button', 'btn'],
            'ссылка': ['link', 'href'],
            'поле': ['field', 'input', 'box'],
            'меню': ['menu', 'nav'],
            'логин': ['login', 'signin'],
            'регистрация': ['signup', 'register'],
            'лайк': ['like', 'heart'],
            'подписка': ['subscribe', 'follow'],
            'комментарий': ['comment', 'reply']
        }
        
        for rus_word, eng_words in keywords_map.items():
            if rus_word in description_lower:
                for eng_word in eng_words:
                    for selector_name, selector_xpath in selectors.items():
                        if eng_word in selector_name.lower():
                            return selector_name, selector_xpath
        
        return None
    
    def generate_web_navigation_dsl(self, site_name: str, url: str = None) -> str:
        """Генерация DSL для перехода на сайт"""
        site_info = self.web_selectors.get(site_name, {})
        
        if not site_info:
            return f"# Сайт {site_name} не найден в базе селекторов"
        
        domain = site_info.get('domain', '')
        description = site_info.get('description', f'Сайт {site_name}')
        
        target_url = url if url else f"https://{domain}"
        
        return f"""# Переход на {description}
navigate "{target_url}"
wait 3s"""
    
    def generate_search_dsl(self, site_name: str, query: str) -> str:
        """Генерация DSL для поиска на сайте"""
        site_info = self.web_selectors.get(site_name, {})
        
        if not site_info:
            return f"# Сайт {site_name} не найден"
        
        selectors = site_info.get('selectors', {})
        search_box = selectors.get('search_box') or selectors.get('search_input') or selectors.get('search_field')
        search_button = selectors.get('search_button')
        
        if not search_box:
            return f"# Поисковое поле не найдено для {site_name}"
        
        dsl = f"""# Поиск на {site_name}: {query}
click_element "{search_box}"
wait 1s
type "{query}"
wait 1s"""
        
        if search_button:
            dsl += f'\nclick_element "{search_button}"'
        else:
            dsl += '\npress enter'
        
        dsl += '\nwait 3s'
        
        return dsl
    
    def generate_youtube_automation_dsl(self, action: str, query: str = None) -> str:
        """Специализированная генерация для YouTube"""
        youtube_selectors = self.get_site_selectors('youtube')
        
        if action == "search_and_play":
            return f"""# Поиск и воспроизведение видео на YouTube: {query}
navigate "https://youtube.com"
wait 3s
click_element "{youtube_selectors.get('search_box', '//input[@id=\"search\"]')}"
wait 1s
type "{query}"
press enter
wait 3s
click_element "{youtube_selectors.get('first_video', '//div[@id=\"contents\"]//a[@id=\"video-title\"][1]')}"
wait 5s"""
        
        elif action == "like_video":
            return f"""# Лайк текущего видео на YouTube
click_element "{youtube_selectors.get('like_button', '//button[contains(@aria-label, \"like\")]')}"
wait 1s"""
        
        elif action == "subscribe":
            return f"""# Подписка на канал YouTube
click_element "{youtube_selectors.get('subscribe_button', '//button[contains(text(), \"Subscribe\")]')}"
wait 2s"""
        
        else:
            return f"# Неизвестное действие для YouTube: {action}"
    
    def generate_google_search_dsl(self, query: str, search_type: str = "web") -> str:
        """Специализированная генерация для Google поиска"""
        google_selectors = self.get_site_selectors('google')
        
        dsl = f"""# Поиск в Google: {query}
navigate "https://google.com"
wait 2s
click_element "{google_selectors.get('search_box', '//input[@name=\"q\"]')}"
wait 1s
type "{query}"
press enter
wait 3s"""
        
        # Переключение на нужный тип поиска
        if search_type == "images":
            dsl += f'\nclick_element "{google_selectors.get("images_tab", "//a[contains(@href, \"tbm=isch\")]")}"'
            dsl += '\nwait 2s'
        elif search_type == "videos":
            dsl += f'\nclick_element "{google_selectors.get("videos_tab", "//a[contains(@href, \"tbm=vid\")]")}"'
            dsl += '\nwait 2s'
        elif search_type == "news":
            dsl += f'\nclick_element "{google_selectors.get("news_tab", "//a[contains(@href, \"tbm=nws\")]")}"'
            dsl += '\nwait 2s'
        
        return dsl
    
    def generate_social_media_post_dsl(self, site_name: str, content: str) -> str:
        """Генерация DSL для публикации в социальных сетях"""
        site_info = self.web_selectors.get(site_name, {})
        
        if not site_info:
            return f"# Сайт {site_name} не поддерживается"
        
        selectors = site_info.get('selectors', {})
        
        if site_name == "twitter":
            return f"""# Публикация твита: {content}
click_element "{selectors.get('tweet_button', '//a[@data-testid=\"SideNav_NewTweet_Button\"]')}"
wait 2s
click_element "{selectors.get('tweet_compose', '//div[@data-testid=\"tweetTextarea_0\"]')}"
wait 1s
type "{content}"
wait 1s
click_element "{selectors.get('tweet_send', '//div[@data-testid=\"tweetButton\"]')}"
wait 3s"""
        
        elif site_name == "linkedin":
            return f"""# Публикация поста в LinkedIn: {content}
click_element "{selectors.get('post_button', '//button[contains(text(), \"Start a post\")]')}"
wait 2s
click_element "{selectors.get('post_text', '//div[@data-placeholder=\"What do you want to talk about?\"]')}"
wait 1s
type "{content}"
wait 1s
click_element "{selectors.get('post_submit', '//button[contains(text(), \"Post\")]')}"
wait 3s"""
        
        else:
            return f"# Публикация постов на {site_name} пока не поддерживается"
    
    def get_common_patterns(self, pattern_type: str) -> Dict[str, str]:
        """Получение общих паттернов веб-элементов"""
        return self.web_patterns.get(pattern_type, {})
    
    def suggest_selectors(self, site_name: str, partial_name: str) -> List[str]:
        """Предложение селекторов по частичному имени"""
        selectors = self.get_site_selectors(site_name)
        suggestions = []
        
        partial_lower = partial_name.lower()
        
        for selector_name in selectors.keys():
            if partial_lower in selector_name.lower():
                suggestions.append(selector_name)
        
        return suggestions[:10]  # Ограничиваем количество предложений
    
    def validate_selector(self, selector: str) -> bool:
        """Базовая валидация XPath селектора"""
        try:
            # Проверяем базовый синтаксис XPath
            if not selector.startswith('//'):
                return False
            
            # Проверяем наличие запрещенных символов
            forbidden_chars = ['<', '>', '&', '"', "'"]
            if any(char in selector for char in forbidden_chars if char not in ["'", '"']):
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_site_statistics(self) -> Dict[str, Any]:
        """Получение статистики веб-селекторов"""
        total_selectors = sum(len(site.get('selectors', {})) for site in self.web_selectors.values())
        
        return {
            "total_sites": len(self.web_selectors),
            "total_selectors": total_selectors,
            "total_keywords": len(self.site_keywords),
            "sites_list": list(self.web_selectors.keys()),
            "patterns_count": len(self.web_patterns),
            "commands_count": len(self.web_commands)
        }
    
    def export_selectors_for_site(self, site_name: str) -> Dict[str, Any]:
        """Экспорт всех селекторов для сайта"""
        return self.web_selectors.get(site_name, {})
    
    def add_custom_selector(self, site_name: str, selector_name: str, selector_xpath: str):
        """Добавление пользовательского селектора"""
        if site_name not in self.web_selectors:
            self.web_selectors[site_name] = {
                'domain': 'custom',
                'description': f'Пользовательский сайт {site_name}',
                'selectors': {},
                'keywords': [site_name.lower()]
            }
        
        self.web_selectors[site_name]['selectors'][selector_name] = selector_xpath
        logger.info(f"➕ Добавлен селектор {selector_name} для {site_name}")
    
    def get_supported_sites(self) -> List[Dict[str, str]]:
        """Получение списка поддерживаемых сайтов"""
        sites = []
        
        for site_name, site_info in self.web_selectors.items():
            sites.append({
                'name': site_name,
                'domain': site_info.get('domain', ''),
                'description': site_info.get('description', ''),
                'selectors_count': len(site_info.get('selectors', {}))
            })
        
        return sites
