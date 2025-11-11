# 🖥️ Этап 4: GUI интеграция (1 неделя)

**Время выполнения:** 1 неделя  
**Приоритет:** Средний  
**Зависимости:** Этапы 1, 2, 3 завершены

## 🎯 Цели этапа

1. Создать виджет голосового ассистента для GUI
2. Интегрировать с существующим PySide6 интерфейсом
3. Добавить визуализацию состояния прослушивания
4. Реализовать логи диалогов и настройки

## 📋 Компоненты GUI

### Основные элементы интерфейса
- **Статус ассистента** - индикатор прослушивания
- **Лог диалогов** - история команд и ответов
- **Настройки голоса** - выбор движка TTS/ASR
- **Управление сессиями** - список активных макросов

## 🛠️ Детальная реализация

### Шаг 4.1: Создать voice_assistant_widget.py

**Файл:** `gui/views/voice_assistant_widget.py`

```python
#!/usr/bin/env python3
"""
voice_assistant_widget.py
GUI виджет для голосового ассистента
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTextEdit, QComboBox, QGroupBox, QListWidget,
    QListWidgetItem, QProgressBar, QCheckBox, QSpinBox,
    QSplitter, QFrame
)
from PySide6.QtCore import QTimer, Signal, QThread, pyqtSignal
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.voice.speech_recognition import VoiceRecognizer, HotwordDetector
    from src.voice.text_to_speech import TextToSpeech, VoiceAssistantResponses
    from src.memory.state_manager import state_manager
    VOICE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Голосовые модули недоступны: {e}")
    VOICE_MODULES_AVAILABLE = False


class VoiceAssistantThread(QThread):
    """Поток для голосового ассистента"""
    
    voice_command_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.voice_recognizer = None
        self.is_running = False
        
    def initialize_voice(self, engine: str = "whisper"):
        """Инициализация голосового движка"""
        try:
            if VOICE_MODULES_AVAILABLE:
                self.voice_recognizer = VoiceRecognizer(engine=engine)
                self.hotword_detector = HotwordDetector()
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Ошибка инициализации: {e}")
            return False
    
    def start_listening(self):
        """Начать прослушивание"""
        if not self.voice_recognizer:
            return
            
        self.is_running = True
        self.voice_recognizer.start_listening(self._on_voice_command)
        self.status_changed.emit("listening")
    
    def stop_listening(self):
        """Остановить прослушивание"""
        self.is_running = False
        if self.voice_recognizer:
            self.voice_recognizer.stop_listening()
        self.status_changed.emit("stopped")
    
    def _on_voice_command(self, text: str):
        """Обработка голосовой команды"""
        self.voice_command_received.emit(text)


class DialogLogWidget(QTextEdit):
    """Виджет для отображения логов диалогов"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(200)
        
        # Настройка стиля
        font = QFont("Monaco", 10)
        self.setFont(font)
        
    def add_user_message(self, message: str):
        """Добавить сообщение пользователя"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append(f"<span style='color: #4CAF50;'>[{timestamp}] 👤 Пользователь:</span> {message}")
        
    def add_assistant_message(self, message: str):
        """Добавить сообщение ассистента"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append(f"<span style='color: #2196F3;'>[{timestamp}] 🤖 Ассистент:</span> {message}")
        
    def add_system_message(self, message: str):
        """Добавить системное сообщение"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append(f"<span style='color: #FF9800;'>[{timestamp}] ⚙️ Система:</span> {message}")
        
    def add_error_message(self, message: str):
        """Добавить сообщение об ошибке"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append(f"<span style='color: #F44336;'>[{timestamp}] ❌ Ошибка:</span> {message}")


class VoiceStatusWidget(QWidget):
    """Виджет статуса голосового ассистента"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Таймер для анимации
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_frame = 0
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Индикатор статуса
        self.status_label = QLabel("🔇 Не активен")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
                background-color: #424242;
                color: white;
            }
        """)
        
        # Прогресс-бар для визуализации
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch()
        
    def set_status(self, status: str):
        """Установить статус"""
        if status == "listening":
            self.status_label.setText("🎤 Слушаю...")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                    background-color: #4CAF50;
                    color: white;
                }
            """)
            self.progress_bar.setVisible(True)
            self.animation_timer.start(100)
            
        elif status == "processing":
            self.status_label.setText("🧠 Обрабатываю...")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                    background-color: #FF9800;
                    color: white;
                }
            """)
            
        elif status == "speaking":
            self.status_label.setText("🗣️ Говорю...")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                    background-color: #2196F3;
                    color: white;
                }
            """)
            
        else:  # stopped
            self.status_label.setText("🔇 Не активен")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 4px;
                    background-color: #424242;
                    color: white;
                }
            """)
            self.progress_bar.setVisible(False)
            self.animation_timer.stop()
    
    def update_animation(self):
        """Обновление анимации прослушивания"""
        self.animation_frame = (self.animation_frame + 10) % 100
        self.progress_bar.setValue(self.animation_frame)


class SessionsWidget(QListWidget):
    """Виджет для отображения активных сессий"""
    
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(150)
        
        # Обновляем список каждые 2 секунды
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_sessions)
        self.update_timer.start(2000)
        
    def update_sessions(self):
        """Обновить список сессий"""
        try:
            if not VOICE_MODULES_AVAILABLE:
                return
                
            # Получаем возобновляемые сессии
            resumable = state_manager.get_resumable_sessions()
            
            # Очищаем список
            self.clear()
            
            # Добавляем сессии
            for session in resumable:
                item_text = f"📄 {session.atlas_file} - Шаг {session.current_step}/{session.total_steps}"
                if session.voice_command:
                    item_text += f"\n🎤 '{session.voice_command}'"
                
                item = QListWidgetItem(item_text)
                item.setData(1, session.session_id)  # Сохраняем ID сессии
                self.addItem(item)
                
        except Exception as e:
            print(f"⚠️ Ошибка обновления сессий: {e}")


class VoiceSettingsWidget(QGroupBox):
    """Виджет настроек голосового ассистента"""
    
    def __init__(self):
        super().__init__("Настройки голоса")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Движок распознавания речи
        asr_layout = QHBoxLayout()
        asr_layout.addWidget(QLabel("Распознавание:"))
        self.asr_combo = QComboBox()
        self.asr_combo.addItems(["whisper", "speech_recognition"])
        asr_layout.addWidget(self.asr_combo)
        layout.addLayout(asr_layout)
        
        # Движок синтеза речи
        tts_layout = QHBoxLayout()
        tts_layout.addWidget(QLabel("Синтез речи:"))
        self.tts_combo = QComboBox()
        self.tts_combo.addItems(["macos_say", "pyttsx3"])
        tts_layout.addWidget(self.tts_combo)
        layout.addLayout(tts_layout)
        
        # Голос
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Голос:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["Milena", "Yuri", "Katya"])
        voice_layout.addWidget(self.voice_combo)
        layout.addLayout(voice_layout)
        
        # Автоактивация
        self.auto_activation_cb = QCheckBox("Автоматическая активация по ключевым словам")
        self.auto_activation_cb.setChecked(True)
        layout.addWidget(self.auto_activation_cb)
        
        # Чувствительность
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Чувствительность:"))
        self.sensitivity_spin = QSpinBox()
        self.sensitivity_spin.setRange(1, 10)
        self.sensitivity_spin.setValue(5)
        sensitivity_layout.addWidget(self.sensitivity_spin)
        layout.addLayout(sensitivity_layout)


class VoiceAssistantWidget(QWidget):
    """Главный виджет голосового ассистента"""
    
    # Сигналы
    command_received = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_voice_assistant()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("🎤 Голосовой ассистент")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
            }
        """)
        layout.addWidget(title)
        
        # Статус
        self.status_widget = VoiceStatusWidget()
        layout.addWidget(self.status_widget)
        
        # Кнопки управления
        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Начать прослушивание")
        self.start_btn.clicked.connect(self.start_listening)
        self.start_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 8px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.stop_btn = QPushButton("⏹️ Остановить")
        self.stop_btn.clicked.connect(self.stop_listening)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 8px;
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Сплиттер для основного содержимого
        splitter = QSplitter()
        
        # Левая панель - логи и сессии
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Лог диалогов
        left_layout.addWidget(QLabel("💬 Лог диалогов:"))
        self.dialog_log = DialogLogWidget()
        left_layout.addWidget(self.dialog_log)
        
        # Активные сессии
        left_layout.addWidget(QLabel("📋 Активные сессии:"))
        self.sessions_widget = SessionsWidget()
        left_layout.addWidget(self.sessions_widget)
        
        # Правая панель - настройки
        self.settings_widget = VoiceSettingsWidget()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(self.settings_widget)
        splitter.setSizes([400, 300])
        
        layout.addWidget(splitter)
        
    def setup_voice_assistant(self):
        """Настройка голосового ассистента"""
        if not VOICE_MODULES_AVAILABLE:
            self.dialog_log.add_error_message("Голосовые модули недоступны")
            self.start_btn.setEnabled(False)
            return
            
        # Создаем поток для голосового ассистента
        self.voice_thread = VoiceAssistantThread()
        self.voice_thread.voice_command_received.connect(self.on_voice_command)
        self.voice_thread.status_changed.connect(self.status_widget.set_status)
        self.voice_thread.error_occurred.connect(self.on_voice_error)
        
        # Инициализируем TTS
        try:
            self.tts = TextToSpeech(engine="macos_say")
            self.voice_responses = VoiceAssistantResponses(self.tts)
            self.dialog_log.add_system_message("Голосовой ассистент инициализирован")
        except Exception as e:
            self.dialog_log.add_error_message(f"Ошибка инициализации TTS: {e}")
    
    def start_listening(self):
        """Начать прослушивание"""
        if not VOICE_MODULES_AVAILABLE:
            return
            
        # Инициализируем распознавание речи
        engine = self.settings_widget.asr_combo.currentText()
        if self.voice_thread.initialize_voice(engine):
            self.voice_thread.start_listening()
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            self.dialog_log.add_system_message("Прослушивание начато")
            self.tts.speak("Голосовой ассистент активирован")
        else:
            self.dialog_log.add_error_message("Не удалось инициализировать голосовое распознавание")
    
    def stop_listening(self):
        """Остановить прослушивание"""
        self.voice_thread.stop_listening()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        self.dialog_log.add_system_message("Прослушивание остановлено")
        self.tts.speak("Голосовой ассистент деактивирован")
    
    def on_voice_command(self, command: str):
        """Обработка голосовой команды"""
        self.dialog_log.add_user_message(command)
        
        # Проверяем ключевые слова
        if hasattr(self.voice_thread, 'hotword_detector'):
            if self.voice_thread.hotword_detector.detect_hotword(command):
                actual_command = self.voice_thread.hotword_detector.extract_command(command)
                self.voice_responses.acknowledge_command(actual_command)
                self.dialog_log.add_assistant_message(f"Выполняю: {actual_command}")
                
                # Эмитируем сигнал для основного приложения
                self.command_received.emit(actual_command)
            else:
                # Команда без ключевого слова - игнорируем или обрабатываем по настройкам
                if not self.settings_widget.auto_activation_cb.isChecked():
                    self.dialog_log.add_system_message("Команда проигнорирована (нет ключевого слова)")
                else:
                    self.voice_responses.acknowledge_command(command)
                    self.command_received.emit(command)
    
    def on_voice_error(self, error: str):
        """Обработка ошибки голосового ассистента"""
        self.dialog_log.add_error_message(error)
        self.voice_responses.report_error("Произошла ошибка распознавания")
    
    def speak_response(self, text: str):
        """Произнести ответ ассистента"""
        self.tts.speak(text)
        self.dialog_log.add_assistant_message(text)
```

