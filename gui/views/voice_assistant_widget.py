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
from PySide6.QtCore import QTimer, Signal, QThread
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.voice.voice_assistant import VoiceAssistant
    from src.voice.speech_recognition import VoiceRecognizer, HotwordDetector
    from src.voice.text_to_speech import TextToSpeech, VoiceAssistantResponses
    from src.memory.state_manager import state_manager
    VOICE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Голосовые модули недоступны: {e}")
    VOICE_MODULES_AVAILABLE = False


class VoiceAssistantThread(QThread):
    """Поток для голосового ассистента"""
    
    voice_command_received = Signal(str)
    status_changed = Signal(str)
    error_occurred = Signal(str)
    assistant_response = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.voice_assistant = None
        self.is_running = False
        
    def initialize_voice(self, recognition_engine: str = "google", tts_engine: str = "macos_say"):
        """Инициализация голосового ассистента"""
        try:
            if VOICE_MODULES_AVAILABLE:
                self.voice_assistant = VoiceAssistant(
                    recognition_engine=recognition_engine,
                    tts_engine=tts_engine
                )
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Ошибка инициализации: {e}")
            return False
    
    def start_listening(self):
        """Начать прослушивание"""
        if not self.voice_assistant:
            self.error_occurred.emit("Голосовой ассистент не инициализирован")
            return
            
        try:
            self.is_running = True
            self.voice_assistant.start()
            self.status_changed.emit("listening")
        except Exception as e:
            self.error_occurred.emit(f"Ошибка запуска прослушивания: {e}")
    
    def stop_listening(self):
        """Остановить прослушивание"""
        try:
            self.is_running = False
            if self.voice_assistant:
                self.voice_assistant.stop()
            self.status_changed.emit("stopped")
        except Exception as e:
            self.error_occurred.emit(f"Ошибка остановки: {e}")
    
    def process_text_command(self, command: str):
        """Обработка текстовой команды"""
        if self.voice_assistant:
            try:
                self.status_changed.emit("processing")
                self.voice_assistant.process_text_command(command)
                self.assistant_response.emit("Команда обработана")
                self.status_changed.emit("listening" if self.is_running else "stopped")
            except Exception as e:
                self.error_occurred.emit(f"Ошибка обработки команды: {e}")


class DialogLogWidget(QTextEdit):
    """Виджет для отображения логов диалогов"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(200)
        
        # Настройка стиля
        font = QFont("Monaco", 10)
        self.setFont(font)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
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
        
        # Стилизация
        self.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #444444;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #444444;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
        """)
        
        # Обновляем список каждые 3 секунды
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_sessions)
        self.update_timer.start(3000)
        
    def update_sessions(self):
        """Обновить список сессий"""
        try:
            if not VOICE_MODULES_AVAILABLE:
                return
                
            # Получаем возобновляемые сессии
            resumable = state_manager.get_resumable_sessions()
            
            # Очищаем список
            self.clear()
            
            if not resumable:
                item = QListWidgetItem("📭 Нет активных сессий")
                item.setData(1, None)
                self.addItem(item)
                return
            
            # Добавляем сессии
            for session in resumable:
                item_text = f"📄 {session.atlas_file} - Шаг {session.current_step}/{session.total_steps}"
                if hasattr(session, 'voice_command') and session.voice_command:
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
        
        # Стилизация
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #444444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Движок распознавания речи
        asr_layout = QHBoxLayout()
        asr_layout.addWidget(QLabel("Распознавание:"))
        self.asr_combo = QComboBox()
        self.asr_combo.addItems(["google", "whisper", "fallback"])
        self.asr_combo.setCurrentText("google")
        asr_layout.addWidget(self.asr_combo)
        layout.addLayout(asr_layout)
        
        # Движок синтеза речи
        tts_layout = QHBoxLayout()
        tts_layout.addWidget(QLabel("Синтез речи:"))
        self.tts_combo = QComboBox()
        self.tts_combo.addItems(["macos_say", "pyttsx3", "fallback"])
        self.tts_combo.setCurrentText("macos_say")
        tts_layout.addWidget(self.tts_combo)
        layout.addLayout(tts_layout)
        
        # Голос
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Голос:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["Milena", "Yuri", "Katya", "Alex"])
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
        
        self.test_btn = QPushButton("🧪 Тест команды")
        self.test_btn.clicked.connect(self.test_command)
        self.test_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                padding: 8px;
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.test_btn)
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
        self.voice_thread.assistant_response.connect(self.on_assistant_response)
        
        self.dialog_log.add_system_message("Голосовой ассистент готов к инициализации")
    
    def start_listening(self):
        """Начать прослушивание"""
        if not VOICE_MODULES_AVAILABLE:
            return
            
        # Инициализируем голосовой ассистент
        recognition_engine = self.settings_widget.asr_combo.currentText()
        tts_engine = self.settings_widget.tts_combo.currentText()
        
        if self.voice_thread.initialize_voice(recognition_engine, tts_engine):
            self.voice_thread.start_listening()
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            
            self.dialog_log.add_system_message(f"Прослушивание начато ({recognition_engine} + {tts_engine})")
        else:
            self.dialog_log.add_error_message("Не удалось инициализировать голосовой ассистент")
    
    def stop_listening(self):
        """Остановить прослушивание"""
        self.voice_thread.stop_listening()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        self.dialog_log.add_system_message("Прослушивание остановлено")
    
    def test_command(self):
        """Тестовая команда"""
        test_commands = [
            "открой Calculator",
            "сделай скриншот", 
            "покажи активное приложение",
            "покажи процессы"
        ]
        
        import random
        command = random.choice(test_commands)
        
        self.dialog_log.add_user_message(f"[ТЕСТ] {command}")
        self.voice_thread.process_text_command(command)
    
    def on_voice_command(self, command: str):
        """Обработка голосовой команды"""
        self.dialog_log.add_user_message(command)
        
        # Эмитируем сигнал для основного приложения
        self.command_received.emit(command)
    
    def on_voice_error(self, error: str):
        """Обработка ошибки голосового ассистента"""
        self.dialog_log.add_error_message(error)
    
    def on_assistant_response(self, response: str):
        """Обработка ответа ассистента"""
        self.dialog_log.add_assistant_message(response)
    
    def speak_response(self, text: str):
        """Произнести ответ ассистента"""
        self.dialog_log.add_assistant_message(text)
        # TTS будет обрабатываться в voice_thread
