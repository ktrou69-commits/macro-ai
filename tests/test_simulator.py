#!/usr/bin/env python3
"""
test_simulator.py
🎮 ВАЖНО: Тестирование симулятора макросов

Проверяет:
- DSLSimulator класс
- Симуляция DSL команд
- SimulationReport и SimulationStep
- Анализ рисков
- Генерация рекомендаций
- Парсинг DSL
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_simulator_import():
    """Тест импорта симулятора"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Импорт симулятора")
    print("="*60)
    
    try:
        from simulator.dsl_simulator import DSLSimulator, SimulationStep, SimulationReport
        print("✅ DSLSimulator импортирован")
        print("✅ SimulationStep импортирован")
        print("✅ SimulationReport импортирован")
        
        # Проверяем что это классы
        assert callable(DSLSimulator), "DSLSimulator должен быть классом"
        assert callable(SimulationStep), "SimulationStep должен быть классом"
        assert callable(SimulationReport), "SimulationReport должен быть классом"
        print("✅ Все классы валидны")
        
    except ImportError as e:
        print(f"❌ Не удалось импортировать: {e}")
        raise
    
    print()


def test_simulator_initialization():
    """Тест инициализации симулятора"""
    print("="*60)
    print("🧪 Тест 2: Инициализация симулятора")
    print("="*60)
    
    try:
        from simulator.dsl_simulator import DSLSimulator
        
        # Создаём экземпляр
        simulator = DSLSimulator()
        assert simulator is not None, "Симулятор не создался"
        print("✅ DSLSimulator создан")
        
        # Проверяем атрибуты
        assert hasattr(simulator, 'learning_system'), "Нет атрибута learning_system"
        assert hasattr(simulator, 'base_times'), "Нет атрибута base_times"
        print("✅ Все атрибуты на месте")
        
        # Проверяем base_times
        assert 'click' in simulator.base_times, "Нет времени для click"
        assert 'wait' in simulator.base_times, "Нет времени для wait"
        assert 'type' in simulator.base_times, "Нет времени для type"
        print(f"✅ base_times содержит {len(simulator.base_times)} действий")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        raise
    
    print()


def test_simple_dsl_simulation():
    """Тест симуляции простого DSL"""
    print("="*60)
    print("🧪 Тест 3: Симуляция простого DSL")
    print("="*60)
    
    from simulator.dsl_simulator import DSLSimulator
    
    # Простой DSL код
    dsl_code = """
# Простой тест
wait 2s
log "Начало теста"
type Hello World
wait 1s
"""
    
    simulator = DSLSimulator()
    report = simulator.simulate(dsl_code)
    
    assert report is not None, "Отчет не создан"
    print(f"✅ Отчет создан")
    
    assert report.total_steps > 0, "Нет шагов в отчете"
    print(f"✅ Найдено шагов: {report.total_steps}")
    
    assert report.overall_probability > 0, "Вероятность = 0"
    print(f"✅ Общая вероятность: {report.overall_probability*100:.1f}%")
    
    assert report.estimated_total_time > 0, "Время = 0"
    print(f"✅ Ожидаемое время: {report.estimated_total_time:.1f}s")
    
    print()


def test_click_simulation():
    """Тест симуляции клика"""
    print("="*60)
    print("🧪 Тест 4: Симуляция клика")
    print("="*60)
    
    from simulator.dsl_simulator import DSLSimulator
    
    dsl_code = """
click button_template
wait 1s
"""
    
    simulator = DSLSimulator()
    report = simulator.simulate(dsl_code)
    
    assert report.total_steps == 2, f"Ожидалось 2 шага, получено {report.total_steps}"
    print(f"✅ Правильное количество шагов: {report.total_steps}")
    
    # Проверяем первый шаг (click)
    click_step = report.steps[0]
    assert click_step.action == 'click', f"Ожидался click, получен {click_step.action}"
    assert click_step.template_id == 'button_template', "Неверный template_id"
    print(f"✅ Click шаг корректен")
    
    # Проверяем второй шаг (wait)
    wait_step = report.steps[1]
    assert wait_step.action == 'wait', f"Ожидался wait, получен {wait_step.action}"
    assert wait_step.probability == 1.0, "wait должен иметь вероятность 1.0"
    print(f"✅ Wait шаг корректен")
    
    print()


