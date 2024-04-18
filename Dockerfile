# Используем базовый образ Python
FROM python:3.11

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости через pip
COPY requirements.txt .
RUN pip install -r requirements.txt &&

# Копируем файлы проекта в контейнер
COPY . .
RUN rm -f .env