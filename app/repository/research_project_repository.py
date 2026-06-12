from app.repository.mongodb import get_database
from app.config.config import get_setting
from app.schema import ResearchCreateRequest,ProjectStatusEnum
from uuid import uuid4
import datetime
async def create_project(research_create_request:ResearchCreateRequest) -> str:
    """
    创建项目
    """

    project_id = str(uuid4())
    project_document  = {
        "_id": project_id,
        "project_id":project_id,
        "topic": research_create_request.topic,
        "status":ProjectStatusEnum.CREATED.value,
        "request":research_create_request.model_dump(),
        "created_at":datetime.datetime.now(),
        "updated_at":datetime.datetime.now()
    }

    await get_database()[get_setting().research_project_collection_name].insert_one(project_document)
    return project_id


async def save_outline(outline,project_id):
    """
    对大纲和任务书进行保存：
    outline: 一个Dict，里面包含了大纲和任务书
    """

    await get_database()[get_setting().research_project_collection_name].update_one(
        {"_id":project_id},

        {"$set":
         {
             "outline": outline["outline"],
             "research_brief": outline["research_brief"]
         }
         }
    )

async def update_status(project_id, status:str):
    await get_database()[get_setting().research_project_collection_name].update_one(
        {"_id":project_id},

        {"$set":
         {
             "status": status,
         }
         }
    )

async def get_research_result(project_id):
    """
    根据project_id查找文档，返回当前project的research_result
    """
    # select col_a, col_b, col_c from xxx_table; 
    result = await get_database()[get_setting().research_project_collection_name].find_one(
        {"_id":project_id},
        projection = {"research_result":1}
    )
    return result


async def get_project(project_id) -> dict | None:

    result:dict  | None = await get_database()[get_setting().research_project_collection_name].find_one(
        {"_id":project_id},
    )
    return result