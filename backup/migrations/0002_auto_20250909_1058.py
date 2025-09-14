# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestoreTask',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('filename', models.CharField(max_length=255, verbose_name='Имя файла')),
                ('file_size', models.BigIntegerField(verbose_name='Размер файла (байт)')),
                ('status', models.CharField(choices=[('pending', 'Ожидает'), ('processing', 'Обрабатывается'), ('completed', 'Завершено'), ('failed', 'Ошибка'), ('cancelled', 'Отменено')], default='pending', max_length=20, verbose_name='Статус')),
                ('progress', models.IntegerField(default=0, verbose_name='Прогресс (%)')),
                ('message', models.TextField(blank=True, verbose_name='Сообщение')),
                ('error_details', models.TextField(blank=True, verbose_name='Детали ошибки')),
                ('imported_categories', models.IntegerField(default=0, verbose_name='Импортировано категорий')),
                ('imported_tags', models.IntegerField(default=0, verbose_name='Импортировано тегов')),
                ('imported_tours', models.IntegerField(default=0, verbose_name='Импортировано туров')),
                ('imported_services', models.IntegerField(default=0, verbose_name='Импортировано услуг')),
                ('imported_reviews', models.IntegerField(default=0, verbose_name='Импортировано отзывов')),
                ('imported_news', models.IntegerField(default=0, verbose_name='Импортировано новостей')),
                ('imported_blog', models.IntegerField(default=0, verbose_name='Импортировано статей')),
                ('imported_prices', models.IntegerField(default=0, verbose_name='Импортировано прайсов')),
                ('imported_files', models.IntegerField(default=0, verbose_name='Импортировано файлов')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Начато')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Завершено')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Задача восстановления',
                'verbose_name_plural': 'Задачи восстановления',
                'ordering': ['-created_at'],
            },
        ),
    ]
