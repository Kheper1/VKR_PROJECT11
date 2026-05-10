# Дипломный проект: web-сервис генерации тестов для распределённой базы данных

## 1. Назначение проекта

Тема проекта: **«Разработка web-сервиса генерации тестов для проверки работоспособности распределённой базы данных»**.

Цель проекта: предоставить программистам простой инструмент для проектирования и тестирования приложений распределённых баз данных. На основе формального описания таблицы сервис генерирует SQL-скрипты, контрольный запрос Q0, XML-наборы данных для DBUnit и выполняет проверку корректности изменений.

В проекте используется следующий стек:

- **Visual Studio Code** — основная среда разработки.
- **Python 3.11/3.12** — язык реализации web-сервиса.
- **Flask** — простой web-фреймворк для интерфейса.
- **Docker Desktop** — запуск MySQL-контейнеров.
- **MySQL 8.0** — центральная база данных и базы филиалов.
- **DBUnit** — внешний модуль проверки состояния БД на основе XML datasets.
- **Maven + JUnit** — запуск DBUnit-тестов.

## 2. Важное пояснение по архитектуре

В проекте используется учебная модель распределённой базы данных.

Она состоит из четырёх независимых MySQL-узлов:

| Узел | Назначение | Порт на компьютере |
|---|---|---:|
| `mysql-center` | Центральная БД | `3307` |
| `mysql-branch-1` | БД филиала 1 | `3308` |
| `mysql-branch-2` | БД филиала 2 | `3309` |
| `mysql-branch-3` | БД филиала 3 | `3310` |

В промышленной системе можно использовать настоящую репликацию MySQL. В данном учебном проекте используется более понятный и надёжный механизм: **управляемая консолидация данных через Python**.

Это означает:

1. изменения сначала применяются в базах филиалов;
2. Python-сервис читает данные из филиалов;
3. Python-сервис переносит данные в центральную БД;
4. результат проверяется через Q0 и DBUnit.

Такой вариант проще реализовать, проще объяснить в дипломе и легче защитить.

## 3. Структура проекта

```text
diplom-rdb-test-service/
│
├── docker/
│   ├── docker-compose.yml
│   └── init/
│       ├── center-init.sql
│       ├── branch1-init.sql
│       ├── branch2-init.sql
│       └── branch3-init.sql
│
├── webapp/
│   ├── app.py
│   ├── db.py
│   ├── generator.py
│   ├── checker.py
│   ├── consolidate.py
│   ├── requirements.txt
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── check.html
│   └── static/
│       └── style.css
│
├── generated/
│   ├── readers_schema.json
│   ├── branch1_changes.sql
│   ├── branch2_changes.sql
│   ├── branch3_changes.sql
│   └── Q0.sql
│
├── datasets/
│   ├── initial_readers.xml
│   └── expected_center.xml
│
├── dbunit-tests/
│   ├── pom.xml
│   └── src/test/java/ru/diplom/dbunit/
│       └── ReadersDbUnitTest.java
│
├── results/
│   └── expected_q0_result.json
│
└── README.md
```

## 4. Что делает web-приложение

Web-приложение выполняет следующие функции:

1. принимает описание таблицы `readers`;
2. генерирует SQL-скрипты изменений для трёх филиалов;
3. генерирует запрос `Q0.sql` для центральной БД;
4. генерирует XML datasets для DBUnit;
5. позволяет скачать сгенерированные файлы;
6. запускает консолидацию данных из филиалов в центральную БД;
7. выполняет Q0 на центральной БД;
8. сохраняет результат Q0 в JSON;
9. сравнивает фактический результат Q0 с ожидаемым результатом.

## 5. Установка программ

### 5.1. Visual Studio Code

Установите Visual Studio Code.

Рекомендуемые расширения:

- Python;
- Pylance;
- Docker или Container Tools;
- Extension Pack for Java;
- Maven for Java;
- SQLTools;
- SQLTools MySQL/MariaDB Driver.

### 5.2. Docker Desktop

Установите Docker Desktop и запустите его.

Проверка:

```bash
docker --version
docker compose version
```

Если команды выводят версии, Docker установлен правильно.

### 5.3. Python

Установите Python 3.11 или 3.12.

