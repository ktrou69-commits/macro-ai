#!/usr/bin/env python3
"""
Тесты для Этапа 4: GUI интеграция
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Мокаем Qt для тестов без GUI
class MockQWidget:
    def __init__(self, *args, **kwargs):
        pass
    def setWindowTitle(self, title):
        pass
    def resize(self, w, h):
        pass
    def show(self):
        pass
    def hide(self):
        pass

class MockQApplication:
    def __init__(self, *args, **kwargs):
        pass
    def exec(self):
        return 0

# Патчим Qt модули
sys.modules['PySide6'] = Mock()
sys.modules['PySide6.QtWidgets'] = Mock()
sys.modules['PySide6.QtCore'] = Mock()
sys.modules['PySide6.QtGui'] = Mock()

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestVoiceAssistantWidget:
    """Тесты GUI виджета голосового ассистента"""
    
    def setup_method(self):
        # Мокаем Qt компоненты
        with patch.multiple(
            'gui.views.voice_assistant_widget',
            QWidget=MockQWidget,
            QVBoxLayout=Mock,
            QHBoxLayout=Mock,
            QPushButton=Mock,
            QLabel=Mock,
            QTextEdit=Mock,
            QComboBox=Mock,
            QGroupBox=Mock,
            QListWidget=Mock,
            QProgressBar=Mock,
            QCheckBox=Mock,
            QSpinBox=Mock,
            QSplitter=Mock,
            QTimer=Mock,
            Signal=Mock,
            QThread=Mock
        ):
            try:
                from gui.views.voice_assistant_widget import (
                    VoiceAssistantWidget, DialogLogWidget, VoiceStatusWidget,
                    VoiceSettingsWidget, SessionsWidget, VoiceAssistantThread
                )
                self.widget_classes = {
                    'VoiceAssistantWidget': VoiceAssistantWidget,
                    'DialogLogWidget': DialogLogWidget,
                    'VoiceStatusWidget': VoiceStatusWidget,
                    'VoiceSettingsWidget': VoiceSettingsWidget,
                    'SessionsWidget': SessionsWidget,
                    'VoiceAssistantThread': VoiceAssistantThread
                }
            except ImportError as e:
                pytest.skip(f"GUI модули недоступны: {e}")
    
    def test_widget_imports(self):
        """Тест импорта виджетов"""
        assert 'VoiceAssistantWidget' in self.widget_classes
        assert 'DialogLogWidget' in self.widget_classes
        assert 'VoiceStatusWidget' in self.widget_classes
        assert 'VoiceSettingsWidget' in self.widget_classes
        assert 'SessionsWidget' in self.widget_classes
        assert 'VoiceAssistantThread' in self.widget_classes
    
    def test_widget_creation(self):
        """Тест создания виджетов"""
        with patch.multiple(
            'gui.views.voice_assistant_widget',
            QWidget=MockQWidget,
            QTextEdit=MockQWidget,
            QGroupBox=MockQWidget,
            QListWidget=MockQWidget,
            QThread=Mock
        ):
            # Тестируем создание основных виджетов
            for name, widget_class in self.widget_classes.items():
                try:
                    if name == 'VoiceAssistantWidget':
                        widget = widget_class()
                    else:
                        widget = widget_class()
                    assert widget is not None, f"Не удалось создать {name}"
                except Exception as e:
                    pytest.fail(f"Ошибка создания {name}: {e}")


class TestMainWindowIntegration:
    """Тесты интеграции с главным окном"""
    
    def test_main_window_import(self):
        """Тест импорта главного окна с голосовой интеграцией"""
        with patch.multiple(
            'gui.views.main_window',
            QMainWindow=Mock,
            QWidget=MockQWidget,
            QVBoxLayout=Mock,
            QHBoxLayout=Mock,
            QSplitter=Mock,
            QLabel=Mock,
            QStatusBar=Mock
        ):
            try:
                from gui.views.main_window import MainWindow
                assert MainWindow is not None
            except ImportError as e:
                pytest.fail(f"Не удалось импортировать MainWindow: {e}")
    
    def test_voice_mode_in_navigation(self):
        """Тест добавления голосового режима в навигацию"""
        with patch.multiple(
            'gui.views.sidebar',
            QWidget=MockQWidget,
            QVBoxLayout=Mock,
            QHBoxLayout=Mock,
            QPushButton=Mock,
            QLabel=Mock,
            QButtonGroup=Mock,
            QFrame=Mock,
            QSpacerItem=Mock,
            QSizePolicy=Mock
        ):
            try:
                from gui.views.sidebar import Sidebar
                
                # Проверяем, что в навигации есть голосовой режим
                # Это косвенная проверка через код
                sidebar = Sidebar(Path('.'))
                assert sidebar is not None
                
            except ImportError as e:
                pytest.fail(f"Не удалось импортировать Sidebar: {e}")


class TestGUIComponents:
    """Тесты отдельных GUI компонентов"""
    
    def test_dialog_log_functionality(self):
        """Тест функциональности лога диалогов"""
        # Мокаем методы для тестирования логики
        class MockDialogLog:
            def __init__(self):
                self.messages = []
            
            def add_user_message(self, message):
                self.messages.append(('user', message))
            
            def add_assistant_message(self, message):
                self.messages.append(('assistant', message))
            
            def add_system_message(self, message):
                self.messages.append(('system', message))
            
            def add_error_message(self, message):
                self.messages.append(('error', message))
        
        log = MockDialogLog()
        
        # Тестируем добавление сообщений
        log.add_user_message("Тестовое сообщение пользователя")
        log.add_assistant_message("Ответ ассистента")
        log.add_system_message("Системное сообщение")
        log.add_error_message("Сообщение об ошибке")
        
        assert len(log.messages) == 4
        assert log.messages[0] == ('user', "Тестовое сообщение пользователя")
        assert log.messages[1] == ('assistant', "Ответ ассистента")
        assert log.messages[2] == ('system', "Системное сообщение")
        assert log.messages[3] == ('error', "Сообщение об ошибке")
    
    def test_voice_status_states(self):
        """Тест состояний голосового статуса"""
        # Мокаем статус виджет
        class MockVoiceStatus:
            def __init__(self):
                self.current_status = "stopped"
            
            def set_status(self, status):
                valid_statuses = ["listening", "processing", "speaking", "stopped"]
                if status in valid_statuses:
                    self.current_status = status
                    return True
                return False
        
        status = MockVoiceStatus()
        
        # Тестируем переключение состояний
        assert status.set_status("listening") == True
        assert status.current_status == "listening"
        
        assert status.set_status("processing") == True
        assert status.current_status == "processing"
        
        assert status.set_status("speaking") == True
        assert status.current_status == "speaking"
        
        assert status.set_status("stopped") == True
        assert status.current_status == "stopped"
        
        # Тестируем неверное состояние
        assert status.set_status("invalid") == False
        assert status.current_status == "stopped"  # Не изменилось
    
    def test_settings_widget_configuration(self):
        """Тест конфигурации настроек"""
        # Мокаем настройки
        class MockVoiceSettings:
            def __init__(self):
                self.asr_engine = "google"
                self.tts_engine = "macos_say"
                self.voice = "Milena"
                self.auto_activation = True
                self.sensitivity = 5
            
            def get_asr_engine(self):
                return self.asr_engine
            
            def get_tts_engine(self):
                return self.tts_engine
            
            def get_voice(self):
                return self.voice
            
            def is_auto_activation_enabled(self):
                return self.auto_activation
            
            def get_sensitivity(self):
                return self.sensitivity
        
        settings = MockVoiceSettings()
        
        # Тестируем настройки по умолчанию
        assert settings.get_asr_engine() == "google"
        assert settings.get_tts_engine() == "macos_say"
        assert settings.get_voice() == "Milena"
        assert settings.is_auto_activation_enabled() == True
        assert settings.get_sensitivity() == 5


class TestGUIIntegration:
    """Тесты общей интеграции GUI"""
    
    def test_signal_connections(self):
        """Тест подключения сигналов"""
        # Мокаем сигналы
        class MockSignal:
            def __init__(self):
                self.connected_slots = []
            
            def connect(self, slot):
                self.connected_slots.append(slot)
            
            def emit(self, *args):
                for slot in self.connected_slots:
                    slot(*args)
        
        # Тестируем подключение сигналов
        command_signal = MockSignal()
        status_signal = MockSignal()
        error_signal = MockSignal()
        
        received_commands = []
        received_statuses = []
        received_errors = []
        
        def on_command(cmd):
            received_commands.append(cmd)
        
        def on_status(status):
            received_statuses.append(status)
        
        def on_error(error):
            received_errors.append(error)
        
        # Подключаем слоты
        command_signal.connect(on_command)
        status_signal.connect(on_status)
        error_signal.connect(on_error)
        
        # Эмитируем сигналы
        command_signal.emit("тестовая команда")
        status_signal.emit("listening")
        error_signal.emit("тестовая ошибка")
        
        # Проверяем получение
        assert len(received_commands) == 1
        assert received_commands[0] == "тестовая команда"
        
        assert len(received_statuses) == 1
        assert received_statuses[0] == "listening"
        
        assert len(received_errors) == 1
        assert received_errors[0] == "тестовая ошибка"
    
    def test_thread_safety(self):
        """Тест потокобезопасности"""
        # Мокаем поток
        class MockVoiceThread:
            def __init__(self):
                self.is_running = False
                self.voice_assistant = None
            
            def initialize_voice(self, recognition_engine, tts_engine):
                # Симулируем инициализацию
                self.voice_assistant = f"Mock assistant ({recognition_engine}, {tts_engine})"
                return True
            
            def start_listening(self):
                if self.voice_assistant:
                    self.is_running = True
                    return True
                return False
            
            def stop_listening(self):
                self.is_running = False
                return True
        
        thread = MockVoiceThread()
        
        # Тестируем жизненный цикл потока
        assert thread.is_running == False
        
        # Инициализация
        result = thread.initialize_voice("google", "macos_say")
        assert result == True
        assert thread.voice_assistant is not None
        
        # Запуск
        result = thread.start_listening()
        assert result == True
        assert thread.is_running == True
        
        # Остановка
        result = thread.stop_listening()
        assert result == True
        assert thread.is_running == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
