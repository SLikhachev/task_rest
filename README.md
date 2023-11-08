# Task Rest v0.2.0

## Web приложение (REST API сервис) для поготовки отчетности по ОМС

Простое web приложение предназначенное для подготовки пакетов с отчетами,
разбора протоколов ошибок и оформления реестров к счетам для страховых компаний.
Использует фреймворк Flask.

Приложение является частью проекта <a href="http://omslite.site" target=_blank>omslite</a>. Более подробное
описание приложения находится <a href="https://docs.omslite.site/admin/task_rest/" target=_blank>по ссылке</a>.

### Установка

В текущей версии приложения предлагается устанавливать код в виртуальное окружение Python
непосредственно из репозитория

[git@github.com:SLikhachev/task_rest.git](git@github.com:SLikhachev/task_rest.git)

Зависимости перечислены в файле `requirements.txt`.

Нужно отметить, что приложение зависит от библиотеки `barsxml`, котрую нужно установить, в первую
очередь из репозитория:

[git@github.com:SLikhachev/barsxml.git](git@github.com:SLikhachev/barsxml.git).

Файлы:

    setup.cfg
    setup.py

в текущей версии приложения не используются.

### Тестирование

Тесты находятся в подкаталоге `./tests`.

В этом же каталоге должен находится подкаталог `data/`. В __data__ будут формироватся тестовые пакеты
для проверки работосбособности кода.

Для тестирования используется библиотека __pytest__, так что, она должна быть установлена в виртуальное
окружение.

Перед запуском тестов следует из шаблонного файла `pytest.ini` создать рабочий файл для тестовой
конфигурации. В этом файле необходимо указать реальные значения переменных окружения:

    DB_HOST= 127.0.0.1
    DB_NAME= dbname
    DB_SCHEMA= dbchema
    DB_USER= dbuser
    DB_PASSWORD= dbpassword
    TEST_YEAR=2022
    TEST_MONTH=03
    MO_CODE=250999
    PACK= xml
    TEST_SIGN= 1
    BARS_ERR_FILE=FHT25M250999_22039992.xml
    BARS_INVOICE_FILE=HM250999S25011_22039994.zip
    BARS_SMO_INVOICE_FILE=HM250796S25011_221079611.zip
    BARS_FOMS_INVOICE_FILE=HM250796T25_22027961.zip

Тестирование еужно призводить в активированном виртуальном окружении python.

Запуск тестов производится командой:

`(venv)> pytest -c pytest_demo.ini`

Для запуска только опреленной функции тестового файла можно использовать команду:

`(venv)> pytest -c pytest_demo.ini tests/test_xml.py::test_xml_pack`

### Подробное описание тестов

#### Аутентифткация токеном JWT

Тесты корректости работы приложения с токеном JWT выполняются в файле `tests/tests_auth.py`.

Для тестирвания нужно создать подкаталог `instance/`в текущей папке (если он еще не создан),
скопировать шаблонный файл `pytest_auth.ini` в `instance/` и указать корректные данные в этой копии
файла `pytest_auth.ini`.

Запустить тест:

`(venv)> pytest -c instance/pytest_auth.ini`

#### Тест

Дальнейшие разделы находятся в разработке.

### Запуск приложения

#### Режим разработчика, приложение Flask

Для запуска приложения в режиме разработчика предназначены файлы:

    flask_conf_local.sh - скрипт установки переменных окружения
    run.py - скрипт создания и запуска приложения Flask в режиме разработчика
    runs.sh - собственно команда запуска приложения на TCP порту 8787

Последовательность команд:

    (venv)$ sh flask_conf_local.sh
    (venv)$ sh runs.sh

#### Режим разработчика gunicorn

Для запуска приложения в режиме задачи для WSGI сервера gunicorn предназначены файлы:

    gunicorn.local.conf.py - файл конфигурации сервера с установленными переменными окружения
    main.py - основной модуль python в котором сознается приложение Flask
    wsgi.py - модуль для создания приложения WSGI как приложения Flask
    start.sh - команда запуска сервера gunicorn с параметрами конфигурации gunicorn.local.conf.py

Запуск сервера:

    (venv)$ sh start.sh

#### Продуктовый режим gunicorn

В продуктовом режиме все преременные окружения и параметры конфигурации приложения необходимо
поместить в отдельный подкаталог `instance/`. Каталог не должен индексироваться __git__.

Пример файла конфигурации (`instace/config_instance.py`):

    ```python
    # place this demo file to instance/ folder, then edit it
    import os

    SECRET_KEY =  'instance secret key'
    JWT_TOKEN_SECRET = 'instance jwt secret'

    # SQL provider string
    SQL_PROVIDER = 'pgrest'
    SQL_PROVIDER = 'postgres'

    # 1st provider definition
    PGREST = { 'srv': os.environ.get('DB_SRV', default='http://localhost:7000')}

    # 2nd provider
    POSTGRES = dict(
        port=os.getenv('DB_PORT') or 5432,
        host=os.getenv('DB_HOST') or '127.0.0.1',
        dbname = os.getenv('DB_NAME') or 'dbname',
        user=os.getenv('DB_USER') or 'postgres',
        password=os.getenv('DB_PASSWORD') or 'dbpass',
        schema=os.getenv('DB_SCHEMA') or 'public',
        dbauth=os.getenv('DB_AUTH') or 'no'
    )

    #dict for registered MO
    #key mo_code_long: (ogrn, )
    STUB_MO_CODE= '000000'
    MOS = {
        '000000': ('0000000000000',),
        '250796': ('1112539013696',)
    }
    ```
Запуск сервера:

    (venv)$ sh start.sh

В файле `start.sh`, нужно указать название реального файла конфигурации для продуктового режима.

#### Продуктовый режим task_rest.service

Предпочтительным режимом запуска задачи в продуктовом режиме является запуск в качестве сервиса (демона).

Для этого нужно в каталог (вариант для __RedHat bsed Linux distros__ )`/etc/systemd/system/` поместить файл
с содержимым

    ```ini
    [Unit]
    Description=Task Rset Flask web application
    After=network.target
    After=postgresql.service
    Requires=postgresql.service
    PartOf=task_ms.service

    [Service]
    Group=task
    User=task
    WorkingDirectory=/home/user/venv/task_rest/webapp
    ExecStart=/home/user/venv/bin/gunicorn --conf gunicorn.conf.py
    Restart=on-failure
    Environment="PATH=/home/user/venv/bin"

    [Install]
    WantedBy=multi-user.target
    WantedBy=task_ms.service
    ```

Конкретные значения параметров конфигурации сервиса исходя из актуальных настроек среды исполнения
и дистрибутива __OS Linux__

Запуск сервиса производится командой:

`sudo systemctl start task_rest.service`

### Запуск приложения в контейнере Docker

Данные раздел находится в разработке

__За подробной документацией обращайтест к автору проекта по электропочте;__

[polaughing@yahoo.com](polaughing@yahoo.com)

[aughing@hotmail.com](aughing@hotmail.com)