def test_type_simulation():
    """Тест симуляции ввода текста"""
    print("="*60)
    print("🧪 Тест 5: Симуляция ввода текста")
    print("="*60)
    
    from simulator.dsl_simulator import DSLSimulator
    
    dsl_code = """
type Hello World
"""
    
    simulator = DSLSimulator()
    report = simulator.simulate(dsl_code)
    
    assert report.total_steps == 1, "Должен быть 1 шаг"
    
    type_step = report.steps[0]
    assert type_step.action == 'type', "Действие должно быть type"
    
    # Время должно зависеть от длины текста
    text_length = len("Hello World")
    expected_time = text_length * simulator.base_times['type']
    assert abs(type_step.estimated_time - expected_time) < 0.01, "Неверное время для type"
    print(f"✅ Время ввода рассчитано правильно: {type_step.estimated_time:.2f}s")
    
    print()


def test_scroll_simulation():
    """Тест симуляции скролла"""
    print("="*60)
    print("🧪 Тест 6: Симуляция скролла")
    print("="*60)
    
    from simulator.dsl_simulator import DSLSimulator
    
    dsl_code = """
scroll down 5
"""
    
    simulator = DSLSimulator()
    report = simulator.simulate(dsl_code)
    
    assert report.total_steps == 1, "Должен быть 1 шаг"
    
    scroll_step = report.steps[0]
    assert scroll_step.action == 'scroll', "Действие должно быть scroll"
    
    # Время должно зависеть от количества скроллов
    expected_time = 5 * simulator.base_times['scroll']
    assert abs(scroll_step.estimated_time - expected_time) < 0.01, "Неверное время для scroll"
    print(f"✅ Время скролла рассчитано правильно: {scroll_step.estimated_time:.2f}s")
    
    print()


def test_complex_dsl_simulation():
    """Тест симуляции сложного DSL"""
    print("="*60)
    print("🧪 Тест 7: Симуляция сложного DSL")
    print("="*60)
    
    from simulator.dsl_simulator import DSLSimulator
    
    dsl_code = """
# Комплексный тест
log "Начало"
wait 1s
click login_button
wait 2s
type username@example.com
wait 0.5s
click password_field
type MyPassword123
wait 0.5s
click submit_button
wait 3s
log "Завершено"
"""
    
    simulator = DSLSimulator()
    report = simulator.simulate(dsl_code)
    
    print(f"✅ Всего шагов: {report.total_steps}")
    print(f"✅ Общая вероятность: {report.overall_probability*100:.1f}%")
    print(f"✅ Ожидаемое время: {report.estimated_total_time:.1f}s")
    print(f"✅ Рисков: {report.total_risks}")
    
    assert report.total_steps > 5, "Должно быть больше 5 шагов"
    assert report.overall_probability > 0, "Вероятность должна быть > 0"
    assert report.estimated_total_time > 0, "Время должно быть > 0"
    
    print()


def test_simulation_report_methods():
    """Тест методов SimulationReport"""
    print("="*60)
    print("🧪 Тест 8: Методы SimulationReport")
    print("="*60)
    
    from simulator.dsl_simulator import DSLSimulator
    
    dsl_code = """
wait 1s
log "test"
"""
    
    simulator = DSLSimulator()
    report = simulator.simulate(dsl_code)
    
    # Проверяем метод to_dict
    report_dict = report.to_dict()
    assert isinstance(report_dict, dict), "to_dict должен возвращать dict"
    assert 'total_steps' in report_dict, "Нет total_steps в dict"
    assert 'overall_probability' in report_dict, "Нет overall_probability в dict"
    assert 'steps' in report_dict, "Нет steps в dict"
    print("✅ to_dict() работает корректно")
    
    # Проверяем метод print_report (не должен падать)
    try:
        report.print_report()
        print("✅ print_report() работает корректно")
    except Exception as e:
        print(f"❌ print_report() упал: {e}")
        raise
    
    print()


def test_simulation_step_to_dict():
    """Тест метода to_dict у SimulationStep"""
    print("="*60)
    print("🧪 Тест 9: SimulationStep.to_dict()")
    print("="*60)
    
    from simulator.dsl_simulator import SimulationStep
    
    step = SimulationStep(
        step_number=1,
        action='click',
        template_id='test_button',
        probability=0.95,
        estimated_time=0.5,
        risks=['Риск 1'],
        recommendations=['Рекомендация 1']
    )
    
    step_dict = step.to_dict()
    
    assert isinstance(step_dict, dict), "to_dict должен возвращать dict"
    assert step_dict['step_number'] == 1, "Неверный step_number"
    assert step_dict['action'] == 'click', "Неверный action"
    assert step_dict['template_id'] == 'test_button', "Неверный template_id"
    assert step_dict['probability'] == 0.95, "Неверная probability"
    print("✅ SimulationStep.to_dict() работает корректно")
    
    print()


