# Backup and Restore

This project exposes admin endpoints to dump and restore the database together with uploaded media.

## Creating a backup

1. Start the project and sign in as a staff user or superuser.
2. Download the archive from the backup endpoint:

```bash
curl -L -o TDP_$(date +%Y%m%d).zip -H "Cookie: sessionid=<SESSION_ID>" http://localhost:8000/backup/download/
```

The command saves a file named `TDP_YYYYMMDD.zip` with JSON dumps under `data/` and media files under `media/`.

Example `zipinfo` output:

```
Archive:  TDP_20240601.zip
  inflating: data/categories.json
  inflating: media/example.jpg
```

## Restoring from a backup

> ⚠️ Restoring replaces existing records and media files with the contents of the archive. Ensure you have a fresh backup before running it.

Upload the archive to the restore endpoint:

```bash
curl -L -H "Cookie: sessionid=<SESSION_ID>" -F "archive=@TDP_20240601.zip" http://localhost:8000/backup/restore/
```

Expected server message on success:

```
Импортировано: 12 категорий, 34 тегов, 7 туров, 5 сервисов, 2 новостей, 1 статей; файлов медиа: 20
```

Run the restore only on a clean database or when you intend to completely overwrite the current data.
