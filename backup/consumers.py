import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import RestoreTask


class RestoreProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.room_group_name = f'restore_{self.task_id}'

        # Проверяем, что пользователь имеет доступ к этой задаче
        if not await self.check_task_access():
            await self.close()
            return

        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Отправляем текущий статус
        await self.send_current_status()

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Отправляем сообщение в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'restore_message',
                'message': message
            }
        )

    async def restore_message(self, event):
        message = event['message']

        # Отправляем сообщение WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def restore_progress(self, event):
        # Отправляем обновление прогресса
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            'progress': event['progress'],
            'message': event['message'],
            'status': event['status']
        }))

    @database_sync_to_async
    def check_task_access(self):
        """Проверяем, что пользователь имеет доступ к задаче"""
        try:
            task = RestoreTask.objects.get(id=self.task_id)
            return task.user == self.scope['user']
        except RestoreTask.DoesNotExist:
            return False

    @database_sync_to_async
    def get_task_status(self):
        """Получаем текущий статус задачи"""
        try:
            task = RestoreTask.objects.get(id=self.task_id)
            return {
                'status': task.status,
                'progress': task.progress,
                'message': task.message,
                'imported': {
                    'categories': task.imported_categories,
                    'tags': task.imported_tags,
                    'tours': task.imported_tours,
                    'services': task.imported_services,
                    'reviews': task.imported_reviews,
                    'news': task.imported_news,
                    'blog': task.imported_blog,
                    'prices': task.imported_prices,
                    'files': task.imported_files,
                }
            }
        except RestoreTask.DoesNotExist:
            return None

    async def send_current_status(self):
        """Отправляем текущий статус задачи"""
        status = await self.get_task_status()
        if status:
            await self.send(text_data=json.dumps({
                'type': 'status_update',
                'status': status['status'],
                'progress': status['progress'],
                'message': status['message'],
                'imported': status['imported']
            }))
