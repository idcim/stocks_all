# tasks.py
import aiohttp
import asyncio
from datetime import datetime
from .db import create_task, update_task_status, increment_times_completed, get_task_data, save_response_data


async def send_request(task_data, task_id, stock_id):
    url = task_data['target_url']
    method = task_data['method']
    post_body = task_data['post_body'].copy() if task_data['post_body'] else {}
    headers = task_data['header'] if task_data['header'] else {}

    # 替换 post_body 中的 StockID
    post_body['StockID'] = stock_id

    async with aiohttp.ClientSession() as session:
        try:
            if method.lower() == 'post':
                async with session.post(url, data=post_body, headers=headers) as response:
                    response_text = await response.text()
            else:
                async with session.get(url, headers=headers) as response:
                    response_text = await response.text()

            # 保存响应数据到数据库
            await save_response_data(task_id, response_text)

            await update_task_status(task_id, 'success', response_text)
            await increment_times_completed(task_id)
        except Exception as e:
            error_message = str(e)
            await update_task_status(task_id, 'error', error_message=error_message)


async def trigger_task(task_id: int, task_data: dict):
    if not task_data:
        return {"message": "Task not found"}

    status = task_data['status']

    if status == 'completed':
        return {"message": "Task has already been completed"}
    elif status == 'waiting':
        await update_task_status(task_id, "running")
        times = task_data['times']
        data_array = task_data['arrData']
        frequency = task_data.get('frequency', 10)  # 每秒发送请求数，默认10个

        tasks = []
        for i, stock_id in enumerate(data_array):
            tasks.append(send_request(task_data, task_id, stock_id))
            if (i + 1) % frequency == 0:
                await asyncio.gather(*tasks)
                tasks = []
                await asyncio.sleep(1)

        if tasks:
            await asyncio.gather(*tasks)

        await update_task_status(task_id, 'completed', completed_at=datetime.now())

    return {"message": "Task completed", "task_id": task_id}


async def execute_task(task_id):
    task_data = await get_task_data(task_id)

    if not task_data:
        return {"message": "Task not found"}

    status = task_data.get('status')

    if not status:
        return {"message": "Invalid task data"}

    if status == 'running':
        return {"message": "Task is already running"}

    await update_task_status(task_id, 'running')
    result = await trigger_task(task_id, task_data)
    return result
