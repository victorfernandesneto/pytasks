import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio


load_dotenv()

def notify_task(instance_pk):
    from tasks.models import Task
    instance = Task.objects.get(pk=instance_pk)
    if not instance.finished:
        asyncio.run(send_notification(instance))


async def send_notification(task):
    if not task.finished:
        message = f"Task '{task.task_name}' is due in 1 hour! Deadline: {task.deadline}"
            
        bot = Bot(os.getenv('BOT_TOKEN'))
        chat_id = task.user
        await bot.send_message(chat_id=chat_id, text=message)