def test_dsl_parser():
    """Тест парсера DSL"""
    print("="*60)
    print("🧪 Тест 10: Парсер DSL")
    print("="*60)
    
    from simulator.dsl_simulator import DSLSimulator
    
    simulator = DSLSimulator()
    
    # Тестируем различные команды
    test_cases = [
        ("click button", [{'action': 'click', 'template_id': 'button'}]),
        ("wait 2s", [{'action': 'wait', 'duration': 2.0}]),
        ("type hello", [{'action': 'type', 'text': 'hello'}]),
        ("scroll down 3", [{'action': 'scroll', 'direction': 'down', 'amount': 3}]),
        ("log test", [{'action': 'log', 'message': 'test'}]),
        ("# comment", []),  # Комментарий должен быть пропущен
        ("", []),  # Пустая строка должна быть пропущена
    ]
    
    for dsl_code, expected in test_cases:
        steps = simulator._parse_dsl(dsl_code)
        
        if len(expected) == 0:
            assert len(steps) == 0, f"Для '{dsl_code}' ожидалось 0 шагов, получено {len(steps)}"
        else:
            assert len(steps) == len(expected), f"Для '{dsl_code}' ожидалось {len(expected)} шагов"
            assert steps[0]['action'] == expected[0]['action'], f"Неверный action для '{dsl_code}'"
    
    print("✅ Парсер DSL работает корректно для всех команд")
    print()


def test_critical_steps_detection():
    """Тест обнаружения критических шагов"""
    print("="*60)
    print("🧪 Тест 11: Обнаружение критических шагов")
    print("="*60)
    
    from simulator.dsl_simulator import SimulationStep, SimulationReport
    
    # Создаём шаги с разной вероятностью
    steps = [
        SimulationStep(1, 'click', 'btn1', 0.95, 0.5, [], []),  # Хороший
        SimulationStep(2, 'click', 'btn2', 0.65, 0.5, [], []),  # Критический
        SimulationStep(3, 'wait', None, 1.0, 1.0, [], []),      # Отличный
        SimulationStep(4, 'click', 'btn3', 0.50, 0.5, [], []),  # Критический
    ]
    
    report = SimulationReport(steps)
    
    # Должно быть 2 критических шага (вероятность < 0.7)
    assert len(report.critical_steps) == 2, f"Ожидалось 2 критических шага, найдено {len(report.critical_steps)}"
    print(f"✅ Найдено критических шагов: {len(report.critical_steps)}")
    
    # Проверяем что правильные шаги помечены как критические
    critical_numbers = [s.step_number for s in report.critical_steps]
    assert 2 in critical_numbers, "Шаг 2 должен быть критическим"
    assert 4 in critical_numbers, "Шаг 4 должен быть критическим"
    print("✅ Критические шаги определены правильно")
    
    print()


def test_overall_probability_calculation():
    """Тест расчета общей вероятности"""
    print("="*60)
    print("🧪 Тест 12: Расчет общей вероятности")
    print("="*60)
    
    from simulator.dsl_simulator import SimulationStep, SimulationReport
    
    # Создаём шаги с известной вероятностью
    steps = [
        SimulationStep(1, 'click', 'btn1', 0.9, 0.5, [], []),
        SimulationStep(2, 'click', 'btn2', 0.8, 0.5, [], []),
    ]
    
    report = SimulationReport(steps)
    
    # Общая вероятность = 0.9 * 0.8 = 0.72
    expected_prob = 0.9 * 0.8
    assert abs(report.overall_probability - expected_prob) < 0.01, \
        f"Ожидалась вероятность {expected_prob}, получена {report.overall_probability}"
    print(f"✅ Общая вероятность рассчитана правильно: {report.overall_probability*100:.1f}%")
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🎮 ТЕСТИРОВАНИЕ СИМУЛЯТОРА".center(60))
    print("="*60)
    print("\nПроверяем симулятор макросов!\n")
    
    tests = [
        test_simulator_import,
        test_simulator_initialization,
        test_simple_dsl_simulation,
        test_click_simulation,
        test_type_simulation,
        test_scroll_simulation,
        test_complex_dsl_simulation,
        test_simulation_report_methods,
        test_simulation_step_to_dict,
        test_dsl_parser,
        test_critical_steps_detection,
        test_overall_probability_calculation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}\n")
            failed += 1
    
    print("="*60)
    if failed == 0:
        print("🎉 ВСЕ ТЕСТЫ СИМУЛЯТОРА ПРОШЛИ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print("\n💡 Симулятор работает отлично!")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ С СИМУЛЯТОРОМ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print(f"❌ Провалено: {failed}/{len(tests)}")
        print("\n💡 Проверьте симулятор!")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
