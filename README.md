Шаги по созданию и документированию API
Установка необходимых библиотек
Установите Python (если не установлен):

sudo apt update
sudo apt install python3 python3-pip

Установите Django и Django REST Framework:
pip3 install django djangorestframework
Установите PostgreSQL и настройте базу данных (если необходимо):

Установка PostgreSQL:
sudo apt install postgresql postgresql-contrib

Создание базы данных и пользователя:
sudo -u postgres psql
CREATE DATABASE dbname;
CREATE USER username WITH PASSWORD 'password';
ALTER ROLE username SET client_encoding TO 'utf8';
ALTER ROLE username SET default_transaction_isolation TO 'read committed';
ALTER ROLE username SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE dbname TO username;

Клонирование проекта
Склонируйте репозиторий с проектом:
git clone https://github.com/Yanina-t/referal_my.git


Установка зависимостей
Перейдите в каталог вашего проекта и установите необходимые зависимости, указанные в файле requirements.txt:
cd referal_my
pip install -r requirements.txt

Настройка файлов окружения

В данном проекте используется файл .env для хранения конфиденциальных данных и настроек. 
В файле .env_sample предоставляются примеры переменных окружения, которые нужно задать для работы проекта.
Создайте копию файла .env_sample и назовите ее .env:
cp .env_sample .env
Откройте файл .env в текстовом редакторе и установите значения переменных окружения, такие как настройки базы данных, ключи для аутентификации и другие конфиденциальные данные.

Применение миграций

Выполните миграции Django, чтобы создать таблицы базы данных:
python manage.py migrate

Запуск проекта
После завершения настройки вы можете запустить сервер Django для развертывания вашего проекта:
python manage.py runserver

