# 📋 DSL Cheatsheet - Шпаргалка

## Основные команды

```
# Запуск приложения
open ChromeApp

# Клик
click Button
click (500, 300)

# Двойной клик
double_click Icon
dclick Icon

# Ввод текста
type "Hello World"

# Клавиши
press enter
press tab
press esc

# Комбинации
hotkey command+t
hotkey ctrl+c

# Пауза
wait 2s
wait 1.5s
wait 500ms

# Скролл
scroll down
scroll up
scroll down 10

# Повторение
repeat 5:
  click Button
  wait 1s
```

## Примеры

### TikTok Like
```
open ChromeApp
wait 2s
click ChromeNewTab
click ChromeSearchField
type "tiktok.com"
press enter
wait 4s

repeat 10:
  click TikTok-Like
  wait 1s
  scroll down
  wait 2s
```

### Chrome Search
```
open ChromeApp
wait 2s
click ChromeNewTab
click ChromeSearchField
type "Python tutorial"
press enter
```

### Multi-Tab
```
open ChromeApp
wait 2s

repeat 3:
  click ChromeNewTab
  wait 0.5s
```

## Запуск

```bash
python3 macro_sequence.py --config script.atlas --run script
```

## Конвертация

```bash
python3 atlas_dsl_parser.py script.atlas script.yaml
```