Проверка:

```bash
python --version
```

Если в Windows команда `python` не работает, попробуйте:

```bash
py --version
```

### 5.4. Java JDK

DBUnit работает в Java-среде, поэтому нужен JDK.

Рекомендуемая версия: **JDK 17**.

Проверка:

```bash
java -version
```

### 5.5. Maven

Maven нужен для запуска DBUnit-теста.

Проверка:

```bash
mvn -version
```

## 6. Открытие проекта в VS Code

1. Откройте VS Code.
2. Нажмите **File → Open Folder**.
3. Выберите папку `diplom-rdb-test-service`.
4. Откройте встроенный терминал: **Terminal → New Terminal**.

Все команды ниже выполняются из терминала VS Code.

## 7. Запуск MySQL-контейнеров

Перейдите в папку `docker`:

```bash
cd docker
```

Запустите контейнеры:

```bash
docker compose up -d
```

Проверьте, что контейнеры работают:

```bash
docker compose ps
```

Должны быть запущены контейнеры:

- `diplom-mysql-center`;
- `diplom-mysql-branch-1`;
- `diplom-mysql-branch-2`;
- `diplom-mysql-branch-3`.

Если нужно полностью пересоздать базы с нуля:

```bash
docker compose down -v
docker compose up -d
```

Команда `down -v` удаляет тома с данными. Используйте её только если нужно сбросить БД к начальному состоянию.

## 8. Проверка подключения к MySQL

Проверка центральной БД:

```bash
docker exec -it diplom-mysql-center mysql -udiplom -pdiplom center_db
```

Внутри MySQL выполните:

```sql
SELECT * FROM readers;
```

Вы должны увидеть три начальные записи:

- Иванов Иван Иванович;
- Петрова Анна Сергеевна;
- Сидоров Пётр Андреевич.

Выход из MySQL:

```sql
exit;
```

## 9. Запуск Python web-сервиса

Вернитесь в корень проекта:

```bash
cd ..
```

Перейдите в папку `webapp`:

```bash
cd webapp
```

Создайте виртуальное окружение:

```bash
python -m venv .venv
```

Активируйте окружение.

Для Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

Для Windows CMD:

```bash
.\.venv\Scripts\activate.bat
```

Для Linux/macOS:

