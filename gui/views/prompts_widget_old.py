"""
Prompts Widget - Виджет для просмотра и управления AI промптами
Двухпанельный интерфейс по дизайну из GUI_DESIGN_PLAN.md
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTextEdit, QPushButton,
    QLabel, QMessageBox, QFrame, QProgressBar, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QTextDocument
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

class PromptSyntaxHighlighter(QSyntaxHighlighter):
    """Подсветка синтаксиса для промптов"""
    
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        self.setup_formats()
    
    def setup_formats(self):
        """Настройка форматов подсветки"""
        
        # Заголовки (ЗАДАЧА:, ТРЕБОВАНИЯ:, etc.)
        self.header_format = QTextCharFormat()
        self.header_format.setForeground(QColor("#60A5FA"))
        self.header_format.setFontWeight(QFont.Bold)
        
        # Переменные {platform_name}
        self.variable_format = QTextCharFormat()
        self.variable_format.setForeground(QColor("#F59E0B"))
        
        # Списки (1., 2., •)
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor("#10B981"))
    
    def highlightBlock(self, text: str):
        """Подсветка блока текста"""
        import re
        
        # Заголовки
        for match in re.finditer(r'^[А-ЯA-Z][А-ЯA-Z\s]*:', text, re.MULTILINE):
            self.setFormat(match.start(), match.end() - match.start(), self.header_format)
        
        # Переменные
        for match in re.finditer(r'\{[^}]+\}', text):
            self.setFormat(match.start(), match.end() - match.start(), self.variable_format)
        
        # Списки
        for match in re.finditer(r'^\s*[•\d]+\.?\s', text, re.MULTILINE):
            self.setFormat(match.start(), match.end() - match.start(), self.list_format)

class PromptsWidget(QWidget):
    """Виджет для просмотра AI промптов - двухпанельный интерфейс"""
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.prompts_service = PromptsService(project_root)
        self.current_worker = None
        self.current_prompt_data = None
        
        self.setup_ui()
        self.load_prompts_list()
        
    def setup_ui(self):
        """Настройка двухпанельного интерфейса"""
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем сплиттер для разделения панелей
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Левая панель - список промптов и действий
        self.create_left_panel(splitter)
        
        # Правая панель - просмотр промпта
        self.create_right_panel(splitter)
        
        # Настройка пропорций (400px для левой панели, остальное для правой)
        splitter.setSizes([400, 1000])
        
    def create_left_panel(self, splitter: QSplitter):
        """Создание левой панели со списком промптов"""
        
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-right: 1px solid #444444;
            }
        """)
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(20, 20, 20, 20)  # Увеличили отступы
        left_layout.setSpacing(15)  # Увеличили расстояние между элементами
        
        # Заголовок левой панели
        title_label = QLabel("📁 ДЕЙСТВИЯ С ПРОМПТАМИ")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))  # Увеличили размер
        title_label.setStyleSheet("color: #60A5FA; margin-bottom: 15px; padding: 5px 0px;")
        left_layout.addWidget(title_label)
        
        # Список промптов и действий
        self.prompts_list = QListWidget()
        self.prompts_list.setStyleSheet("""
            QListWidget {
                background-color: #1E1E1E;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 15px 12px;
                border-radius: 6px;
                margin: 3px 0px;
                color: #E0E0E0;
                border: 1px solid transparent;
                min-height: 20px;
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
        self.prompts_list.itemClicked.connect(self.on_item_selected)
        left_layout.addWidget(self.prompts_list, 1)  # Растягиваем список на всю доступную высоту
        
        # Кнопка "Назад" (для навигации)
        self.back_button = QPushButton("← Назад")
        self.back_button.setVisible(False)
        self.back_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #444444;
                border-radius: 6px;
                background-color: #2D2D2D;
                color: #E0E0E0;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
            }
        """)
        self.back_button.clicked.connect(self.go_back)
        left_layout.addWidget(self.back_button)
        
        splitter.addWidget(left_frame)
        
    def create_right_panel(self, splitter: QSplitter):
        """Создание правой панели для просмотра промпта"""
        
        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: #1E1E1E; }")
        
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)  # Нормальные отступы везде
        right_layout.setSpacing(15)  # Увеличили расстояние между элементами
        
        # Заголовок промпта
        self.prompt_title = QLabel("Выберите действие для просмотра")
        self.prompt_title.setFont(QFont("Arial", 18, QFont.Bold))  # Увеличили размер
        self.prompt_title.setStyleSheet("color: #60A5FA; margin-bottom: 15px; padding: 5px 0px;")
        self.prompt_title.setWordWrap(True)
        right_layout.addWidget(self.prompt_title)
        
        # Область просмотра промпта
        self.prompt_viewer = QTextEdit()
        self.prompt_viewer.setReadOnly(True)
        self.prompt_viewer.setFont(QFont("Arial", 14))  # Изменили шрифт
        self.prompt_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #2D2D2D;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 20px;
                color: #E0E0E0;
                line-height: 1.6;
                font-size: 14px;
                selection-background-color: #60A5FA;
            }
        """)
        
        # Подключаем подсветку синтаксиса
        self.syntax_highlighter = PromptSyntaxHighlighter(self.prompt_viewer.document())
        
        right_layout.addWidget(self.prompt_viewer)
        
        # Кнопки действий
        self.create_action_buttons(right_layout)
        
        # НОВАЯ ПАНЕЛЬ РЕЗУЛЬТАТОВ
        self.create_results_panel(right_layout)
        
        splitter.addWidget(right_frame)
        
    def create_action_buttons(self, layout: QVBoxLayout):
        """Создание кнопок действий"""
        
        buttons_layout = QHBoxLayout()
        
        # Кнопка запуска/отмены действия
        self.run_button = QPushButton("▶️ ЗАПУСТИТЬ ОПЕРАЦИЮ")
        self.run_button.setMinimumHeight(50)  # Большая кнопка
        self.run_button.setStyleSheet("""
            QPushButton {
                padding: 15px 25px;
                border: 2px solid #10B981;
                border-radius: 8px;
                background-color: transparent;
                color: #10B981;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #10B981;
                color: white;
                border-color: #0D9668;
            }
            QPushButton:pressed {
                background-color: #0D9668;
                border-color: #0A7C5A;
            }
            QPushButton:disabled {
                border-color: #444444;
                color: #888888;
                background-color: transparent;
            }
        """)
        self.run_button.clicked.connect(self.on_run_button_clicked)
        self.run_button.setEnabled(False)
        self.is_operation_running = False
        
        buttons_layout.addWidget(self.run_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
    
    def create_results_panel(self, layout: QVBoxLayout):
        """Создание панели результатов операций"""
        
        # Создаем контейнер для панели результатов (изначально скрыт)
        self.results_container = QFrame()
        self.results_container.setVisible(False)
        results_container_layout = QVBoxLayout(self.results_container)
        results_container_layout.setContentsMargins(0, 20, 0, 0)
        results_container_layout.setSpacing(10)
        
        # Заголовок панели результатов
        results_title = QLabel("📊 РЕЗУЛЬТАТ ОПЕРАЦИИ")
        results_title.setFont(QFont("Arial", 16, QFont.Bold))
        results_title.setStyleSheet("color: #10B981; margin-bottom: 10px;")
        results_container_layout.addWidget(results_title)
        self.results_title = results_title
        
        # Область вывода результатов
        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)
        self.results_output.setFont(QFont("Courier New", 12))
        self.results_output.setMaximumHeight(200)
        self.results_output.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 15px;
                color: #E0E0E0;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        results_container_layout.addWidget(self.results_output)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 4px;
                text-align: center;
                background-color: #2D2D2D;
                color: #E0E0E0;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #60A5FA;
                border-radius: 3px;
            }
        """)
        results_container_layout.addWidget(self.progress_bar)
        
        # Статус операции
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #A0A0A0; font-size: 12px; margin: 5px 0px;")
        results_container_layout.addWidget(self.status_label)
        
        # Кнопка скрытия результатов
        hide_results_layout = QHBoxLayout()
        hide_results_button = QPushButton("✕ Скрыть результаты")
        hide_results_button.setMaximumWidth(150)
        hide_results_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                border: 1px solid #666666;
                border-radius: 4px;
                background-color: transparent;
                color: #A0A0A0;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
                color: #E0E0E0;
            }
        """)
        hide_results_button.clicked.connect(self.hide_results)
        hide_results_layout.addStretch()
        hide_results_layout.addWidget(hide_results_button)
        results_container_layout.addLayout(hide_results_layout)
        
        # Добавляем контейнер в основной layout
        layout.addWidget(self.results_container)
        
    def load_prompts_list(self):
        """Загрузка списка промптов и действий"""
        
        self.prompts_list.clear()
        
        # Добавляем действия из консольного меню
        actions = [
            {
                'type': 'action',
                'id': 'update_all',
                'title': '🔄 Обновить все промпты',
                'subtitle': 'сканирует templates/',
                'data': {
                    'description': 'Обновление всех промптов через AI',
                    'details': [
                        'Сканирует templates/ и находит все PNG файлы',
                        'AI обновляет TEMPLATES_STRUCTURE.txt',
                        'AI обновляет BEST_PRACTICES.txt',
                        'Регенерирует DSL_REFERENCE.txt'
                    ],
                    'warning': '⚠️ Это займёт 10-20 секунд'
                }
            },
            {
                'type': 'action',
                'id': 'add_platform',
                'title': '➕ Добавить новую платформу',
                'subtitle': 'AI создаст структуру',
                'data': {
                    'description': 'Добавление новой платформы',
                    'details': [
                        'AI создаст структуру названий для фото-шаблонов',
                        'на основе вашего описания действий.',
                        '',
                        'Примеры:',
                        '• Instagram: "открываю Instagram, кликаю лайк, пишу комментарий"',
                        '• Twitter: "открываю Twitter, пишу твит, ставлю лайк, делаю ретвит"',
                        '• LinkedIn: "открываю LinkedIn, ищу вакансии, откликаюсь"'
                    ]
                }
            },
            {
                'type': 'action',
                'id': 'show_structure',
                'title': '📊 Показать структуру шаблонов',
                'subtitle': 'парсит все .png',
                'data': {
                    'description': 'Структура шаблонов',
                    'content': 'Загружается при выборе...'
                }
            },
            {
                'type': 'action',
                'id': 'open_docs',
                'title': '📚 Открыть документацию',
                'subtitle': 'руководства и оптимизация',
                'data': {
                    'description': 'Документация по промптам',
                    'details': [
                        'Доступные документы:',
                        '1. docs/PROMPT_UPDATER_GUIDE.md - Подробное руководство',
                        '2. docs/AI_OPTIMIZATION_SUMMARY.md - Оптимизация AI',
                        '3. docs/AI_PROMPT_OPTIMIZATION.md - Детальное объяснение'
                    ]
                }
            }
        ]
        
        # Добавляем элементы в список
        for action in actions:
            item = QListWidgetItem()
            item.setText(f"{action['title']}\n{action['subtitle']}")
            item.setData(Qt.ItemDataRole.UserRole, action)
            self.prompts_list.addItem(item)
    
    def on_item_selected(self, item: QListWidgetItem):
        """Обработка выбора элемента"""
        
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        self.current_prompt_data = data
        
        # Обновляем заголовок
        self.prompt_title.setText(f"📋 {data['title']}")
        
        # Формируем содержимое для просмотра
        if data['type'] == 'action':
            content = self.format_action_content(data)
        else:
            content = data.get('content', 'Содержимое недоступно')
        
        self.prompt_viewer.setPlainText(content)
        
        # Активируем кнопку запуска
        self.run_button.setEnabled(True)
    
    def on_run_button_clicked(self):
        """Обработка нажатия кнопки запуска/отмены"""
        
        if self.is_operation_running:
            # Отменяем операцию
            self.cancel_operation()
        else:
            # Запускаем операцию
            self.run_action()
    
    def format_action_content(self, action_data: dict) -> str:
        """Форматирование содержимого действия"""
        
        content = f"{action_data['title']}\n"
        content += "=" * 80 + "\n\n"
        
        if 'description' in action_data['data']:
            content += f"{action_data['data']['description']}\n\n"
        
        if 'details' in action_data['data']:
            for detail in action_data['data']['details']:
                if detail:
                    content += f"{detail}\n"
                else:
                    content += "\n"
            content += "\n"
        
        if 'warning' in action_data['data']:
            content += f"{action_data['data']['warning']}\n\n"
        
        # Добавляем специфичную информацию для каждого действия
        if action_data['id'] == 'show_structure':
            # Загружаем структуру шаблонов
            structure_result = self.prompts_service.get_templates_structure()
            if structure_result['success']:
                content += f"📂 Найдено: {structure_result['total_platforms']} папок, {structure_result['total_files']} файлов\n\n"
                for platform, info in structure_result['structure'].items():
                    content += f"📁 {platform}/ ({info['files_count']} файлов)\n"
                    for file_name in info['files'][:3]:  # Показываем первые 3
                        content += f"   • {file_name}\n"
                    if info['files_count'] > 3:
                        content += f"   ... и еще {info['files_count'] - 3}\n"
                    content += "\n"
        
        return content
    
    def run_action(self):
        """Запуск выбранного действия"""
        
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
        """Выполнение показа структуры шаблонов"""
        
        try:
            result = self.prompts_service.get_templates_structure()
            
            if result['success']:
                # Обновляем содержимое в просмотрщике
                self.on_item_selected(self.prompts_list.currentItem())
                QMessageBox.information(
                    self,
                    "Структура шаблонов",
                    f"Найдено {result['total_platforms']} платформ, {result['total_files']} файлов"
                )
            else:
                QMessageBox.warning(self, "Ошибка", result['message'])
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сканирования: {str(e)}")
    
    def execute_open_docs(self):
        """Выполнение открытия документации"""
        
        docs = self.prompts_service.open_documentation()
        existing_docs = [doc for doc in docs if doc['exists']]
        
        if not existing_docs:
            QMessageBox.warning(
                self,
                "Документация не найдена",
                "Файлы документации не найдены в проекте"
            )
            return
        
        # Показываем список доступных документов
        doc_names = [f"{doc['title']}" for doc in existing_docs]
        
        from PySide6.QtWidgets import QInputDialog
        selected_doc, ok = QInputDialog.getItem(
            self,
            "Выберите документ",
            "Доступные документы:",
            doc_names,
            0,
            False
        )
        
        if ok and selected_doc:
            # Находим выбранный документ
            for doc in existing_docs:
                if doc['title'] == selected_doc:
                    success = self.prompts_service.open_file_in_system(doc['full_path'])
                    if success:
                        QMessageBox.information(
                            self,
                            "Документация открыта",
                            f"Файл {doc['name']} открыт в системном редакторе"
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "Ошибка",
                            f"Не удалось открыть файл {doc['name']}"
                        )
                    break
    
    def start_operation(self, operation: str, **kwargs):
        """Запуск операции в отдельном потоке"""
        
        # Показываем весь контейнер результатов
        self.results_container.setVisible(True)
        self.results_output.clear()
        
        # Настраиваем прогресс
        self.progress_bar.setRange(0, 0)  # Бесконечный прогресс
        self.status_label.setText("Запуск операции...")
        
        # Меняем кнопку на "Отменить"
        self.is_operation_running = True
        self.run_button.setText("⏹️ ОТМЕНИТЬ ОПЕРАЦИЮ")
        self.run_button.setStyleSheet("""
            QPushButton {
                padding: 15px 25px;
                border: 2px solid #EF4444;
                border-radius: 8px;
                background-color: transparent;
                color: #EF4444;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: white;
                border-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #DC2626;
                border-color: #B91C1C;
            }
        """)
        
        # Создаем рабочий поток
        self.current_worker = PromptsWorker(self.prompts_service, operation, **kwargs)
        self.current_worker.progress_updated.connect(self.on_progress_updated)
        self.current_worker.operation_finished.connect(self.on_operation_finished)
        self.current_worker.start()
    
    def on_progress_updated(self, message: str):
        """Обновление прогресса"""
        self.status_label.setText(message)
        # Добавляем сообщение в вывод результатов
        self.results_output.append(message)
        # Прокручиваем вниз
        self.results_output.verticalScrollBar().setValue(
            self.results_output.verticalScrollBar().maximum()
        )
    
    def on_operation_finished(self, success: bool, message: str, result: dict):
        """Завершение операции"""
        
        # Скрываем прогресс бар
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        
        if success:
            # Показываем полный результат
            self.results_output.append("\n" + "=" * 80)
            self.results_output.append("✅ " + message)
            
            if 'output' in result and result['output']:
                self.results_output.append("\n📋 Полный вывод:")
                self.results_output.append("-" * 40)
                self.results_output.append(result['output'])
            
            # Показываем информацию о созданных файлах
            if 'files_created' in result:
                self.results_output.append(f"\n📁 Созданные файлы:")
                for file_path in result['files_created']:
                    self.results_output.append(f"   • {file_path}")
            
            self.results_output.append("\n" + "=" * 80)
            self.status_label.setText("✅ Операция завершена успешно")
            
            # Обновляем содержимое если нужно
            if self.current_prompt_data and self.current_prompt_data['id'] == 'show_structure':
                self.on_item_selected(self.prompts_list.currentItem())
                
        else:
            # Показываем ошибку
            self.results_output.append("\n" + "=" * 80)
            self.results_output.append("❌ " + message)
            
            if 'error' in result and result['error']:
                self.results_output.append(f"\n🔍 Детали ошибки:")
                self.results_output.append("-" * 40)
                self.results_output.append(result['error'])
            
            if 'output' in result and result['output']:
                self.results_output.append(f"\n📋 Вывод команды:")
                self.results_output.append("-" * 40)
                self.results_output.append(result['output'])
            
            self.results_output.append("\n" + "=" * 80)
            self.status_label.setText("❌ Операция завершена с ошибкой")
        
        # Прокручиваем вниз
        self.results_output.verticalScrollBar().setValue(
            self.results_output.verticalScrollBar().maximum()
        )
        
        # Возвращаем кнопку в исходное состояние
        self.is_operation_running = False
        self.run_button.setText("▶️ ЗАПУСТИТЬ ОПЕРАЦИЮ")
        self.run_button.setStyleSheet("""
            QPushButton {
                padding: 15px 25px;
                border: 2px solid #10B981;
                border-radius: 8px;
                background-color: transparent;
                color: #10B981;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #10B981;
                color: white;
                border-color: #0D9668;
            }
            QPushButton:pressed {
                background-color: #0D9668;
                border-color: #0A7C5A;
            }
        """)
        
        # Очищаем ссылку на worker
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
    
    def cancel_operation(self):
        """Отмена текущей операции"""
        
        if self.current_worker and self.current_worker.isRunning():
            # Прерываем поток
            self.current_worker.terminate()
            self.current_worker.wait(1000)  # Ждем 1 секунду
            
            # Если не завершился, принудительно убиваем
            if self.current_worker.isRunning():
                self.current_worker.kill()
                self.current_worker.wait()
            
            # Показываем сообщение об отмене
            self.results_output.append("\n" + "=" * 80)
            self.results_output.append("⏹️ ОПЕРАЦИЯ ОТМЕНЕНА ПОЛЬЗОВАТЕЛЕМ")
            self.results_output.append("=" * 80)
            
            self.status_label.setText("⏹️ Операция отменена")
            
            # Возвращаем кнопку в исходное состояние
            self.is_operation_running = False
            self.run_button.setText("▶️ ЗАПУСТИТЬ ОПЕРАЦИЮ")
            self.run_button.setStyleSheet("""
                QPushButton {
                    padding: 15px 25px;
                    border: 2px solid #10B981;
                    border-radius: 8px;
                    background-color: transparent;
                    color: #10B981;
                    font-weight: bold;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #10B981;
                    color: white;
                    border-color: #0D9668;
                }
                QPushButton:pressed {
                    background-color: #0D9668;
                    border-color: #0A7C5A;
                }
            """)
            
            # Скрываем прогресс бар
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)
            
            # Очищаем ссылку на worker
            if self.current_worker:
                self.current_worker.deleteLater()
                self.current_worker = None
    
    def hide_results(self):
        """Скрытие панели результатов"""
        self.results_container.setVisible(False)
    
    def go_back(self):
        """Возврат к списку"""
        self.back_button.setVisible(False)
        self.load_prompts_list()
