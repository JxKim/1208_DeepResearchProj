from app.repository.mongodb import get_database
from app.config.config import get_setting
from app.schema import TaskStatusEnum
from datetime import datetime
from uuid import uuid4
async def create_task(project_id:str, task_type:str) -> str:
    """
    创建任务，在数据库中插入任务的元数据信息
    """
    setting = get_setting()
    task_id = str(uuid4())
    task = {
        "_id":task_id,
        "project_id":project_id,
        "task_type":task_type,
        "status": TaskStatusEnum.QUEUED.value,
        "message":"任务已创建",
        "created_at":datetime.now(),
        "updated_at": datetime.now()
    }
    await get_database()[setting.research_task_collection_name].insert_one(task)

    return task_id



async def update_status(task_id:str,task_status:TaskStatusEnum):
    """
    修改任务状态
    """
    setting = get_setting()
    
    await get_database()[setting.research_task_collection_name].update_one(
        {"_id":task_id},
        {
            "$set":{
                "status":task_status.value,
                "updated_at": datetime.now()
            }
         }
    )


async def get_task(task_id:str) -> dict | None:
    """
    根据任务id查询任务状态
    """
    setting = get_setting()
    return await get_database()[setting.research_task_collection_name].find_one(
        {"_id":task_id}
    )