```bash
source .venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Запустите web-сервис:

```bash
python app.py
```

Откройте браузер:

```text
http://127.0.0.1:5000
```

На главной странице должны быть видны четыре MySQL-узла. Если всё настроено правильно, у каждого узла будет статус `OK`.

## 10. Формат таблицы «Читатели»

В проекте используется таблица `readers`.

Её смысловой аналог на русском языке — таблица **«Читатели»**.

Поля таблицы:

| Поле | Назначение |
|---|---|
| `reader_id` | Уникальный идентификатор читателя |
| `full_name` | ФИО читателя |
| `birth_date` | Дата рождения |
| `phone` | Телефон |
| `email` | Электронная почта |
| `branch_id` | Номер филиала |
| `is_deleted` | Признак логического удаления |
| `updated_at` | Дата последнего изменения |

Пример JSON-описания:

```json
{
  "table": "readers",
  "description": "Таблица Читатели",
  "columns": [
    {"name": "reader_id", "type": "INT", "primary_key": true},
    {"name": "full_name", "type": "VARCHAR(255)", "nullable": false},
    {"name": "birth_date", "type": "DATE", "nullable": true},
    {"name": "phone", "type": "VARCHAR(30)", "nullable": true},
    {"name": "email", "type": "VARCHAR(255)", "nullable": true},
    {"name": "branch_id", "type": "INT", "nullable": false},
    {"name": "is_deleted", "type": "BOOLEAN", "nullable": false}
  ]
}
```

## 11. Генерация SQL-скриптов

На главной странице web-приложения можно:

1. вставить JSON-описание таблицы;
2. загрузить JSON/SQL-файл;
3. оставить поле пустым и использовать стандартную структуру;
4. нажать кнопку **«Сгенерировать SQL, Q0 и XML datasets»**.

После генерации создаются файлы:

| Файл | Назначение |
|---|---|
| `branch1_changes.sql` | Изменения для филиала 1 |
| `branch2_changes.sql` | Изменения для филиала 2 |
| `branch3_changes.sql` | Изменения для филиала 3 |
| `Q0.sql` | Контрольный запрос к центральной БД |
| `expected_center.xml` | Ожидаемое состояние центральной БД для DBUnit |
| `initial_readers.xml` | Начальное состояние данных |
| `expected_q0_result.json` | Ожидаемый результат Q0 |

## 12. Применение SQL-скриптов к филиалам

Откройте новый терминал VS Code и перейдите в корень проекта.

### 12.1. Филиал 1

```bash
docker exec -i diplom-mysql-branch-1 mysql -udiplom -pdiplom branch1_db < generated/branch1_changes.sql
```

### 12.2. Филиал 2

```bash
docker exec -i diplom-mysql-branch-2 mysql -udiplom -pdiplom branch2_db < generated/branch2_changes.sql
```

### 12.3. Филиал 3

```bash
docker exec -i diplom-mysql-branch-3 mysql -udiplom -pdiplom branch3_db < generated/branch3_changes.sql
```

Если вы используете PowerShell и символ `<` не работает, используйте такой вариант:

```bash
Get-Content generated/branch1_changes.sql | docker exec -i diplom-mysql-branch-1 mysql -udiplom -pdiplom branch1_db
Get-Content generated/branch2_changes.sql | docker exec -i diplom-mysql-branch-2 mysql -udiplom -pdiplom branch2_db
Get-Content generated/branch3_changes.sql | docker exec -i diplom-mysql-branch-3 mysql -udiplom -pdiplom branch3_db
```

## 13. Что именно меняют SQL-скрипты

Скрипт филиала 1:

- обновляет телефон и email читателя `reader_id = 1`;
- добавляет нового читателя `reader_id = 4`.

Скрипт филиала 2:

- выполняет логическое удаление читателя `reader_id = 2`;
- добавляет нового читателя `reader_id = 5`.

Скрипт филиала 3:

- обновляет email читателя `reader_id = 3`;
- добавляет нового читателя `reader_id = 6`.

После консолидации центральная БД должна содержать шесть записей.

## 14. Консолидация данных

Консолидация — это перенос данных из филиалов в центральную БД.

В web-интерфейсе нажмите:

```text
Выполнить консолидацию
```

После этого Python-приложение:

1. подключится к `branch1_db`;
2. прочитает таблицу `readers`;
3. перенесёт записи в `center_db`;
4. повторит действия для `branch2_db`;
5. повторит действия для `branch3_db`;
6. запишет служебную информацию в таблицу `consolidation_log`.

Также консолидацию можно запустить из терминала:

```bash
cd webapp
python consolidate.py
```

## 15. Выполнение Q0

Q0 — это контрольный запрос к центральной БД.

Содержимое `generated/Q0.sql`:

```sql
SELECT
    reader_id,
    full_name,
    DATE_FORMAT(birth_date, '%Y-%m-%d') AS birth_date,
    phone,
    email,
    branch_id,
    CAST(is_deleted AS UNSIGNED) AS is_deleted
FROM readers
ORDER BY reader_id;
```

В web-интерфейсе нажмите:

```text
Выполнить Q0 на центр.БД
```

Результат будет сохранён в файл:

```text
results/q0_result.json
```

## 16. Проверка результата в web-приложении

После выполнения Q0 нажмите:

```text
Проверить корректность изменений
```

Web-приложение сравнит:

```text
results/q0_result.json
```

с ожидаемым результатом:

```text
results/expected_q0_result.json
```

Если данные совпадают, будет выведено:

```text
Тест пройден. Данные в центральной БД соответствуют ожидаемому результату.
```

Если есть ошибки, приложение покажет список расхождений.

## 17. Запуск DBUnit-теста

DBUnit используется как независимый модуль проверки.

Перед запуском DBUnit должны быть выполнены:

1. запуск Docker-контейнеров;
2. применение SQL-скриптов к филиалам;
3. консолидация данных в центральную БД.

Перейдите в папку DBUnit-модуля:

```bash
cd dbunit-tests
```

Запустите тест:

```bash
mvn test
```

Если всё правильно, Maven завершится успешно.

DBUnit-тест делает следующее:

1. подключается к центральной БД `center_db`;
2. выполняет выборку из таблицы `readers`;
3. загружает ожидаемый XML dataset `datasets/expected_center.xml`;
4. сортирует данные по `reader_id`;
5. сравнивает фактическую таблицу с ожидаемой.

Если данные отличаются, Maven покажет ошибку теста.

## 18. Сценарии тестирования

### 18.1. Проверка целостности данных

В проекте проверяются:

- наличие первичного ключа `reader_id`;
- непустое значение `full_name`;
- корректность `branch_id`;
- базовая корректность email;
- работа триггеров в центральной БД;
- отсутствие лишних или пропущенных записей после консолидации.

Пример ограничения:

```sql
CONSTRAINT chk_center_email CHECK (email IS NULL OR email LIKE '%@%')
```

Пример триггера:

```sql
CREATE TRIGGER trg_readers_before_insert
BEFORE INSERT ON readers
FOR EACH ROW
BEGIN
    IF NEW.full_name IS NULL OR TRIM(NEW.full_name) = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'full_name cannot be empty';
    END IF;
