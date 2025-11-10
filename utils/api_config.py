"""
api_config.py
Централизованная конфигурация API ключей

Все API ключи загружаются из .env файла.
Изменяйте ключи только в .env - они автоматически подхватятся везде!
"""

import os
from pathlib import Path
from typing import Optional


def load_env():
    """
    Загружает переменные из .env файла
    
    Ищет .env в корне проекта и загружает все переменные
    """
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if not env_file.exists():
        return
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Пропускаем комментарии и пустые строки
            if not line or line.startswith('#'):
                continue
            
            # Парсим KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Устанавливаем переменную окружения если её ещё нет
                if key and not os.getenv(key):
                    os.environ[key] = value


# Автоматически загружаем .env при импорте
load_env()


class APIConfig:
    """
    Централизованная конфигурация API ключей
    
    Использование:
        from utils.api_config import APIConfig
        
        config = APIConfig()
        if config.has_gemini():
            client = genai.Client(api_key=config.gemini_key)
    """
    
    def __init__(self):
        """Инициализация - загружает все API ключи из переменных окружения"""
        # Gemini API
        self.gemini_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # OpenAI API
        self.openai_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        
        # Anthropic API
        self.anthropic_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        
        # Настройки AI
        self.ai_model: str = os.getenv("AI_MODEL", "gemini-pro")
        self.ai_temperature: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.ai_max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "100"))
    
    def has_gemini(self) -> bool:
        """Проверяет доступность Gemini API"""
        return bool(self.gemini_key)
    
    def has_openai(self) -> bool:
        """Проверяет доступность OpenAI API"""
        return bool(self.openai_key)
    
    def has_anthropic(self) -> bool:
        """Проверяет доступность Anthropic API"""
        return bool(self.anthropic_key)
    
    def get_gemini_key(self) -> str:
        """
        Возвращает Gemini API ключ
        
        Raises:
            ValueError: Если ключ не установлен
        """
        if not self.gemini_key:
            raise ValueError(
                "GEMINI_API_KEY не найден!\n"
                "Добавьте ключ в .env файл:\n"
                "GEMINI_API_KEY=your-key-here\n"
                "Или установите переменную окружения:\n"
                "export GEMINI_API_KEY='your-key'"
            )
        return self.gemini_key
    
    def get_openai_key(self) -> str:
        """
        Возвращает OpenAI API ключ
        
        Raises:
            ValueError: Если ключ не установлен
        """
        if not self.openai_key:
            raise ValueError(
                "OPENAI_API_KEY не найден!\n"
                "Добавьте ключ в .env файл или установите переменную окружения"
            )
        return self.openai_key
    
    def get_anthropic_key(self) -> str:
        """
        Возвращает Anthropic API ключ
        
        Raises:
            ValueError: Если ключ не установлен
        """
        if not self.anthropic_key:
            raise ValueError(
                "ANTHROPIC_API_KEY не найден!\n"
                "Добавьте ключ в .env файл или установите переменную окружения"
            )
        return self.anthropic_key
    
    def print_status(self):
        """Выводит статус доступности API ключей"""
        print("\n📊 Статус API ключей:")
        print(f"   Gemini:    {'✅ Установлен' if self.has_gemini() else '❌ Не установлен'}")
        print(f"   OpenAI:    {'✅ Установлен' if self.has_openai() else '❌ Не установлен'}")
        print(f"   Anthropic: {'✅ Установлен' if self.has_anthropic() else '❌ Не установлен'}")
        print()


# Глобальный экземпляр для удобства
api_config = APIConfig()


# Для обратной совместимости - функции-хелперы
def get_gemini_key() -> Optional[str]:
    """Возвращает Gemini API ключ или None"""
    return api_config.gemini_key


def get_openai_key() -> Optional[str]:
    """Возвращает OpenAI API ключ или None"""
    return api_config.openai_key


def get_anthropic_key() -> Optional[str]:
    """Возвращает Anthropic API ключ или None"""
    return api_config.anthropic_key


if __name__ == "__main__":
    # Тест конфигурации
    print("="*80)
    print("API Configuration Test".center(80))
    print("="*80)
    
    config = APIConfig()
    config.print_status()
    
    print("📁 Путь к .env:", Path(__file__).parent.parent / ".env")
    print()
    
    if config.has_gemini():
        print(f"✅ Gemini ключ: {config.gemini_key[:20]}...")
    else:
        print("❌ Gemini ключ не найден")
        print("💡 Добавьте в .env:")
        print("   GEMINI_API_KEY=your-key-here")
    
    print()
    print("="*80)
