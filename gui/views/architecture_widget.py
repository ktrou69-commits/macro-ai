"""
Architecture Widget - Виджет для работы с архитектурой шаблонов
Интеграция с консольной функциональностью создания архитектуры шаблонов
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QPushButton,
    QLabel, QMessageBox, QFrame, QProgressBar, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from pathlib import Path

# Импорт сервиса
import sys
gui_root = Path(__file__).parent.parent
sys.path.insert(0, str(gui_root))

from services.architecture_service import ArchitectureService

class ArchitectureWorker(QThread):
    """Рабочий поток для операций с архитектурой"""
    
    progress_updated = Signal(str)
    operation_finished = Signal(bool, str, dict)
    
    def __init__(self, service: ArchitectureService, operation: str, **kwargs):
        super().__init__()
        self.service = service
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        """Выполнение операции"""
        try:
            if self.operation == "generate_architecture":
                result = self.service.generate_architecture_async(
                    self.kwargs['description'],
                    callback=lambda msg: self.progress_updated.emit(msg)
                )
            elif self.operation == "save_architecture":
                result = self.service.save_architecture_to_file(self.kwargs['architecture'])
            elif self.operation == "update_structure":
                result = self.service.update_full_structure(
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

class ArchitectureWidget(QWidget):
    """Виджет для работы с архитектурой шаблонов"""
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.architecture_service = ArchitectureService(project_root)
        self.current_worker = None
        self.is_operation_running = False
        self.generated_architecture = None  # Для хранения сгенерированной архитектуры
        
        self.setup_ui()
        self.load_structure()
        
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
        """Левая панель - древовидная структура шаблонов"""
        
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
        title = QLabel("🏗️ АРХИТЕКТУРА ШАБЛОНОВ")
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
        
        # КНОПКИ ДЕЙСТВИЙ
        buttons_layout = QVBoxLayout()
        
        # Кнопка создания архитектуры
        self.create_arch_button = QPushButton("➕ Создать архитектуру")
        self.create_arch_button.setMinimumHeight(35)
        self.create_arch_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.create_arch_button.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                margin-bottom: 5px;
            }
            QPushButton:hover {
                background-color: #0D9668;
            }
            QPushButton:pressed {
                background-color: #0A7C5A;
            }
        """)
        self.create_arch_button.clicked.connect(self.create_architecture)
        buttons_layout.addWidget(self.create_arch_button)
        
        # Кнопка обновления структуры
        self.update_structure_button = QPushButton("🔄 Обновить структуру")
        self.update_structure_button.setMinimumHeight(35)
        self.update_structure_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.update_structure_button.setStyleSheet("""
            QPushButton {
                background-color: #60A5FA;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #3B82F6;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        self.update_structure_button.clicked.connect(self.update_full_structure)
        buttons_layout.addWidget(self.update_structure_button)
        
        layout.addLayout(buttons_layout)
        
        # ДРЕВОВИДНЫЙ СПИСОК ШАБЛОНОВ - на всю оставшуюся высоту
        self.templates_tree = QTreeWidget()
        self.templates_tree.setHeaderLabel("Структура шаблонов")
        self.templates_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1E1E1E;
                border: none;
                border-radius: 8px;
                padding: 5px;
                font-size: 13px;
                color: #E0E0E0;
            }
            QTreeWidget::item {
                padding: 8px 5px;
                border-radius: 4px;
                margin: 1px 0px;
            }
            QTreeWidget::item:hover {
                background-color: #3D3D3D;
            }
            QTreeWidget::item:selected {
                background-color: #60A5FA;
                color: white;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
        """)
        self.templates_tree.itemClicked.connect(self.on_template_selected)
        
        # ДОБАВЛЯЕМ ДЕРЕВО С РАСТЯЖЕНИЕМ
        layout.addWidget(self.templates_tree, 1)  # stretch factor = 1
        
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
        self.content_title = QLabel("Выберите элемент или создайте архитектуру")
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
        
        # ОБЛАСТЬ ПРОСМОТРА СТРУКТУРЫ
        self.structure_viewer = QTextEdit()
        self.structure_viewer.setReadOnly(True)
        self.structure_viewer.setFont(QFont("Courier New", 12))
        self.structure_viewer.setStyleSheet("""
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
        layout.addWidget(self.structure_viewer, 1)  # Растягиваем
        
        # КНОПКИ ДЕЙСТВИЙ
        self.create_action_buttons(layout)
        
        # ПАНЕЛЬ РЕЗУЛЬТАТОВ (всегда видна)
        self.create_results_panel(layout)
        
        splitter.addWidget(right_widget)
        
    def create_action_buttons(self, layout: QVBoxLayout):
        """Создание кнопок действий"""
        
        buttons_layout = QHBoxLayout()
        
        # КНОПКА СОХРАНЕНИЯ (для новой архитектуры)
        self.save_button = QPushButton("💾 СОХРАНИТЬ В ФАЙЛ")
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
        self.save_button.clicked.connect(self.save_architecture)
        self.save_button.setEnabled(False)
        self.save_button.setVisible(False)
        buttons_layout.addWidget(self.save_button)
        
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
        self.results_output.setPlainText("Выберите элемент структуры или создайте новую архитектуру...")
        
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
        
    def load_structure(self):
        """Загрузка структуры шаблонов"""
        
        self.templates_tree.clear()
        
        if not self.architecture_service.is_ai_available():
            item = QTreeWidgetItem(["❌ AI недоступен"])
            item.setData(0, Qt.ItemDataRole.UserRole, None)
            self.templates_tree.addTopLevelItem(item)
            
            self.stats_label.setText("AI недоступен")
            return
        
        # Загружаем структуру
        structure_info = self.architecture_service.get_current_structure()
        
        if not structure_info['success']:
            item = QTreeWidgetItem([f"❌ Ошибка: {structure_info['error']}"])
            self.templates_tree.addTopLevelItem(item)
            self.stats_label.setText("Ошибка загрузки")
            return
        
        structure = structure_info['structure']
        
        if not structure:
            item = QTreeWidgetItem(["📁 Нет шаблонов"])
            item.setData(0, Qt.ItemDataRole.UserRole, None)
            self.templates_tree.addTopLevelItem(item)
        else:
            # Создаем дерево
            for folder_path, folder_info in sorted(structure.items()):
                # Создаем узел папки
                folder_item = QTreeWidgetItem([f"📁 {folder_path} ({folder_info['count']} файлов)"])
                folder_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'folder', 'data': folder_info})
                
                # Добавляем файлы
                for file_info in sorted(folder_info['files'], key=lambda x: x['name']):
                    file_item = QTreeWidgetItem([f"🖼️ {file_info['short_name']}"])
                    file_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'file', 'data': file_info})
                    folder_item.addChild(file_item)
                
                self.templates_tree.addTopLevelItem(folder_item)
                folder_item.setExpanded(True)  # Разворачиваем папки
        
        # Обновляем статистику
        self.update_statistics()
        
        # Загружаем содержимое файла структуры
        self.load_structure_file()
    
    def load_structure_file(self):
        """Загрузка содержимого файла TEMPLATES_STRUCTURE.txt"""
        
        content = self.architecture_service.get_structure_file_content()
        self.structure_viewer.setPlainText(content)
    
    def update_statistics(self):
        """Обновление статистики"""
        
        if not self.architecture_service.is_ai_available():
            self.stats_label.setText("AI недоступен")
            return
        
        stats = self.architecture_service.get_statistics()
        platforms_text = ", ".join(stats['platforms']) if stats['platforms'] else "Нет"
        
        self.stats_label.setText(
            f"Файлов: {stats['total_files']} | "
            f"Папок: {stats['total_folders']} | "
            f"Платформы: {platforms_text}"
        )
    
    def on_template_selected(self, item: QTreeWidgetItem, column: int):
        """Обработка выбора элемента в дереве"""
        
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not item_data:
            return
        
        if item_data['type'] == 'folder':
            folder_info = item_data['data']
            self.content_title.setText(f"📁 Папка: {folder_info['path']}")
            
            content = f"# Папка: {folder_info['path']}\n"
            content += f"# Количество файлов: {folder_info['count']}\n\n"
            content += "Файлы в папке:\n"
            
            for file_info in folder_info['files']:
                content += f"• {file_info['name']} ({file_info['short_name']})\n"
            
            self.structure_viewer.setPlainText(content)
            
        elif item_data['type'] == 'file':
            file_info = item_data['data']
            self.content_title.setText(f"🖼️ Файл: {file_info['short_name']}")
            
            content = f"# Файл: {file_info['name']}\n"
            content += f"# Короткое имя: {file_info['short_name']}\n"
            content += f"# Полный путь: {file_info['full_path']}\n"
            content += f"# Размер: {file_info['size']} байт\n\n"
            content += "Использование в DSL:\n"
            content += f"click {file_info['short_name']}\n"
            content += f"# или\n"
            content += f"open {file_info['short_name']}"
            
            self.structure_viewer.setPlainText(content)
        
        # Скрываем кнопку сохранения
        self.save_button.setVisible(False)
        
        # Обновляем результаты
        self.results_output.setPlainText(f"Выбран элемент: {item.text(0)}")
    
    def create_architecture(self):
        """Создание новой архитектуры"""
        
        if not self.architecture_service.is_ai_available():
            QMessageBox.warning(
                self,
                "AI недоступен",
                "Для создания архитектуры необходимо установить AI библиотеки и настроить GEMINI_API_KEY"
            )
            return
        
        # Запрашиваем описание
        description, ok = QInputDialog.getText(
            self,
            "Новая архитектура шаблонов",
            "📝 Опишите ваши действия:\n\n"
            "Примеры:\n"
            "• 'Я захожу в настройки, вижу кнопку Wi-Fi, затем нажимаю на сеть'\n"
            "• 'Открываю Instagram, кликаю на лайк, затем на комментарии'\n"
            "• 'Перехожу в Chrome, открываю TikTok, ставлю лайк'\n\n"
            "Описание:"
        )
        
        if not ok or not description.strip():
            return
        
        # Запускаем генерацию
        self.start_operation("generate_architecture", description=description.strip())
    
    def update_full_structure(self):
        """Обновление полной структуры"""
        
        if not self.architecture_service.is_ai_available():
            QMessageBox.warning(
                self,
                "AI недоступен",
                "Для обновления структуры необходимо установить AI библиотеки"
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Обновление структуры",
            "Обновить файл TEMPLATES_STRUCTURE.txt на основе текущих шаблонов?\n\n"
            "⚠️ Это перезапишет существующий файл",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.start_operation("update_structure")
    
    def save_architecture(self):
        """Сохранение сгенерированной архитектуры"""
        
        if not self.generated_architecture:
            return
        
        reply = QMessageBox.question(
            self,
            "Сохранение архитектуры",
            "Добавить эту архитектуру в файл TEMPLATES_STRUCTURE.txt?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.start_operation("save_architecture", architecture=self.generated_architecture)
    
    def start_operation(self, operation: str, **kwargs):
        """Запуск операции"""
        
        # Настраиваем прогресс
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Запуск операции...")
        self.results_output.clear()
        
        # Запускаем worker
        self.current_worker = ArchitectureWorker(self.architecture_service, operation, **kwargs)
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
            
            # Обрабатываем результат генерации архитектуры
            if 'architecture' in result:
                self.generated_architecture = result['architecture']
                
                # Показываем предпросмотр
                self.content_title.setText("Новая архитектура шаблонов")
                self.structure_viewer.setPlainText(self.generated_architecture)
                
                # Показываем кнопку сохранения
                self.save_button.setVisible(True)
                self.save_button.setEnabled(True)
                
                self.results_output.append(f"\n📋 Предпросмотр архитектуры:")
                self.results_output.append(f"   Описание: {result.get('description', '')}")
                self.results_output.append(f"\n💾 Нажмите 'Сохранить в файл' для добавления в TEMPLATES_STRUCTURE.txt")
            
            # Обновляем структуру после сохранения/обновления
            if result.get('file_path'):
                self.results_output.append(f"\n📁 Файл: {result['file_path']}")
                self.load_structure()  # Перезагружаем структуру
                
                # Очищаем состояние
                self.generated_architecture = None
                self.content_title.setText("Выберите элемент или создайте архитектуру")
                self.save_button.setVisible(False)
            
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
