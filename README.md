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

## ✅ Запуск и использование API
### 1. Запуск API
Запустите сервер:
```
uvicorn api:app --reload
```
Сервер запустится по адресу http://127.0.0.1:8000

### 2. Выполните POST-запрос
Выполните POST-запрос к серверу через cmd, powershell, bash или postman. 

Пример POST-запроса в cmd:
```
curl -X POST "http://127.0.0.1:8000/generate-report" \
-H "Content-Type: application/json" \
-d '{
  "github_url": "https://github.com/example/example",
  "email": "user@example.com",
  "start_date": "2023-01-01T00:00:00Z",
  "end_date": "2024-01-01T00:00:00Z"
}' \
-o "report.pdf"
```
Параметры:
`github_url` - URL Github-репозиторий для анализа

`email` - Email автора для анализа

`start_date` - Начальная дата анализа (ISO формат)

`end_date` - Конечная дата анализа (ISO формат)

Отчёт автоматически скачивается в текущую директорию с именем `report.pdf`.
Чтобы указать свой путь:
```
-o "/path/to/your/report.pdf"
```
Для доступа к приватным репозиториям в заголовке POST-запроса укажите токен Github:
```
-H "Authorization: Bearer github_token_11AABBCCDD..." \
```