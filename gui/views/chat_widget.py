"""
Chat Widget - Виджет чата с AI
Основной интерфейс для генерации макросов через AI
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLineEdit, QPushButton, QScrollArea, QFrame,
    QLabel, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QTextCursor, QPixmap
from pathlib import Path
import datetime

# Импорт сервисов
import sys
from pathlib import Path
gui_root = Path(__file__).parent.parent
sys.path.insert(0, str(gui_root))

from services.ai_service import AIService
from services.file_service import FileService

class ChatWidget(QWidget):
    """Виджет чата с AI для генерации макросов"""
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.chat_history = []
        self.last_generated_macro = None  # Хранение последнего сгенерированного макроса
        
        # Инициализация сервисов
        self.ai_service = AIService(project_root)
        self.file_service = FileService(project_root)
        
        # Подключение сигналов AI сервиса
        self.ai_service.generation_started.connect(self.on_ai_started)
        self.ai_service.generation_finished.connect(self.on_ai_finished)
        self.ai_service.progress_updated.connect(self.on_ai_progress)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Область чата
        self.create_chat_area(layout)
        
        # Область ввода
        self.create_input_area(layout)
        
        # Добавляем приветственное сообщение
        self.add_welcome_message()
        
    def create_chat_area(self, layout: QVBoxLayout):
        """Создание области чата"""
        
        # Скроллируемая область для истории чата
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Виджет для содержимого чата
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(15)
        
        scroll_area.setWidget(self.chat_content)
        layout.addWidget(scroll_area)
        
    def create_input_area(self, layout: QVBoxLayout):
        """Создание области ввода"""
        
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(10)
        
        # Прогресс бар (скрыт по умолчанию)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 4px;
                text-align: center;
                background-color: #1E1E1E;
            }
            QProgressBar::chunk {
                background-color: #60A5FA;
                border-radius: 3px;
            }
        """)
        input_layout.addWidget(self.progress_bar)
        
        # Поле ввода и кнопка отправки
        input_row = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите запрос для AI (например: 'Создай макрос для лайков в TikTok')...")
        self.input_field.setMinimumHeight(40)
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #444444;
                border-radius: 6px;
                background-color: #1E1E1E;
                color: #E0E0E0;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #60A5FA;
            }
        """)
        
        self.send_button = QPushButton("→")
        self.send_button.setMinimumSize(40, 40)
        self.send_button.setMaximumSize(40, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #60A5FA;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4F94D4;
            }
            QPushButton:pressed {
                background-color: #3B82F6;
            }
            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
            }
        """)
        
        input_row.addWidget(self.input_field)
        input_row.addWidget(self.send_button)
        input_layout.addLayout(input_row)
        
        layout.addWidget(input_frame)
        
        # Подключение сигналов
        self.send_button.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)
        
    def add_welcome_message(self):
        """Добавление приветственного сообщения"""
        
        welcome_text = """👋 **Привет! Я AI помощник Macro AI Master.**

Я помогу вам создать макросы для автоматизации действий на macOS.

**Примеры запросов:**
• "Создай макрос для лайков в TikTok"
• "Сделай автоматизацию поиска в YouTube"
• "Создай последовательность для Instagram"

**Просто опишите что нужно сделать, и я создам готовый макрос!** ✨"""
        
        self.add_message("ai", welcome_text, show_actions=False)
        
    def add_message(self, sender: str, text: str, show_actions: bool = True):
        """Добавление сообщения в чат"""
        
        message_frame = QFrame()
        message_layout = QVBoxLayout(message_frame)
        message_layout.setSpacing(8)
        
        # Заголовок сообщения
        header_layout = QHBoxLayout()
        
        if sender == "user":
            icon = "👤"
            name = "Вы"
            align = Qt.AlignmentFlag.AlignRight
            bg_color = "#3B82F6"
        else:
            icon = "🤖"
            name = "AI"
            align = Qt.AlignmentFlag.AlignLeft
            bg_color = "#10B981"
            
        header_label = QLabel(f"{icon} {name}")
        header_label.setFont(QFont("Arial", 11, QFont.Bold))
        header_label.setStyleSheet(f"color: {bg_color}; margin-bottom: 5px;")
        
        time_label = QLabel(datetime.datetime.now().strftime("%H:%M"))
        time_label.setStyleSheet("color: #888888; font-size: 10px;")
        
        if sender == "user":
            header_layout.addWidget(time_label)
            header_layout.addStretch()
            header_layout.addWidget(header_label)
        else:
            header_layout.addWidget(header_label)
            header_layout.addStretch()
            header_layout.addWidget(time_label)
            
        message_layout.addLayout(header_layout)
        
        # Текст сообщения
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setTextFormat(Qt.TextFormat.MarkdownText)
        text_label.setStyleSheet(f"""
            QLabel {{
                padding: 12px;
                border-radius: 8px;
                background-color: {bg_color if sender == 'user' else '#2D2D2D'};
                color: {'white' if sender == 'user' else '#E0E0E0'};
                border: 1px solid {'transparent' if sender == 'user' else '#444444'};
                font-size: 13px;
                line-height: 1.4;
            }}
        """)
        
        if sender == "user":
            text_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        message_layout.addWidget(text_label)
        
        # Кнопки действий (только для AI сообщений с кодом)
        if sender == "ai" and show_actions and self._has_macro_code(text):
            self.add_action_buttons(message_layout, text)
        
        # Стилизация рамки сообщения
        message_frame.setStyleSheet("""
            QFrame {
                margin: 5px;
                border-radius: 8px;
            }
        """)
        
        self.chat_layout.addWidget(message_frame)
        
        # Прокрутка вниз
        QTimer.singleShot(100, self.scroll_to_bottom)
        
    def add_action_buttons(self, layout: QVBoxLayout, code_text: str):
        """Добавление кнопок действий под AI сообщением"""
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Кнопка "Открыть макрос"
        open_btn = QPushButton("📂 Открыть")
        open_btn.setStyleSheet(self.get_action_button_style("#10B981"))
        open_btn.clicked.connect(lambda: self.open_macro(code_text))
        
        # Кнопка "Сохранить"
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setStyleSheet(self.get_action_button_style("#3B82F6"))
        save_btn.clicked.connect(lambda: self.save_macro(code_text))
        
        # Кнопка "Создать переменную"
        var_btn = QPushButton("🔄 Переменная")
        var_btn.setStyleSheet(self.get_action_button_style("#F59E0B"))
        var_btn.clicked.connect(lambda: self.create_variable(code_text))
        
        # Кнопка "Копировать"
        copy_btn = QPushButton("📋 Копировать")
        copy_btn.setStyleSheet(self.get_action_button_style("#8B5CF6"))
        copy_btn.clicked.connect(lambda: self.copy_code(code_text))
        
        buttons_layout.addWidget(open_btn)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(var_btn)
        buttons_layout.addWidget(copy_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
    def get_action_button_style(self, color: str) -> str:
        """Получение стиля для кнопок действий"""
        return f"""
            QPushButton {{
                padding: 6px 12px;
                border: 1px solid {color};
                border-radius: 4px;
                background-color: transparent;
                color: {color};
                font-size: 11px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: white;
            }}
        """
        
    def send_message(self):
        """Отправка сообщения"""
        
        text = self.input_field.text().strip()
        if not text:
            return
            
        # Добавляем сообщение пользователя
        self.add_message("user", text)
        
        # Очищаем поле ввода
        self.input_field.clear()
        
        # Блокируем интерфейс и показываем прогресс
        self.set_loading(True)
        
        # Запускаем реальную генерацию через AI
        self.ai_service.generate_macro_async(text)
    
    def on_ai_started(self):
        """Обработка начала AI генерации"""
        self.set_loading(True)
        
    def on_ai_progress(self, status: str):
        """Обработка прогресса AI генерации"""
        # Можно показать статус в прогресс баре или статус баре
        print(f"AI Progress: {status}")
        
    def on_ai_finished(self, success: bool, result: str, metadata: dict):
        """Обработка завершения AI генерации"""
        self.set_loading(False)
        
        if success:
            # Создаем ответ AI с кодом
            ai_response = f"""✅ **Макрос сгенерирован!**

**Платформа:** {metadata.get('platform', 'Unknown')}
**Описание:** {metadata.get('description', 'Автоматически сгенерированный макрос')}

**Код макроса:**
```
{result}
```

Используйте кнопки ниже для дальнейших действий."""
            
            # Добавляем сообщение с кнопками действий
            self.add_message("ai", ai_response, show_actions=True)
            
            # Сохраняем последний результат для кнопок
            self.last_generated_macro = {
                'code': result,
                'metadata': metadata
            }
        else:
            # Показываем ошибку
            error_response = f"""❌ **Ошибка генерации макроса**

{result}

Попробуйте:
• Переформулировать запрос
• Указать конкретную платформу (TikTok, YouTube, Instagram)
• Проверить настройки API в .env файле"""
            
            self.add_message("ai", error_response, show_actions=False)
    
    def _has_macro_code(self, text: str) -> bool:
        """Проверяет, содержит ли текст код макроса"""
        text_lower = text.lower()
        
        # Проверяем наличие DSL команд
        dsl_commands = ['open ', 'click ', 'wait ', 'type ', 'press ', 'repeat ', 'scroll ']
        has_dsl_commands = any(cmd in text_lower for cmd in dsl_commands)
        
        # Проверяем наличие блока кода
        has_code_block = '```' in text
        
        # Проверяем ключевые слова макроса
        macro_keywords = ['макрос', 'код макроса', 'последовательность', 'chrome', 'tiktok', 'youtube']
        has_macro_keywords = any(keyword in text_lower for keyword in macro_keywords)
        
        return has_dsl_commands or (has_code_block and has_macro_keywords)
        
    def simulate_ai_response(self, user_text: str):
        """Имитация ответа AI (временная заглушка)"""
        
        # Простая заглушка для демонстрации
        if "tiktok" in user_text.lower():
            response = """Вот макрос для лайков в TikTok:

```
open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
click ChromeSearchField
type "tiktok.com"
press enter
wait 5s
repeat 5:
  click Chrome-TikTok-Like
  wait 1.5s
  click Chrome-TikTok-ScrollDown
  wait 2s
```

Этот макрос откроет TikTok и поставит 5 лайков подряд с прокруткой."""
        else:
            response = f"""Понял ваш запрос: "{user_text}"

Пока это демо-версия. В полной версии здесь будет:
• Генерация макроса через AI
• Анализ доступных шаблонов
• Создание оптимальной последовательности

**Скоро будет готово!** 🚀"""
        
        self.add_message("ai", response)
        self.set_loading(False)
        
    def set_loading(self, loading: bool):
        """Установка состояния загрузки"""
        
        self.send_button.setEnabled(not loading)
        self.input_field.setEnabled(not loading)
        self.progress_bar.setVisible(loading)
        
        if loading:
            self.progress_bar.setRange(0, 0)  # Бесконечный прогресс
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            
    def scroll_to_bottom(self):
        """Прокрутка чата вниз"""
        scroll_area = self.parent()
        if hasattr(scroll_area, 'verticalScrollBar'):
            scroll_bar = scroll_area.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
            
    # Методы для кнопок действий
    def open_macro(self, code: str):
        """Открытие/запуск макроса"""
        if not self.last_generated_macro:
            QMessageBox.warning(self, "Ошибка", "Нет сгенерированного макроса для запуска")
            return
        
        try:
            # Сначала сохраняем макрос во временный файл
            metadata = self.last_generated_macro.get('metadata', {})
            result = self.file_service.save_macro_to_file(
                macro_code=code,
                description=metadata.get('description', 'Временный макрос'),
                platform=metadata.get('platform', 'Unknown')
            )
            
            if result['success']:
                # Запускаем макрос
                run_result = self.file_service.run_macro(result['file_path'])
                
                if run_result['success']:
                    QMessageBox.information(
                        self, 
                        "Макрос запущен", 
                        f"Макрос успешно запущен!\n\nФайл: {result['filename']}\nВывод: {run_result.get('output', 'Нет вывода')}"
                    )
                else:
                    QMessageBox.critical(
                        self, 
                        "Ошибка запуска", 
                        f"Не удалось запустить макрос:\n{run_result.get('error', 'Неизвестная ошибка')}"
                    )
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить макрос:\n{result.get('error', 'Неизвестная ошибка')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка запуска макроса:\n{str(e)}")
        
    def save_macro(self, code: str):
        """Сохранение макроса в файл"""
        if not self.last_generated_macro:
            QMessageBox.warning(self, "Ошибка", "Нет сгенерированного макроса для сохранения")
            return
        
        try:
            metadata = self.last_generated_macro.get('metadata', {})
            
            # Диалог для ввода имени файла
            from PySide6.QtWidgets import QInputDialog
            
            suggested_name = f"{metadata.get('platform', 'macro').lower()}_macro"
            filename, ok = QInputDialog.getText(
                self, 
                "Сохранить макрос", 
                "Введите имя файла (без расширения):",
                text=suggested_name
            )
            
            if ok and filename:
                result = self.file_service.save_macro_to_file(
                    macro_code=code,
                    filename=filename,
                    description=metadata.get('description', 'Сгенерированный макрос'),
                    platform=metadata.get('platform', 'Unknown')
                )
                
                if result['success']:
                    QMessageBox.information(
                        self, 
                        "Макрос сохранен", 
                        f"Макрос успешно сохранен!\n\nФайл: {result['filename']}\nПуть: {result['file_path']}"
                    )
                else:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить макрос:\n{result.get('error', 'Неизвестная ошибка')}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения:\n{str(e)}")
        
    def create_variable(self, code: str):
        """Создание DSL переменной из макроса"""
        if not self.last_generated_macro:
            QMessageBox.warning(self, "Ошибка", "Нет сгенерированного макроса для создания переменной")
            return
        
        try:
            from PySide6.QtWidgets import QInputDialog
            
            metadata = self.last_generated_macro.get('metadata', {})
            
            # Диалог для ввода имени переменной
            suggested_name = f"{metadata.get('platform', 'Custom')}Action"
            var_name, ok = QInputDialog.getText(
                self, 
                "Создать DSL переменную", 
                "Введите имя переменной:",
                text=suggested_name
            )
            
            if ok and var_name:
                result = self.file_service.create_dsl_variable(
                    name=var_name,
                    code=code,
                    description=metadata.get('description', 'Автоматически созданная переменная')
                )
                
                if result['success']:
                    QMessageBox.information(
                        self, 
                        "Переменная создана", 
                        f"DSL переменная успешно создана!\n\nИмя: ${{{var_name}}}\nДобавлена в DSL_VARIABLES.txt"
                    )
                else:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось создать переменную:\n{result.get('error', 'Неизвестная ошибка')}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания переменной:\n{str(e)}")
        
    def copy_code(self, code: str):
        """Копирование кода в буфер обмена"""
        try:
            success = self.file_service.copy_to_clipboard(code)
            
            if success:
                QMessageBox.information(self, "Копирование", "Код скопирован в буфер обмена!")
            else:
                # Fallback для других систем
                from PySide6.QtGui import QClipboard
                from PySide6.QtWidgets import QApplication
                
                clipboard = QApplication.clipboard()
                clipboard.setText(code)
                QMessageBox.information(self, "Копирование", "Код скопирован в буфер обмена!")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка копирования:\n{str(e)}")
