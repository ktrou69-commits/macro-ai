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

class ChatWidget(QWidget):
    """Виджет чата с AI для генерации макросов"""
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.chat_history = []
        
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
        if sender == "ai" and show_actions and ("open " in text.lower() or "click " in text.lower()):
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
        
        # Имитация AI ответа (пока заглушка)
        QTimer.singleShot(2000, lambda: self.simulate_ai_response(text))
        
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
            
    # Методы для кнопок действий (заглушки)
    def open_macro(self, code: str):
        """Открытие макроса"""
        QMessageBox.information(self, "Открыть макрос", "Функция будет реализована в следующей версии")
        
    def save_macro(self, code: str):
        """Сохранение макроса"""
        QMessageBox.information(self, "Сохранить макрос", "Функция будет реализована в следующей версии")
        
    def create_variable(self, code: str):
        """Создание DSL переменной"""
        QMessageBox.information(self, "Создать переменную", "Функция будет реализована в следующей версии")
        
    def copy_code(self, code: str):
        """Копирование кода"""
        from PySide6.QtGui import QClipboard
        from PySide6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        clipboard.setText(code)
        QMessageBox.information(self, "Копирование", "Код скопирован в буфер обмена!")
