# 🚀 Проект: Code Review Assistant

Добро пожаловать! Этот репозиторий содержит ассистента для анализа кода и формирования отчета с результатами

---

## 📦 Установка и запуск
### 1. Клонирование репозитория
Склонируйте репозиторий к себе локально:

```
git clone https://github.com/ndlairoke/code-review-assistant.git
cd code-review-assistant
```
### 2. Создание виртуального окружения
Создайте виртуальное окружение:

```
python -m venv venv
source venv/bin/activate   # для Linux/macOS
venv\Scripts\activate      # для Windows
```
### 3. Установка зависимостей 
Установите все необходимые библиотеки:
```
pip install -r requirements.txt
```

## 🤖 Установка и настройка Ollama + Mistral
### 1. Установка Ollama
Склонируйте репозиторий к себе локально:  

- Следуйте инструкциям на [официальном сайте](https://ollama.com)  
- Или используйте команду для быстрой установки (для macOS/Linux):
```
curl -fsSL https://ollama.com/install.sh | sh
```
### 2. Установка модели Mistral
После установки Ollama выполните команду в терминале для локальной загрузки Mistral:
```
ollama pull mistral
```
### 3. Запуск модели Mistral
Запустите модель через Ollama:
```
ollama run mistral
```
Теперь модель активна и готова к работе!