END
```

### 18.2. Тестирование репликации/консолидации

В рамках учебной реализации вместо сложной промышленной репликации используется консолидация.

Проверяется:

- дошли ли данные из филиала 1 до центра;
- дошли ли данные из филиала 2 до центра;
- дошли ли данные из филиала 3 до центра;
- не потерялись ли обновления;
- корректно ли обработано логическое удаление;
- совпадает ли итоговая центральная таблица с ожидаемым XML dataset.

### 18.3. Проверка результата Q0

Q0 выполняется на центральной БД и показывает итоговое состояние данных.

Результат Q0 сравнивается с ожидаемым JSON:

```text
expected_q0_result.json
```

Если все строки и поля совпадают, проверка считается успешной.

## 19. Критерии оценки работоспособности

### 19.1. Согласованность данных

Согласованность проверяется сравнением фактической центральной таблицы с ожидаемым набором данных.

Практический показатель:

```text
Количество расхождений = 0
```

Если DBUnit и Python-проверка не находят расхождений, данные считаются согласованными.

### 19.2. Доступность системы

Доступность можно оценивать через успешность подключений к узлам.

Пример:

```text
Доступность = количество успешных подключений / общее количество проверок * 100%
```

В web-интерфейсе отображается статус каждого узла.

### 19.3. Устойчивость к разделению

Для демонстрации можно остановить один филиал:

```bash
docker stop diplom-mysql-branch-2
```

После этого web-приложение должно:

- показать ошибку подключения к филиалу 2;
- продолжить работу с доступными филиалами;
- не прекращать полностью работу.

Вернуть филиал:

```bash
docker start diplom-mysql-branch-2
```

### 19.4. Отклик системы

Отклик можно измерять временем выполнения Q0 и консолидации.

В базовой версии это можно делать вручную:

```bash
time python consolidate.py
```

На Windows PowerShell:

```bash
Measure-Command { python consolidate.py }
```

### 19.5. Максимальная пропускная способность

В простой учебной версии пропускную способность можно оценить количеством обработанных записей за секунду:

```text
Пропускная способность = количество обработанных записей / время выполнения консолидации
```

Например:

```text
6 записей / 0.2 секунды = 30 записей/сек
```

Для расширенной версии можно добавить генерацию большого количества тестовых читателей.

## 20. Полный демонстрационный сценарий

Ниже приведён сценарий, который удобно показывать на защите.

### Шаг 1. Открыть проект

Открыть папку `diplom-rdb-test-service` в VS Code.

### Шаг 2. Запустить MySQL

```bash
cd docker
docker compose up -d
```

### Шаг 3. Запустить web-сервис

```bash
cd ../webapp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Шаг 4. Открыть браузер

```text
http://127.0.0.1:5000
```

### Шаг 5. Сгенерировать файлы

На главной странице нажать:

```text
Сгенерировать SQL, Q0 и XML datasets
```

### Шаг 6. Применить SQL к филиалам

Из корня проекта:

