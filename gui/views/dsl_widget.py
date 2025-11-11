"""
DSL Widget - Виджет для работы с DSL переменными
Интеграция с консольной функциональностью генерации DSL переменных
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTextEdit, QPushButton,
    QLabel, QMessageBox, QFrame, QProgressBar, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from pathlib import Path

# Импорт сервиса
import sys
gui_root = Path(__file__).parent.parent
sys.path.insert(0, str(gui_root))

from services.dsl_service import DSLService

class DSLWorker(QThread):
    """Рабочий поток для операций с DSL переменными"""
    
    progress_updated = Signal(str)
    operation_finished = Signal(bool, str, dict)
    
    def __init__(self, service: DSLService, operation: str, **kwargs):
        super().__init__()
        self.service = service
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        """Выполнение операции"""
        try:
            if self.operation == "generate_variable":
                result = self.service.generate_variable_async(
                    self.kwargs['description'],
                    callback=lambda msg: self.progress_updated.emit(msg)
                )
            elif self.operation == "save_variable":
                result = self.service.save_variable(self.kwargs['variable'])
            elif self.operation == "delete_variable":
                result = self.service.delete_variable(self.kwargs['var_name'])
            else:
                result = {'success': False, 'error': 'Неизвестная операция'}
            
            self.operation_finished.emit(
                result['success'], 
                result.get('message', ''), 
                result
            )
            
        except Exception as e:
            self.operation_finished.emit(False, str(e), {})

class DSLWidget(QWidget):
    """Виджет для работы с DSL переменными"""
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.dsl_service = DSLService(project_root)
        self.current_worker = None
        self.current_variable_data = None
        self.is_operation_running = False
        self.generated_variable = None  # Для хранения сгенерированной переменной
        
        self.setup_ui()
        self.load_variables()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        
        # ГЛАВНЫЙ LAYOUT - без отступов, на весь экран
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ГОРИЗОНТАЛЬНЫЙ СПЛИТТЕР на весь экран
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # ЛЕВАЯ ПАНЕЛЬ
        self.create_left_panel(splitter)
        
        # ПРАВАЯ ПАНЕЛЬ  
        self.create_right_panel(splitter)
        
        # ПРОПОРЦИИ: 400px слева, остальное справа
        splitter.setSizes([400, 1000])
        
    def create_left_panel(self, splitter: QSplitter):
        """Левая панель - список переменных"""
        
        # КОНТЕЙНЕР левой панели
        left_widget = QWidget()
        left_widget.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
                border-right: 1px solid #444444;
            }
        """)
        
        # ВЕРТИКАЛЬНЫЙ LAYOUT на всю высоту
        layout = QVBoxLayout(left_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # ЗАГОЛОВОК
        title = QLabel("📝 DSL ПЕРЕМЕННЫЕ")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #60A5FA;
                padding: 10px 0px;
                border-bottom: 1px solid #444444;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # КНОПКА СОЗДАНИЯ НОВОЙ ПЕРЕМЕННОЙ
        self.create_button = QPushButton("➕ Создать переменную")
        self.create_button.setMinimumHeight(35)
        self.create_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #0D9668;
            }
            QPushButton:pressed {
                background-color: #0A7C5A;
            }
        """)
        self.create_button.clicked.connect(self.create_new_variable)
        layout.addWidget(self.create_button)
        
        # СПИСОК ПЕРЕМЕННЫХ - на всю оставшуюся высоту
        self.variables_list = QListWidget()
        self.variables_list.setStyleSheet("""
            QListWidget {
                background-color: #1E1E1E;
                border: none;
                border-radius: 8px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px 10px;
                border-radius: 6px;
                margin: 2px 0px;
                color: #E0E0E0;
                border: 1px solid transparent;
            }
            QListWidget::item:hover {
                background-color: #3D3D3D;
                border-color: #555555;
            }
            QListWidget::item:selected {
                background-color: #60A5FA;
                color: white;
                border-color: #60A5FA;
            }
        """)
        self.variables_list.itemClicked.connect(self.on_variable_selected)
        
        # ДОБАВЛЯЕМ СПИСОК С РАСТЯЖЕНИЕМ
        layout.addWidget(self.variables_list, 1)  # stretch factor = 1
        
        # СТАТИСТИКА
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #A0A0A0; font-size: 11px; padding: 5px 0px;")
        layout.addWidget(self.stats_label)
        
        splitter.addWidget(left_widget)
        
    def create_right_panel(self, splitter: QSplitter):
        """Правая панель - просмотр и редактирование"""
        
        # КОНТЕЙНЕР правой панели
        right_widget = QWidget()
        right_widget.setStyleSheet("QWidget { background-color: #1E1E1E; }")
        
        # ВЕРТИКАЛЬНЫЙ LAYOUT
        layout = QVBoxLayout(right_widget)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # ЗАГОЛОВОК
        self.content_title = QLabel("Выберите переменную или создайте новую")
        self.content_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.content_title.setStyleSheet("""
            QLabel {
                color: #60A5FA;
                padding: 10px 0px;
                border-bottom: 1px solid #444444;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(self.content_title)
        
        # ОБЛАСТЬ ПРОСМОТРА КОДА
        self.code_viewer = QTextEdit()
        self.code_viewer.setReadOnly(True)
        self.code_viewer.setFont(QFont("Courier New", 12))
        self.code_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #2D2D2D;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 15px;
                color: #E0E0E0;
                line-height: 1.5;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.code_viewer, 1)  # Растягиваем
        
        # КНОПКИ ДЕЙСТВИЙ
        self.create_action_buttons(layout)
        
        # ПАНЕЛЬ РЕЗУЛЬТАТОВ (всегда видна)
        self.create_results_panel(layout)
        
        splitter.addWidget(right_widget)
        
    def create_action_buttons(self, layout: QVBoxLayout):
        """Создание кнопок действий"""
        
        buttons_layout = QHBoxLayout()
        
        # КНОПКА СОХРАНЕНИЯ (для новых переменных)
        self.save_button = QPushButton("💾 СОХРАНИТЬ")
        self.save_button.setMinimumHeight(45)
        self.save_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #0D9668;
            }
            QPushButton:pressed {
                background-color: #0A7C5A;
            }
            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
            }
        """)
        self.save_button.clicked.connect(self.save_variable)
        self.save_button.setEnabled(False)
        self.save_button.setVisible(False)
        buttons_layout.addWidget(self.save_button)
        
        # КНОПКА УДАЛЕНИЯ
        self.delete_button = QPushButton("🗑️ УДАЛИТЬ")
        self.delete_button.setMinimumHeight(45)
        self.delete_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
            }
        """)
        self.delete_button.clicked.connect(self.delete_variable)
        self.delete_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_button)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
    def create_results_panel(self, layout: QVBoxLayout):
        """Панель результатов (всегда видна)"""
        
        # КОНТЕЙНЕР результатов
        self.results_frame = QFrame()
        results_layout = QVBoxLayout(self.results_frame)
        results_layout.setContentsMargins(0, 15, 0, 0)
        results_layout.setSpacing(10)
        
        # ЗАГОЛОВОК результатов
        results_title = QLabel("📊 РЕЗУЛЬТАТ")
        results_title.setFont(QFont("Arial", 14, QFont.Bold))
        results_title.setStyleSheet("color: #10B981; margin-bottom: 5px;")
        results_layout.addWidget(results_title)
        
        # ОБЛАСТЬ ВЫВОДА
        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)
        self.results_output.setFont(QFont("Courier New", 11))
        self.results_output.setMaximumHeight(200)
        self.results_output.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px;
                color: #E0E0E0;
                font-family: monospace;
            }
        """)
        results_layout.addWidget(self.results_output)
        
        # Начальный текст
        self.results_output.setPlainText("Выберите переменную для просмотра или создайте новую...")
        
        # ПРОГРЕСС БАР
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 4px;
                text-align: center;
                background-color: #2D2D2D;
                color: #E0E0E0;
            }
            QProgressBar::chunk {
                background-color: #60A5FA;
                border-radius: 3px;
            }
        """)
        results_layout.addWidget(self.progress_bar)
        
        # СТАТУС
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #A0A0A0; font-size: 11px;")
        results_layout.addWidget(self.status_label)
        
        layout.addWidget(self.results_frame)
        
    def load_variables(self):
        """Загрузка списка переменных"""
        
        self.variables_list.clear()
        
        if not self.dsl_service.is_ai_available():
            item = QListWidgetItem()
            item.setText("❌ AI недоступен\nУстановите библиотеки")
            item.setData(Qt.ItemDataRole.UserRole, None)
            self.variables_list.addItem(item)
            
            self.stats_label.setText("AI недоступен")
            return
        
        # Загружаем переменные
        variables = self.dsl_service.get_variables_list()
        
        if not variables:
            item = QListWidgetItem()
            item.setText("📝 Нет переменных\nСоздайте первую переменную")
            item.setData(Qt.ItemDataRole.UserRole, None)
            self.variables_list.addItem(item)
        else:
            for var in variables:
                item = QListWidgetItem()
                # Добавляем иконку типа переменной
                type_icon = "👤" if var.get('type') == 'user' else "⚙️"
                item.setText(f"{type_icon} {var['display_name']}\n{var['description']}")
                item.setData(Qt.ItemDataRole.UserRole, var)
                self.variables_list.addItem(item)
        
        # Обновляем статистику
        self.update_statistics()
    
    def update_statistics(self):
        """Обновление статистики"""
        
        if not self.dsl_service.is_ai_available():
            self.stats_label.setText("AI недоступен")
            return
        
        stats = self.dsl_service.get_statistics()
        self.stats_label.setText(
            f"Переменных: {stats['total_variables']} | "
            f"Строк кода: {stats['total_lines']} | "
            f"Использований: {stats['total_usage']}"
        )
    
    def on_variable_selected(self, item: QListWidgetItem):
        """Обработка выбора переменной"""
        
        variable = item.data(Qt.ItemDataRole.UserRole)
        if not variable:
            return
        
        self.current_variable_data = variable
        
        # Обновляем заголовок и код
        var_type = variable.get('type', 'user')
        type_label = "👤 Пользовательская" if var_type == 'user' else "⚙️ Системная"
        self.content_title.setText(f"{type_label}: ${{{variable['name']}}}")
        
        # Форматируем код для просмотра
        content = f"# {variable['description']}\n"
        content += f"# Тип: {type_label}\n"
        content += f"# Источник: {variable.get('source', 'Неизвестно')}\n"
        content += f"# Создано: {variable.get('created', 'Неизвестно')}\n"
        content += f"# Использований: {variable.get('usage_count', 0)}\n"
        content += f"# Строк: {variable.get('lines_count', 0)}\n\n"
        content += variable['code']
        
        self.code_viewer.setPlainText(content)
        
        # Активируем кнопки (системные переменные нельзя удалять)
        can_delete = var_type == 'user'
        self.delete_button.setEnabled(can_delete)
        self.save_button.setVisible(False)
        
        # Обновляем результаты
        self.results_output.setPlainText(f"Переменная ${{{variable['name']}}} загружена для просмотра.")
    
    def create_new_variable(self):
        """Создание новой переменной"""
        
        if not self.dsl_service.is_ai_available():
            QMessageBox.warning(
                self,
                "AI недоступен",
                "Для создания переменных необходимо установить AI библиотеки:\n"
                "pip install openai anthropic google-genai"
            )
            return
        
        # Запрашиваем описание
        description, ok = QInputDialog.getText(
            self,
            "Новая DSL переменная",
            "📝 Опишите действие для переменной:\n\n"
            "Примеры:\n"
            "• 'открыть YouTube и найти видео'\n"
            "• 'поставить лайк и пролистать'\n"
            "• 'написать комментарий в TikTok'\n\n"
            "Описание:"
        )
        
        if not ok or not description.strip():
            return
        
        # Запускаем генерацию
        self.start_operation("generate_variable", description=description.strip())
    
    def save_variable(self):
        """Сохранение сгенерированной переменной"""
        
        if not self.generated_variable:
            return
        
        # Предлагаем изменить название
        current_name = self.generated_variable['name']
        new_name, ok = QInputDialog.getText(
            self,
            "Название переменной",
            f"Изменить название переменной?\n\n"
            f"Текущее: ${{{current_name}}}\n\n"
            f"Новое название (или оставьте пустым):",
            text=current_name
        )
        
        if ok and new_name.strip() and new_name.strip() != current_name:
            # Проверяем формат
            if new_name.strip()[0].isupper() and new_name.strip().replace('_', '').isalnum():
                self.generated_variable['name'] = new_name.strip()
            else:
                QMessageBox.warning(
                    self,
                    "Некорректное название",
                    "Название должно начинаться с заглавной буквы и содержать только буквы, цифры и _"
                )
                return
        
        # Сохраняем
        self.start_operation("save_variable", variable=self.generated_variable)
    
    def delete_variable(self):
        """Удаление переменной"""
        
        if not self.current_variable_data:
            return
        
        var_name = self.current_variable_data['name']
        
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Удалить переменную ${{{var_name}}}?\n\n"
            f"Это действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.start_operation("delete_variable", var_name=var_name)
    
    def start_operation(self, operation: str, **kwargs):
        """Запуск операции"""
        
        # Настраиваем прогресс
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Запуск операции...")
        self.results_output.clear()
        
        # Запускаем worker
        self.current_worker = DSLWorker(self.dsl_service, operation, **kwargs)
        self.current_worker.progress_updated.connect(self.on_progress_updated)
        self.current_worker.operation_finished.connect(self.on_operation_finished)
        self.current_worker.start()
    
    def on_progress_updated(self, message: str):
        """Обновление прогресса"""
        self.status_label.setText(message)
        self.results_output.append(message)
        self.results_output.verticalScrollBar().setValue(
            self.results_output.verticalScrollBar().maximum()
        )
    
    def on_operation_finished(self, success: bool, message: str, result: dict):
        """Завершение операции"""
        
        # Завершаем прогресс
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        
        if success:
            self.results_output.append(f"\n{'='*50}")
            self.results_output.append(f"✅ {message}")
            
            # Обрабатываем результат генерации
            if 'variable' in result:
                self.generated_variable = result['variable']
                
                # Показываем предпросмотр
                var = self.generated_variable
                self.content_title.setText(f"Новая переменная: ${{{var['name']}}}")
                
                content = f"# {var['description']}\n"
                content += f"# Создано: {var['created']}\n"
                content += f"# Строк: {len(var['code'].split(chr(10)))}\n\n"
                content += var['code']
                
                self.code_viewer.setPlainText(content)
                
                # Показываем кнопку сохранения
                self.save_button.setVisible(True)
                self.save_button.setEnabled(True)
                self.delete_button.setEnabled(False)
                
                self.results_output.append(f"\n📋 Предпросмотр переменной:")
                self.results_output.append(f"   Название: ${{{var['name']}}}")
                self.results_output.append(f"   Описание: {var['description']}")
                self.results_output.append(f"   Строк кода: {len(var['code'].split(chr(10)))}")
                self.results_output.append(f"\n💾 Нажмите 'Сохранить' для добавления в файл")
            
            # Обновляем список после сохранения/удаления
            if result.get('file_path'):
                self.results_output.append(f"\n📁 Файл: {result['file_path']}")
                self.load_variables()  # Перезагружаем список
                
                # Очищаем состояние
                self.generated_variable = None
                self.current_variable_data = None
                self.content_title.setText("Выберите переменную или создайте новую")
                self.code_viewer.clear()
                self.save_button.setVisible(False)
                self.delete_button.setEnabled(False)
            
            self.status_label.setText("✅ Операция завершена успешно")
        else:
            self.results_output.append(f"\n{'='*50}")
            self.results_output.append(f"❌ {message}")
            
            if 'error' in result and result['error']:
                self.results_output.append(f"\n🔍 Ошибка:")
                self.results_output.append(result['error'])
            
            self.status_label.setText("❌ Операция завершена с ошибкой")
        
        # Прокручиваем вниз
        self.results_output.verticalScrollBar().setValue(
            self.results_output.verticalScrollBar().maximum()
        )
        
        # Очищаем worker
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