### Шаг 4.2: Интеграция с главным окном

**Обновить файл:** `gui/views/main_window.py`

```python
# Добавить импорт в начало файла
from .voice_assistant_widget import VoiceAssistantWidget

class MainWindow(QMainWindow):
    def __init__(self, project_root):
        super().__init__()
        # Существующий код...
        
        # Добавить голосовой ассистент в setup_ui
        self.setup_voice_assistant()
    
    def setup_voice_assistant(self):
        """Настройка голосового ассистента"""
        # Создаем виджет голосового ассистента
        self.voice_assistant = VoiceAssistantWidget()
        
        # Подключаем сигналы
        self.voice_assistant.command_received.connect(self.handle_voice_command)
        
        # Добавляем в интерфейс (например, как новую вкладку)
        if hasattr(self, 'tab_widget'):
            self.tab_widget.addTab(self.voice_assistant, "🎤 Голосовой ассистент")
    
    def handle_voice_command(self, command: str):
        """Обработка голосовой команды"""
        print(f"🎤 Получена голосовая команда: {command}")
        
        # Здесь можно интегрировать с существующим AI генератором
        # Например, передать команду в macro_generator для создания .atlas файла
        
        # Пример интеграции:
        try:
            # Генерируем макрос из голосовой команды
            # atlas_content = self.ai_generator.generate_from_voice(command)
            
            # Отвечаем пользователю
            self.voice_assistant.speak_response("Макрос создан и выполняется")
            
        except Exception as e:
            self.voice_assistant.speak_response(f"Ошибка выполнения команды: {e}")
```

## 📋 Чек-лист выполнения Этапа 4

- [ ] Создан VoiceAssistantWidget с полным функционалом
- [ ] Реализована визуализация статуса прослушивания
- [ ] Добавлен лог диалогов с цветовой разметкой
- [ ] Создан виджет настроек голоса
- [ ] Интегрирован с главным окном приложения
- [ ] Протестирована работа в GUI режиме
- [ ] Проверена интеграция с предыдущими этапами

## ➡️ Следующий этап

После завершения GUI интеграции переходим к [Этапу 5: Тестирование и оптимизация](./stage-5-testing.md)
