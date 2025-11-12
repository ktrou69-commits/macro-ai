#!/usr/bin/env python3
"""
Быстрый Главный AI - мгновенный анализ и роутинг без загрузки тяжелых модулей
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ai.smart_router import SmartAIRouter

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FastMainAI:
    """
    Быстрый Главный AI - мгновенный анализ и выполнение
    Загружает только нужный модуль, а не все сразу
    """
    
    def __init__(self):
        """Инициализация быстрого AI"""
        self.router = SmartAIRouter()
        self.loaded_modules = {}  # Кэш загруженных модулей
        logger.info("⚡ FastMainAI инициализирован")
    
    def process_request(self, user_request: str) -> Dict[str, Any]:
        """
        Обработка запроса пользователя
        
        Args:
            user_request: Запрос пользователя
            
        Returns:
            Результат выполнения
        """
        try:
            start_time = time.time()
            
            print(f"🎯 Анализирую запрос: '{user_request}'")
            
            # 1. Быстрый роутинг (мгновенно)
            routing_result = self.router.route_request(user_request)
            module_name = routing_result["module"]
            confidence = routing_result["confidence"]
            
            routing_time = time.time() - start_time
            print(f"✅ Выбран модуль: {module_name} (уверенность: {confidence:.2f}) за {routing_time:.2f}с")
            
            # 2. Загрузка только нужного модуля
            module_start = time.time()
            module = self._load_module(module_name)
            module_load_time = time.time() - module_start
            
            print(f"⚡ Модуль загружен за {module_load_time:.2f}с")
            
            # 3. Выполнение через специализированный AI модуля
            execution_start = time.time()
            result = self._execute_with_module(module, user_request, routing_result)
            execution_time = time.time() - execution_start
            
            total_time = time.time() - start_time
            
            print(f"🎉 Выполнено за {execution_time:.2f}с (общее время: {total_time:.2f}с)")
            
            return {
                "success": True,
                "result": result,
                "module": module_name,
                "confidence": confidence,
                "timing": {
                    "routing": routing_time,
                    "module_load": module_load_time,
                    "execution": execution_time,
                    "total": total_time
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки запроса: {e}")
            return {
                "success": False,
                "error": str(e),
                "module": "unknown"
            }
    
    def _load_module(self, module_name: str):
        """
        Ленивая загрузка модуля (только когда нужен)
        """
        if module_name in self.loaded_modules:
            logger.info(f"📦 Модуль {module_name} уже загружен (из кэша)")
            return self.loaded_modules[module_name]
        
        try:
            if module_name == "sequence_generator":
                from src.modules.sequence_generator.module import SequenceGeneratorModule
                module = SequenceGeneratorModule()
                
            elif module_name == "dom_analyzer":
                # Заглушка для dom_analyzer
                class DOMAnalyzerModule:
                    def analyze_request(self, request, context):
                        return {"message": "DOM анализ пока не реализован", "success": False}
                module = DOMAnalyzerModule()
                
            elif module_name == "prompt_updater":
                # Заглушка для prompt_updater
                class PromptUpdaterModule:
                    def update_prompts(self, request, context):
                        return {"message": "Обновление промптов пока не реализовано", "success": False}
                module = PromptUpdaterModule()
                
            else:
                raise ValueError(f"Неизвестный модуль: {module_name}")
            
            # Кэшируем модуль
            self.loaded_modules[module_name] = module
            logger.info(f"✅ Модуль {module_name} загружен и закэширован")
            
            return module
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модуля {module_name}: {e}")
            raise
    
    def _execute_with_module(self, module, user_request: str, routing_result: Dict[str, Any]):
        """
        Выполнение запроса через специализированный модуль
        """
        module_name = routing_result["module"]
        
        try:
            if module_name == "sequence_generator":
                # Используем специализированный AI модуля для генерации
                result = module.generate_and_save(user_request)
                return result
                
            elif module_name == "dom_analyzer":
                return module.analyze_request(user_request, routing_result["context"])
                
            elif module_name == "prompt_updater":
                return module.update_prompts(user_request, routing_result["context"])
                
            else:
                return {"error": f"Неизвестный модуль: {module_name}", "success": False}
                
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения в модуле {module_name}: {e}")
            return {"error": str(e), "success": False}

def main():
    """Главная функция для тестирования"""
    print("🚀 БЫСТРЫЙ ГЛАВНЫЙ AI - ТЕСТИРОВАНИЕ")
    print("=" * 60)
    
    ai = FastMainAI()
    
    test_requests = [
        "открой калькулятор",
        "найди на YouTube видео про Python",
        "найди ноутбуки на Amazon"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n🧪 ТЕСТ {i}: '{request}'")
        print("-" * 40)
        
        result = ai.process_request(request)
        
        if result["success"]:
            print(f"✅ Успех!")
            if "filepath" in result.get("result", {}):
                print(f"📁 Файл: {Path(result['result']['filepath']).name}")
        else:
            print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        
        print(f"⏱️  Время: {result.get('timing', {}).get('total', 0):.2f}с")

if __name__ == "__main__":
    main()
