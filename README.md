Для обновления сгенерированных файлов ресурсов и обновления форм, используйте команду
`pyqt5ac -c config.yml`

Для создания exe файла нужно запустить `pyinstaller -w -F --clean app.py`

### Структура проекта
```
|   task11.py       Файл инициализации и первоначальной настройки приложения
|-- ui              Модуль с генерированными файлами из QT Designer и pyuic5
```
MVK