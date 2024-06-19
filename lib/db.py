# db.py
import aiomysql
import json
from config import env, db

db_config = db()
db_table = f"{env('DB_PREFIX')}{env('TASKS_TABLE')}"
db_table_response = f"{env('DB_PREFIX')}{env('TASKS_TABLE_RESPONSE')}"


async def get_connection_pool():
    return await aiomysql.create_pool(**db_config)


async def create_task(task_data):
    pool = await get_connection_pool()
    task_data['header'] = {} if task_data.get('header') is None else task_data['header']
    task_data['times'] = 0 if task_data.get('times') is None else task_data['times']
    task_data['callback_url'] = '' if task_data.get('callback_url') is None else task_data['callback_url']

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO api_tasks (target_url, method, post_body, header, frequency, times, callback_url, status, data_array)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                task_data['target_url'],
                task_data['method'],
                json.dumps(task_data['post_body']),
                json.dumps(task_data['header']),
                task_data['frequency'],
                task_data['times'],
                task_data['callback_url'],
                'waiting',
                json.dumps(task_data['arrData'])
            ))
            task_id = cur.lastrowid
            await conn.commit()
    pool.close()
    return task_id


async def update_task_status(task_id, status, last_result=None, error_message=None, completed_at=None):
    pool = await get_connection_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"""
                UPDATE {db_table}
                SET status = %s, last_result = %s, error_message = %s, completed_at = %s
                WHERE id = %s
            """, (status, last_result, error_message, completed_at, task_id))
            await conn.commit()
    pool.close()


async def increment_times_completed(task_id):
    pool = await get_connection_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"UPDATE {db_table} SET times_completed = times_completed + 1 WHERE id = %s", (task_id,))
            await conn.commit()
    pool.close()


async def get_task_data(task_id):
    pool = await get_connection_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT target_url, method, post_body, header, frequency, times, callback_url, status, data_array FROM {db_table} WHERE id = %s",
                (task_id,))
            result = await cur.fetchone()
    pool.close()
    if result:
        return {
            'target_url': result[0],
            'method': result[1],
            'post_body': json.loads(result[2]) if result[2] else None,
            'header': json.loads(result[3]) if result[3] else None,
            'frequency': result[4],
            'times': result[5],
            'callback_url': result[6],
            'status': result[7],
            'arrData': json.loads(result[8]) if result[8] else []
        }
    return None


async def save_response_data(task_id: int, response_data: str):
    pool = await get_connection_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"INSERT INTO {db_table_response} (task_id, response_data) VALUES (%s, %s)",
                              (task_id, response_data))
            await conn.commit()
    pool.close()


async def get_all_stocks():
    pool = await get_connection_pool()
    stock_ids = []
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT stock_id FROM ba_stocks")
                result = await cur.fetchall()
                for row in result:
                    stock_ids.append(row[0])
    finally:
        # 确保连接池被释放，不需要手动关闭pool
        pass
    return stock_ids
