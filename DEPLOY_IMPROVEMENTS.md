# Улучшения скрипта деплоя

## 🎯 **Проблема**
Скрипт деплоя не обрабатывал случай, когда база данных отсутствует в папке `/srv/tdp-data/data/`.

## 🔧 **Решение**

### **1. Проверка существования базы данных**
```bash
if [ ! -f "/srv/tdp-data/data/db.sqlite3" ]; then
    echo "📝 База данных не найдена, создаем новую..."
    docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod tdp-web python manage.py migrate --run-syncdb
else
    echo "✅ База данных найдена, применяем миграции..."
    docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod tdp-web python manage.py migrate
fi
```

### **2. Проверка успешности создания**
```bash
if [ -f "/srv/tdp-data/data/db.sqlite3" ] && [ -s "/srv/tdp-data/data/db.sqlite3" ]; then
    echo "✅ База данных создана успешно"
    # Проверка таблиц...
else
    echo "❌ Ошибка: База данных не была создана"
    exit 1
fi
```

### **3. Проверка таблиц в базе данных**
```bash
TABLE_COUNT=$(docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod tdp-web python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
import django
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table';\")
    tables = cursor.fetchall()
    print(len(tables))
" 2>/dev/null || echo "0")
```

## 🚀 **Преимущества**

### **1. Автоматическое создание базы данных**
- Если база данных отсутствует, создается новая
- Используется `--run-syncdb` для создания всех таблиц

### **2. Проверка целостности**
- Проверяется существование файла базы данных
- Проверяется размер файла (не пустой)
- Проверяется количество таблиц

### **3. Информативные сообщения**
- Четкие сообщения о статусе операций
- Рекомендации по созданию суперпользователя
- Ошибки с выходом из скрипта

### **4. Обработка ошибок**
- Скрипт завершается с ошибкой, если база данных не создалась
- Предотвращает запуск с неработающей базой данных

## 📋 **Логика работы**

1. **Проверка существования**: Есть ли файл `/srv/tdp-data/data/db.sqlite3`?
2. **Создание/Обновление**: 
   - Если нет → `migrate --run-syncdb` (создание)
   - Если есть → `migrate` (обновление)
3. **Проверка результата**: Файл создался и не пустой?
4. **Проверка таблиц**: Есть ли таблицы в базе данных?
5. **Рекомендации**: Предложение создать суперпользователя

## ✅ **Итог**

Теперь скрипт деплоя:
- **Автоматически создает** базу данных при первом запуске
- **Проверяет целостность** созданной базы данных
- **Предоставляет рекомендации** по настройке
- **Завершается с ошибкой** при проблемах

Это обеспечивает надежный деплой в любых условиях! 🎉
