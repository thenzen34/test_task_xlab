# Тестовое задание

создаем виртуальное окружение 
```
python3 -m venv venv
```

активируем его
```
source ../venv/bin/activate
```

загружаем зависимости
```
pip3 install -r requirements.txt
```

или посредством баш файла
```
install_requirement.sh
```

создаем настройки для образца берем файл
```
config.py.sample переименовываем в config.py
```

создание таблиц

```
python3 ./make_tables.py
```

пример запуска скрипта для первого задания
```
python3 ./first.py data/4.wav +7918168**91 1 2
```
```
путь к аудио пример "data/4.wav"
номер телефон пример "+7918168**91"
флаг записи в БД 0 или 1
этап 1 или 2
```

вторая часть задания в файле second.sql