```bash
docker exec -i diplom-mysql-branch-1 mysql -udiplom -pdiplom branch1_db < generated/branch1_changes.sql
docker exec -i diplom-mysql-branch-2 mysql -udiplom -pdiplom branch2_db < generated/branch2_changes.sql
docker exec -i diplom-mysql-branch-3 mysql -udiplom -pdiplom branch3_db < generated/branch3_changes.sql
```

### Шаг 7. Выполнить консолидацию

В web-интерфейсе нажать:

```text
Выполнить консолидацию
```

### Шаг 8. Выполнить Q0

В web-интерфейсе нажать:

```text
Выполнить Q0 на центр.БД
```

### Шаг 9. Проверить результат

В web-интерфейсе нажать:

```text
Проверить корректность изменений
```

Ожидаемый результат:

```text
Тест пройден.
```

### Шаг 10. Запустить DBUnit

```bash
cd dbunit-tests
mvn test
```

Ожидаемый результат:

```text
BUILD SUCCESS
```

## 21. Типичные ошибки и исправление

### Проверка окружения перед запуском

Перед началом работы обязательно проверьте, что на вашем компьютере доступны команды:

```bash
docker --version
docker compose version
java -version
mvn -version
python --version
```

Если одна из команд не работает, сначала нужно установить соответствующую программу и перезапустить VS Code.

### Ошибка: порт уже занят

Пример:

```text
Bind for 0.0.0.0:3307 failed: port is already allocated
```

Решение:

1. остановите программу, которая занимает порт;
2. или измените порт в `docker/docker-compose.yml`.

Например:

```yaml
ports:
  - "3317:3306"
```

Тогда нужно также изменить порт в `webapp/db.py` и JDBC URL в DBUnit-тесте.

### Ошибка: web-приложение показывает ERROR у MySQL-узлов

Причины:

- Docker Desktop не запущен;
- контейнеры ещё не успели стартовать;
- контейнеры были удалены;
- порт изменён.

Проверка:

```bash
cd docker
docker compose ps
```

### Ошибка: Maven не найден

Пример:

```text
mvn is not recognized
```

Решение:

1. установите Maven;
2. добавьте Maven в PATH;
3. перезапустите VS Code.

### Ошибка: Java не найден

Пример:

```text
java is not recognized
```

Решение:

1. установите JDK 17;
2. настройте переменную `JAVA_HOME`;
3. перезапустите VS Code.

### Ошибка: DBUnit-тест не проходит

Возможные причины:

- SQL-скрипты не были применены к филиалам;
- консолидация не была выполнена;
- центральная БД содержит старые данные;
- XML dataset не совпадает с фактическими данными.

Быстрый сброс:

```bash
cd docker
docker compose down -v
docker compose up -d
```

После сброса повторите демонстрационный сценарий с начала.

## 22. Как объяснить проект в дипломе

Краткое описание:

```text
Разработан web-сервис на языке Python, предназначенный для генерации SQL-скриптов и тестовых данных для проверки работоспособности распределённой базы данных. Распределённая БД моделируется набором MySQL-узлов, развёрнутых в Docker: центральной базой и тремя базами филиалов. Web-сервис принимает описание таблицы «Читатели», генерирует SQL-скрипты изменений для филиалов, контрольный запрос Q0 и XML-наборы данных для DBUnit. После применения изменений и консолидации данных сервис проверяет корректность результата Q0, а DBUnit дополнительно сравнивает фактическое состояние центральной БД с ожидаемым XML dataset.
```

## 23. Минимальная последовательность команд

Если нужно быстро запустить проект с нуля:

```bash
cd docker
docker compose down -v
docker compose up -d
cd ../webapp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

В другом терминале из корня проекта:

```bash
docker exec -i diplom-mysql-branch-1 mysql -udiplom -pdiplom branch1_db < generated/branch1_changes.sql
docker exec -i diplom-mysql-branch-2 mysql -udiplom -pdiplom branch2_db < generated/branch2_changes.sql
docker exec -i diplom-mysql-branch-3 mysql -udiplom -pdiplom branch3_db < generated/branch3_changes.sql
```

В web-интерфейсе:

```text
Выполнить консолидацию → Выполнить Q0 → Проверить корректность изменений
```

DBUnit:

```bash
cd dbunit-tests
mvn test
```
