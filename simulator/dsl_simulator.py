#!/usr/bin/env python3
"""
dsl_simulator.py
Симуляция выполнения макросов без реальных действий
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

# Добавляем родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from learning import LearningSystem


class SimulationStep:
    """Результат симуляции одного шага"""
    
    def __init__(
        self,
        step_number: int,
        action: str,
        template_id: Optional[str],
        probability: float,
        estimated_time: float,
        risks: List[str],
        recommendations: List[str]
    ):
        self.step_number = step_number
        self.action = action
        self.template_id = template_id
        self.probability = probability
        self.estimated_time = estimated_time
        self.risks = risks
        self.recommendations = recommendations
    
    def to_dict(self) -> Dict:
        """Конвертация в словарь"""
        return {
            'step_number': self.step_number,
            'action': self.action,
            'template_id': self.template_id,
            'probability': self.probability,
            'estimated_time': self.estimated_time,
            'risks': self.risks,
            'recommendations': self.recommendations
        }


class SimulationReport:
    """Отчет о симуляции"""
    
    def __init__(self, steps: List[SimulationStep]):
        self.steps = steps
        self.total_steps = len(steps)
        self.overall_probability = self._calculate_overall_probability()
        self.estimated_total_time = sum(s.estimated_time for s in steps)
        self.total_risks = sum(len(s.risks) for s in steps)
        self.critical_steps = [s for s in steps if s.probability < 0.7]
    
    def _calculate_overall_probability(self) -> float:
        """Вычисляет общую вероятность успеха"""
        if not self.steps:
            return 0.0
        
        # Общая вероятность = произведение вероятностей всех шагов
        prob = 1.0
        for step in self.steps:
            prob *= step.probability
        
        return prob
    
    def to_dict(self) -> Dict:
        """Конвертация в словарь"""
        return {
            'total_steps': self.total_steps,
            'overall_probability': self.overall_probability,
            'estimated_total_time': self.estimated_total_time,
            'total_risks': self.total_risks,
            'critical_steps_count': len(self.critical_steps),
            'steps': [s.to_dict() for s in self.steps]
        }
    
    def print_report(self):
        """Вывод отчета в консоль"""
        print("\n" + "="*60)
        print("📋 ОТЧЕТ О СИМУЛЯЦИИ")
        print("="*60)
        
        # Общая информация
        print(f"\n📊 Общая информация:")
        print(f"   Всего шагов: {self.total_steps}")
        print(f"   Вероятность успеха: {self.overall_probability*100:.1f}%")
        print(f"   Ожидаемое время: {self.estimated_total_time:.1f}s ({self.estimated_total_time/60:.1f}m)")
        print(f"   Обнаружено рисков: {self.total_risks}")
        
        # Оценка
        if self.overall_probability >= 0.9:
            print(f"   ✅ Оценка: ОТЛИЧНО")
        elif self.overall_probability >= 0.7:
            print(f"   ⚠️  Оценка: ХОРОШО (есть риски)")
        elif self.overall_probability >= 0.5:
            print(f"   ⚠️  Оценка: СРЕДНЕ (много рисков)")
        else:
            print(f"   ❌ Оценка: ПЛОХО (высокий риск неудачи)")
        
        # Критические шаги
        if self.critical_steps:
            print(f"\n⚠️  Критические шаги (вероятность < 70%):")
            for step in self.critical_steps:
                print(f"   Шаг {step.step_number}: {step.action} - {step.probability*100:.1f}%")
        
        # Детали по шагам
        print(f"\n📝 Детали по шагам:")
        print("-"*60)
        
        for step in self.steps:
            # Иконка статуса
            if step.probability >= 0.9:
                status = "✅"
            elif step.probability >= 0.7:
                status = "⚠️ "
            else:
                status = "❌"
            
            print(f"\n{status} Шаг {step.step_number}: {step.action}")
            
            if step.template_id:
                print(f"   Шаблон: {step.template_id}")
            
            print(f"   Вероятность: {step.probability*100:.1f}%")
            print(f"   Время: ~{step.estimated_time:.1f}s")
            
            if step.risks:
                print(f"   ⚠️  Риски:")
                for risk in step.risks:
                    print(f"      - {risk}")
            
            if step.recommendations:
                print(f"   💡 Рекомендации:")
                for rec in step.recommendations:
                    print(f"      - {rec}")
        
        print("\n" + "="*60)


class DSLSimulator:
    """Симуляция выполнения DSL макросов"""
    
    def __init__(self, learning_system: Optional[LearningSystem] = None):
        """
        Инициализация симулятора
        
        Args:
            learning_system: Система обучения для получения статистики
        """
        self.learning_system = learning_system or LearningSystem(db_path="learning/memory.db")
        
        # Базовые оценки времени для разных действий
        self.base_times = {
            'click': 0.5,
            'wait': 1.0,
            'type': 0.1,  # за символ
            'scroll': 0.3,
            'selenium_click': 1.0,
            'selenium_type': 0.2,
            'log': 0.01,
            'repeat': 0.1,
        }
    
    def simulate(self, dsl_code: str) -> SimulationReport:
        """
        Симулирует выполнение DSL кода
        
        Args:
            dsl_code: DSL код для симуляции
            
        Returns:
            Отчет о симуляции
        """
        # Парсим DSL
        steps = self._parse_dsl(dsl_code)
        
        # Симулируем каждый шаг
        simulation_steps = []
        
        for i, step in enumerate(steps, 1):
            sim_step = self._simulate_step(i, step)
            simulation_steps.append(sim_step)
        
        return SimulationReport(simulation_steps)
    
    def _parse_dsl(self, dsl_code: str) -> List[Dict]:
        """
        Простой парсер DSL
        
        Args:
            dsl_code: DSL код
            
        Returns:
            Список шагов
        """
        steps = []
        lines = dsl_code.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Пропускаем комментарии и пустые строки
            if not line or line.startswith('#'):
                continue
            
            # Парсим команду
            parts = line.split()
            if not parts:
                continue
            
            action = parts[0].lower()
            
            # Определяем тип действия
            if action == 'click':
                steps.append({
                    'action': 'click',
                    'template_id': parts[1] if len(parts) > 1 else None
                })
            
            elif action == 'wait':
                duration = float(parts[1].replace('s', '')) if len(parts) > 1 else 1.0
                steps.append({
                    'action': 'wait',
                    'duration': duration
                })
            
            elif action == 'type':
                text = ' '.join(parts[1:])
                steps.append({
                    'action': 'type',
                    'text': text
                })
            
            elif action == 'scroll':
                direction = parts[1] if len(parts) > 1 else 'down'
                amount = int(parts[2]) if len(parts) > 2 else 1
                steps.append({
                    'action': 'scroll',
                    'direction': direction,
                    'amount': amount
                })
            
            elif action == 'repeat':
                count = int(parts[1].replace(':', '')) if len(parts) > 1 else 1
                steps.append({
                    'action': 'repeat',
                    'count': count
                })
            
            elif action == 'log':
                message = ' '.join(parts[1:]).strip('"')
                steps.append({
                    'action': 'log',
                    'message': message
                })
            
            elif action == 'selenium_connect':
                steps.append({
                    'action': 'selenium_connect'
                })
            
            else:
                # Неизвестная команда
                steps.append({
                    'action': 'unknown',
                    'raw': line
                })
        
        return steps
    
    def _simulate_step(self, step_number: int, step: Dict) -> SimulationStep:
        """
        Симулирует один шаг
        
        Args:
            step_number: Номер шага
            step: Данные шага
            
        Returns:
            Результат симуляции шага
        """
        action = step['action']
        template_id = step.get('template_id')
        
        # Получаем статистику из Learning System
        if template_id:
            stats = self.learning_system.db.get_statistics(template_id)
            probability = stats['accuracy'] if stats['total_attempts'] > 0 else 0.5
            
            # Оценка времени на основе истории
            examples = self.learning_system.db.get_examples(template_id, limit=10)
            if examples:
                # Используем базовое время + небольшой разброс
                estimated_time = self.base_times.get(action, 1.0)
            else:
                estimated_time = self.base_times.get(action, 1.0)
        else:
            # Нет шаблона - используем базовые оценки
            probability = 0.95  # Высокая вероятность для простых действий
            estimated_time = self.base_times.get(action, 1.0)
        
        # Корректировка времени для специфичных действий
        if action == 'wait':
            estimated_time = step.get('duration', 1.0)
            probability = 1.0  # wait всегда успешен
        
        elif action == 'type':
            text = step.get('text', '')
            estimated_time = len(text) * self.base_times['type']
            probability = 0.98
        
        elif action == 'scroll':
            amount = step.get('amount', 1)
            estimated_time = self.base_times['scroll'] * amount
            probability = 0.99
        
        elif action == 'repeat':
            count = step.get('count', 1)
            estimated_time = self.base_times['repeat'] * count
            probability = 1.0
        
        elif action == 'log':
            estimated_time = self.base_times['log']
            probability = 1.0
        
        # Анализ рисков
        risks = self._analyze_risks(step, probability, stats if template_id else None)
        
        # Рекомендации
        recommendations = self._generate_recommendations(step, probability, risks)
        
        return SimulationStep(
            step_number=step_number,
            action=action,
            template_id=template_id,
            probability=probability,
            estimated_time=estimated_time,
            risks=risks,
            recommendations=recommendations
        )
    
    def _analyze_risks(self, step: Dict, probability: float, stats: Optional[Dict]) -> List[str]:
        """
        Анализирует риски для шага
        
        Args:
            step: Данные шага
            probability: Вероятность успеха
            stats: Статистика из Learning System
            
        Returns:
            Список рисков
        """
        risks = []
        
        # Низкая вероятность успеха
        if probability < 0.7:
            risks.append(f"Низкая вероятность успеха ({probability*100:.1f}%)")
        
        # Нет исторических данных
        if stats and stats['total_attempts'] == 0:
            risks.append("Нет исторических данных - первый запуск")
        
        # Много неудач в истории
        if stats and stats['failed_attempts'] > stats['successful_attempts']:
            risks.append(f"Больше неудач чем успехов в истории ({stats['failed_attempts']} vs {stats['successful_attempts']})")
        
        # Давно не было успехов
        if stats and stats['last_success']:
            last_success = datetime.fromisoformat(stats['last_success'])
            if datetime.now() - last_success > timedelta(days=7):
                risks.append("Последний успех был более 7 дней назад")
        
        # Недавно было переобучение
        if stats and stats['last_retrain']:
            last_retrain = datetime.fromisoformat(stats['last_retrain'])
            if datetime.now() - last_retrain < timedelta(hours=1):
                risks.append("Недавно было переобучение - модель может быть нестабильной")
        
        return risks
    
    def _generate_recommendations(self, step: Dict, probability: float, risks: List[str]) -> List[str]:
        """
        Генерирует рекомендации для улучшения
        
        Args:
            step: Данные шага
            probability: Вероятность успеха
            risks: Список рисков
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # Рекомендации на основе вероятности
        if probability < 0.5:
            recommendations.append("Критически низкая вероятность - рекомендуется проверить шаблон")
        elif probability < 0.7:
            recommendations.append("Добавьте wait перед этим шагом для стабильности")
        
        # Рекомендации на основе рисков
        if "Нет исторических данных" in ' '.join(risks):
            recommendations.append("Запустите макрос несколько раз для накопления статистики")
        
        if "Больше неудач" in ' '.join(risks):
            recommendations.append("Обновите шаблон или проверьте селектор")
        
        if "Последний успех был более" in ' '.join(risks):
            recommendations.append("Возможно изменился дизайн - проверьте актуальность шаблона")
        
        # Общие рекомендации
        if step['action'] == 'click' and not recommendations:
            recommendations.append("Добавьте wait после клика для ожидания загрузки")
        
        return recommendations


def simulate_from_file(file_path: str) -> SimulationReport:
    """
    Симулирует выполнение макроса из файла
    
    Args:
        file_path: Путь к .atlas файлу
        
    Returns:
        Отчет о симуляции
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        dsl_code = f.read()
    
    simulator = DSLSimulator()
    return simulator.simulate(dsl_code)


def main():
    """Главная функция для тестирования"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Симуляция DSL макросов')
    parser.add_argument('file', help='Путь к .atlas файлу')
    parser.add_argument('--json', action='store_true', help='Вывод в JSON формате')
    
    args = parser.parse_args()
    
    # Симуляция
    report = simulate_from_file(args.file)
    
    if args.json:
        # JSON вывод
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        # Красивый вывод
        report.print_report()


if __name__ == '__main__':
    main()
