"""
Prompts Widget - ПОЛНОСТЬЮ ПЕРЕДЕЛАННЫЙ ДИЗАЙН
Простой и чистый интерфейс с правильным использованием пространства
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTextEdit, QPushButton,
    QLabel, QMessageBox, QFrame, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from pathlib import Path

# Импорт сервиса
import sys
gui_root = Path(__file__).parent.parent
sys.path.insert(0, str(gui_root))

from services.prompts_service import PromptsService

class PromptsWorker(QThread):
    """Рабочий поток для операций с промптами"""
    
    progress_updated = Signal(str)
    operation_finished = Signal(bool, str, dict)
    
    def __init__(self, service: PromptsService, operation: str, **kwargs):
        super().__init__()
        self.service = service
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        """Выполнение операции"""
        try:
            if self.operation == "update_prompts":
                result = self.service.update_all_prompts_async(
                    callback=lambda msg: self.progress_updated.emit(msg)
                )
            elif self.operation == "add_platform":
                result = self.service.add_new_platform_async(
                    self.kwargs['platform_name'],
                    self.kwargs['description'],
                    callback=lambda msg: self.progress_updated.emit(msg)
                )
            else:
                result = {'success': False, 'error': 'Неизвестная операция'}
            
            self.operation_finished.emit(
                result['success'], 
                result.get('message', ''), 
                result
            )
            
        except Exception as e:
            self.operation_finished.emit(False, str(e), {})

class PromptsWidget(QWidget):
    """ПЕРЕДЕЛАННЫЙ виджет для работы с промптами"""
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.prompts_service = PromptsService(project_root)
        self.current_worker = None
        self.current_prompt_data = None
        self.is_operation_running = False
        
        self.setup_ui()
        self.load_actions()
        
    def setup_ui(self):
        """Настройка интерфейса - НОВЫЙ ПОДХОД"""
        
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
        """Левая панель - НОВЫЙ ДИЗАЙН"""
        
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
        title = QLabel("📁 ДЕЙСТВИЯ С ПРОМПТАМИ")
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
        
        # СПИСОК ДЕЙСТВИЙ - на всю оставшуюся высоту
        self.actions_list = QListWidget()
        self.actions_list.setStyleSheet("""
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
        self.actions_list.itemClicked.connect(self.on_action_selected)
        
        # ДОБАВЛЯЕМ СПИСОК С РАСТЯЖЕНИЕМ
        layout.addWidget(self.actions_list, 1)  # stretch factor = 1
        
        splitter.addWidget(left_widget)
        
    def create_right_panel(self, splitter: QSplitter):
        """Правая панель - НОВЫЙ ДИЗАЙН"""
        
        # КОНТЕЙНЕР правой панели
        right_widget = QWidget()
        right_widget.setStyleSheet("QWidget { background-color: #1E1E1E; }")
        
        # ВЕРТИКАЛЬНЫЙ LAYOUT
        layout = QVBoxLayout(right_widget)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # ЗАГОЛОВОК
        self.content_title = QLabel("Выберите действие")
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
        
        # ОБЛАСТЬ ОПИСАНИЯ
        self.description_area = QTextEdit()
        self.description_area.setReadOnly(True)
        self.description_area.setFont(QFont("Arial", 13))
        self.description_area.setStyleSheet("""
            QTextEdit {
                background-color: #2D2D2D;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 15px;
                color: #E0E0E0;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.description_area, 1)  # Растягиваем
        
        # КНОПКА ДЕЙСТВИЯ
        self.action_button = QPushButton("▶️ ЗАПУСТИТЬ")
        self.action_button.setMinimumHeight(45)
        self.action_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.action_button.setStyleSheet("""
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
        self.action_button.clicked.connect(self.on_action_button_clicked)
        self.action_button.setEnabled(False)
        layout.addWidget(self.action_button)
        
        # ПАНЕЛЬ РЕЗУЛЬТАТОВ (всегда видна)
        self.create_results_panel(layout)
        
        splitter.addWidget(right_widget)
        
    def create_results_panel(self, layout: QVBoxLayout):
        """Панель результатов"""
        
        # КОНТЕЙНЕР результатов (всегда видимый)
        self.results_frame = QFrame()
        self.results_frame.setVisible(True)
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
        self.results_output.setMaximumHeight(300)
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
        self.results_output.setPlainText("Выберите действие и нажмите 'Запустить' для просмотра результатов...")
        
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
        
        # Убираем кнопку скрытия - панель всегда видна
        
        layout.addWidget(self.results_frame)
        
    def load_actions(self):
        """Загрузка списка действий"""
        
        actions = [
            {
                'id': 'update_all',
                'title': '🔄 Обновить все промпты',
                'subtitle': 'сканирует templates/',
                'description': """🔄 ОБНОВЛЕНИЕ ПРОМПТОВ
================================================================================

Эта функция:
  1. Сканирует templates/ и находит все PNG файлы
  2. AI обновляет TEMPLATES_STRUCTURE.txt
  3. AI обновляет BEST_PRACTICES.txt
  4. Регенерирует DSL_REFERENCE.txt

⚠️  Это займёт 10-20 секунд"""
            },
            {
                'id': 'add_platform',
                'title': '➕ Добавить новую платформу',
                'subtitle': 'AI создаст структуру',
                'description': """➕ ДОБАВЛЕНИЕ НОВОЙ ПЛАТФОРМЫ
================================================================================

AI создаст структуру названий для фото-шаблонов
на основе вашего описания действий.

Примеры:
  • Instagram: "открываю Instagram, кликаю лайк, пишу комментарий"
  • Twitter: "открываю Twitter, пишу твит, ставлю лайк, делаю ретвит"
  • LinkedIn: "открываю LinkedIn, ищу вакансии, откликаюсь"

После нажатия "Запустить" появятся диалоги для ввода данных."""
            },
            {
                'id': 'show_structure',
                'title': '📊 Показать структуру шаблонов',
                'subtitle': 'парсит все .png',
                'description': """📊 СТРУКТУРА ШАБЛОНОВ
================================================================================

Показывает текущую структуру папки templates/:
  • Количество платформ
  • Количество файлов в каждой платформе
  • Список всех PNG файлов

Данные обновляются в реальном времени."""
            },
            {
                'id': 'open_docs',
                'title': '📚 Открыть документацию',
                'subtitle': 'руководства и оптимизация',
                'description': """📚 ДОКУМЕНТАЦИЯ
================================================================================

Доступные документы:
  1. docs/PROMPT_UPDATER_GUIDE.md - Подробное руководство
  2. docs/AI_OPTIMIZATION_SUMMARY.md - Оптимизация AI
  3. docs/AI_PROMPT_OPTIMIZATION.md - Детальное объяснение

После нажатия "Запустить" откроется диалог выбора документа."""
            }
        ]
        
        for action in actions:
            item = QListWidgetItem()
            item.setText(f"{action['title']}\n{action['subtitle']}")
            item.setData(Qt.ItemDataRole.UserRole, action)
            self.actions_list.addItem(item)
    
    def on_action_selected(self, item: QListWidgetItem):
        """Обработка выбора действия"""
        
        action = item.data(Qt.ItemDataRole.UserRole)
        if not action:
            return
        
        self.current_prompt_data = action
        
        # Обновляем заголовок и описание
        self.content_title.setText(action['title'])
        self.description_area.setPlainText(action['description'])
        
        # Активируем кнопку
        self.action_button.setEnabled(True)
    
    def on_action_button_clicked(self):
        """Обработка нажатия кнопки действия"""
        
        if self.is_operation_running:
            self.cancel_operation()
        else:
            self.run_action()
    
    def run_action(self):
        """Запуск действия"""
        
        if not self.current_prompt_data:
            return
        
        action_id = self.current_prompt_data['id']
        
        if action_id == 'update_all':
            self.execute_update_prompts()
        elif action_id == 'add_platform':
            self.execute_add_platform()
        elif action_id == 'show_structure':
            self.execute_show_structure()
        elif action_id == 'open_docs':
            self.execute_open_docs()
    
    def execute_update_prompts(self):
        """Выполнение обновления промптов"""
        
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Обновить все промпты?\n\n⚠️ Это займет 10-20 секунд",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.start_operation("update_prompts")
    
    def execute_add_platform(self):
        """Выполнение добавления платформы"""
        
        from PySide6.QtWidgets import QInputDialog
        
        platform_name, ok = QInputDialog.getText(
            self,
            "Новая платформа",
            "📝 Название платформы (например: Instagram):"
        )
        
        if not ok or not platform_name.strip():
            return
        
        description, ok = QInputDialog.getText(
            self,
            "Описание платформы",
            f"📝 Введите описание действий для {platform_name}:"
        )
        
        if not ok or not description.strip():
            return
        
        self.start_operation("add_platform",
                           platform_name=platform_name.strip(),
                           description=description.strip())
    
    def execute_show_structure(self):
        """Показать структуру шаблонов"""
        
        try:
            result = self.prompts_service.get_templates_structure()
            
            if result['success']:
                # Панель результатов уже видна
                
                output = f"📊 СТРУКТУРА ШАБЛОНОВ\n"
                output += f"{'='*50}\n\n"
                output += f"Всего платформ: {result['total_platforms']}\n"
                output += f"Всего файлов: {result['total_files']}\n\n"
                
                for platform, info in result['structure'].items():
                    output += f"📁 {platform}/ ({info['files_count']} файлов)\n"
                    for file_name in info['files'][:3]:
                        output += f"   • {file_name}\n"
                    if info['files_count'] > 3:
                        output += f"   ... и еще {info['files_count'] - 3}\n"
                    output += "\n"
                
                self.results_output.setPlainText(output)
                self.status_label.setText("✅ Структура загружена")
                
            else:
                QMessageBox.warning(self, "Ошибка", result['message'])
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сканирования: {str(e)}")
    
    def execute_open_docs(self):
        """Открыть документацию"""
        
        docs = self.prompts_service.open_documentation()
        existing_docs = [doc for doc in docs if doc['exists']]
        
        if not existing_docs:
            QMessageBox.warning(self, "Документация не найдена", "Файлы документации не найдены")
            return
        
        from PySide6.QtWidgets import QInputDialog
        
        doc_names = [doc['title'] for doc in existing_docs]
        selected_doc, ok = QInputDialog.getItem(
            self, "Выберите документ", "Доступные документы:", doc_names, 0, False
        )
        
        if ok and selected_doc:
            for doc in existing_docs:
                if doc['title'] == selected_doc:
                    success = self.prompts_service.open_file_in_system(doc['full_path'])
                    if success:
                        QMessageBox.information(self, "Документация открыта", f"Файл {doc['name']} открыт")
                    else:
                        QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл {doc['name']}")
                    break
    
    def start_operation(self, operation: str, **kwargs):
        """Запуск операции"""
        
        # Панель результатов уже видна
        
        # Меняем кнопку на "Отменить"
        self.is_operation_running = True
        self.action_button.setText("⏹️ ОТМЕНИТЬ")
        self.action_button.setStyleSheet("""
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
        """)
        
        # Настраиваем прогресс
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Запуск операции...")
        self.results_output.clear()
        
        # Запускаем worker
        self.current_worker = PromptsWorker(self.prompts_service, operation, **kwargs)
        self.current_worker.progress_updated.connect(self.on_progress_updated)
        self.current_worker.operation_finished.connect(self.on_operation_finished)
        self.current_worker.start()
    
    # Методы show_results() и hide_results() удалены - панель всегда видна
    
    def on_progress_updated(self, message: str):
        """Обновление прогресса"""
        self.status_label.setText(message)
        self.results_output.append(message)
        self.results_output.verticalScrollBar().setValue(
            self.results_output.verticalScrollBar().maximum()
        )
    
    def on_operation_finished(self, success: bool, message: str, result: dict):
        """Завершение операции"""
        
        # Возвращаем кнопку
        self.is_operation_running = False
        self.action_button.setText("▶️ ЗАПУСТИТЬ")
        self.action_button.setStyleSheet("""
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
        """)
        
        # Показываем результат
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        
        if success:
            self.results_output.append(f"\n{'='*50}")
            self.results_output.append(f"✅ {message}")
            
            if 'output' in result and result['output']:
                self.results_output.append(f"\n📋 Полный вывод:")
                self.results_output.append("-" * 30)
                self.results_output.append(result['output'])
            
            if 'files_created' in result:
                self.results_output.append(f"\n📁 Созданные файлы:")
                for file_path in result['files_created']:
                    self.results_output.append(f"   • {file_path}")
            
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
    
    def cancel_operation(self):
        """Отмена операции"""
        
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait(1000)
            
            if self.current_worker.isRunning():
                self.current_worker.kill()
                self.current_worker.wait()
            
            self.results_output.append(f"\n{'='*50}")
            self.results_output.append("⏹️ ОПЕРАЦИЯ ОТМЕНЕНА")
            self.results_output.append("="*50)
            
            self.status_label.setText("⏹️ Операция отменена")
            
            # Возвращаем кнопку
            self.is_operation_running = False
            self.action_button.setText("▶️ ЗАПУСТИТЬ")
            self.action_button.setStyleSheet("""
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
            """)
            
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)
            
            if self.current_worker:
                self.current_worker.deleteLater()
                self.current_worker = None
