from fastapi import FastAPI, HTTPException, BackgroundTasks
from datetime import datetime
from lib.tasks import trigger_task, execute_task
from lib.db import get_task_data, create_task, get_all_stocks
from lib.tools import req
from models import TaskId, TaskData
from config import env

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Task manager is running"}


# 创建任务
@app.post("/create_task", response_model=TaskId)
async def create_task_handler(task_data: TaskData):
    task_id = await create_task(task_data.dict())
    return {"task_id": task_id}


# 执行任务
@app.post("/trigger_task/{task_id}")
async def trigger_task_handler(task_id: int):
    result = await execute_task(task_id)
    if result.get("message") == "Task not found":
        raise HTTPException(status_code=404, detail="Task not found")
    elif result.get("message") == "Task is already running":
        raise HTTPException(status_code=400, detail="Task is already running")
    return result


# 定制任务:全频STOCKS日数据
@app.get("/stocks_daily")
async def stocks_get(background_tasks: BackgroundTasks):
    # 添加交易日判断
    trade_day = req(f"http://api.mairui.club/hszbl/fsjy/000001/dh/{env('MR_TOKEN')}")
    day = trade_day[-1]['d']
    today = datetime.now().strftime('%Y-%m-%d')
    if today != day:
        return HTTPException(status_code=400, detail="This day is not a trade day!")

    arr_data = await get_all_stocks()

    # 创建任务
    task = {
        "target_url": "https://apphwhq.longhuvip.com/w1/api/index.php",
        "method": "POST",
        "post_body": {
            "a": "GetStockPanKou_Narrow",
            "c": "StockL2Data",
            "StockID": "{#arrData}",
            "State": "1"
        },
        "frequency": 5,
        "callback_url": "",
        "arrData": arr_data
    }

    task_id = await create_task(task)

    if isinstance(task_id, (int, float)):
        # 将任务添加到后台任务中
        background_tasks.add_task(execute_task, task_id)
        return {"task_id": task_id}
    else:
        return {"task_id": task_id, 'msg': '任务创建失败'}


# 任务状态查询
@app.get("/task_status/{task_id}")
async def get_task_status_handler(task_id: int):
    task_data = await get_task_data(task_id)
    if task_data:
        status = task_data['status']
        return {"task_id": task_id, "status": status}
    else:
        raise HTTPException(status_code=404, detail="Task not found")
