#!/usr/bin/env python3
"""
database.py
База данных для хранения примеров выполнения макросов
"""

import sqlite3
import pickle
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np


class ExecutionDatabase:
    """База данных для хранения результатов выполнения"""
    
    def __init__(self, db_path: str = "learning/memory.db"):
        """
        Инициализация базы данных
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Создание таблиц в базе данных"""
        self.conn = sqlite3.connect(str(self.db_path))
        cursor = self.conn.cursor()
        
        # Таблица для хранения выполнений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                screenshot BLOB,
                region_x INTEGER,
                region_y INTEGER,
                region_w INTEGER,
                region_h INTEGER,
                method TEXT,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_for_training BOOLEAN DEFAULT 0
            )
        ''')
        
        # Таблица для хранения метаданных шаблонов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                template_id TEXT PRIMARY KEY,
                total_attempts INTEGER DEFAULT 0,
                successful_attempts INTEGER DEFAULT 0,
                failed_attempts INTEGER DEFAULT 0,
                last_success_timestamp DATETIME,
                last_failure_timestamp DATETIME,
                last_retrain_timestamp DATETIME,
                accuracy REAL DEFAULT 0.0
            )
        ''')
        
        # Индексы для быстрого поиска
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_template_id 
            ON executions(template_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_success 
            ON executions(success)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON executions(timestamp)
        ''')
        
        self.conn.commit()
        print("✅ База данных инициализирована")
    
    def record_execution(
        self, 
        template_id: str, 
        success: bool, 
        screenshot: Optional[np.ndarray] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        method: str = "template_match",
        context: str = ""
    ) -> int:
        """
        Записывает результат выполнения
        
        Args:
            template_id: ID шаблона (например, 'Chrome-tiktok-like-dom')
            success: Успешно ли выполнено
            screenshot: Скриншот области (numpy array)
            region: Регион (x, y, width, height)
            method: Метод поиска ('template_match', 'last_known_position', etc.)
            context: Дополнительная информация
            
        Returns:
            ID записи
        """
        cursor = self.conn.cursor()
        
        # Сериализуем скриншот
        screenshot_blob = None
        if screenshot is not None:
            screenshot_blob = pickle.dumps(screenshot)
        
        # Распаковываем регион
        region_x, region_y, region_w, region_h = region if region else (None, None, None, None)
        
        # Вставляем запись
        cursor.execute('''
            INSERT INTO executions 
            (template_id, success, screenshot, region_x, region_y, region_w, region_h, method, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (template_id, success, screenshot_blob, region_x, region_y, region_w, region_h, method, context))
        
        execution_id = cursor.lastrowid
        
        # Обновляем метаданные шаблона
        self._update_template_metadata(template_id, success)
        
        self.conn.commit()
        
        return execution_id
    
    def _update_template_metadata(self, template_id: str, success: bool):
        """Обновляет метаданные шаблона"""
        cursor = self.conn.cursor()
        
        # Проверяем существует ли шаблон
        cursor.execute('SELECT template_id FROM templates WHERE template_id = ?', (template_id,))
        exists = cursor.fetchone()
        
        if not exists:
            # Создаем новый шаблон
            cursor.execute('''
                INSERT INTO templates (template_id, total_attempts, successful_attempts, failed_attempts)
                VALUES (?, 1, ?, ?)
            ''', (template_id, 1 if success else 0, 0 if success else 1))
        else:
            # Обновляем существующий
            if success:
                cursor.execute('''
                    UPDATE templates 
                    SET total_attempts = total_attempts + 1,
                        successful_attempts = successful_attempts + 1,
                        last_success_timestamp = CURRENT_TIMESTAMP
                    WHERE template_id = ?
                ''', (template_id,))
            else:
                cursor.execute('''
                    UPDATE templates 
                    SET total_attempts = total_attempts + 1,
                        failed_attempts = failed_attempts + 1,
                        last_failure_timestamp = CURRENT_TIMESTAMP
                    WHERE template_id = ?
                ''', (template_id,))
        
        # Пересчитываем accuracy
        cursor.execute('''
            UPDATE templates 
            SET accuracy = CAST(successful_attempts AS REAL) / total_attempts
            WHERE template_id = ?
        ''', (template_id,))
        
        self.conn.commit()
    
    def get_total_attempts(self, template_id: str) -> int:
        """Возвращает общее количество попыток для шаблона"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT total_attempts FROM templates WHERE template_id = ?', (template_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def get_last_success(self, template_id: str) -> Optional[Dict]:
        """Возвращает последнее успешное выполнение"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, screenshot, region_x, region_y, region_w, region_h, timestamp
            FROM executions
            WHERE template_id = ? AND success = 1
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (template_id,))
        
        result = cursor.fetchone()
        if not result:
            return None
        
        screenshot = pickle.loads(result[1]) if result[1] else None
        
        return {
            'id': result[0],
            'screenshot': screenshot,
            'region': (result[2], result[3], result[4], result[5]) if result[2] is not None else None,
            'timestamp': result[6]
        }
    
    def get_examples(
        self, 
        template_id: str, 
        limit: Optional[int] = None,
        only_untrained: bool = False
    ) -> List[Dict]:
        """
        Возвращает примеры для обучения
        
        Args:
            template_id: ID шаблона
            limit: Максимальное количество примеров
            only_untrained: Только неиспользованные для обучения
            
        Returns:
            Список примеров
        """
        cursor = self.conn.cursor()
        
        query = '''
            SELECT id, success, screenshot, region_x, region_y, region_w, region_h, method, context, timestamp
            FROM executions
            WHERE template_id = ?
        '''
        
        if only_untrained:
            query += ' AND used_for_training = 0'
        
        query += ' ORDER BY timestamp DESC'
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (template_id,))
        results = cursor.fetchall()
        
        examples = []
        for row in results:
            screenshot = pickle.loads(row[2]) if row[2] else None
            examples.append({
                'id': row[0],
                'success': bool(row[1]),
                'screenshot': screenshot,
                'region': (row[3], row[4], row[5], row[6]) if row[3] is not None else None,
                'method': row[7],
                'context': row[8],
                'timestamp': row[9]
            })
        
        return examples
    
    def mark_as_trained(self, example_ids: List[int]):
        """Помечает примеры как использованные для обучения"""
        cursor = self.conn.cursor()
        placeholders = ','.join('?' * len(example_ids))
        cursor.execute(f'''
            UPDATE executions 
            SET used_for_training = 1 
            WHERE id IN ({placeholders})
        ''', example_ids)
        self.conn.commit()
    
    def update_retrain_timestamp(self, template_id: str):
        """Обновляет время последнего переобучения"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE templates 
            SET last_retrain_timestamp = CURRENT_TIMESTAMP
            WHERE template_id = ?
        ''', (template_id,))
        self.conn.commit()
    
    def get_statistics(self, template_id: str) -> Dict:
        """Возвращает статистику по шаблону"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT total_attempts, successful_attempts, failed_attempts, 
                   accuracy, last_success_timestamp, last_failure_timestamp,
                   last_retrain_timestamp
            FROM templates
            WHERE template_id = ?
        ''', (template_id,))
        
        result = cursor.fetchone()
        if not result:
            return {
                'total_attempts': 0,
                'successful_attempts': 0,
                'failed_attempts': 0,
                'accuracy': 0.0,
                'last_success': None,
                'last_failure': None,
                'last_retrain': None
            }
        
        return {
            'total_attempts': result[0],
            'successful_attempts': result[1],
            'failed_attempts': result[2],
            'accuracy': result[3],
            'last_success': result[4],
            'last_failure': result[5],
            'last_retrain': result[6]
        }
    
    def get_all_templates(self) -> List[str]:
        """Возвращает список всех шаблонов"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT template_id FROM templates ORDER BY total_attempts DESC')
        return [row[0] for row in cursor.fetchall()]
    
    def close(self):
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Деструктор"""
        self.close()
