"""
定义路由函数
"""
from fastapi import FastAPI, HTTPException,status,APIRouter
from app.schema import (
    OutlineNode,
    ResearchCreateRequest,
    ResearchCreateResponse,
    GetOutlineResponse,
    SaveOutlineRequest,
    SaveOutlineResponse,
    GenerateReportRequest,
    GenerateReportResponse,
    GetTaskStatusResponse,
    GetReportResponse,
    Source,
    TaskStatusEnum,
    TaskTypeEnum,
    ProjectStatusEnum,
    NextStepEnum
)
from app.repository import research_project_repository as project_repo
from app.repository import research_task_repository as task_repository
from app.repository import report_repository
from app.background.research_tasks import start_outline_generation,start_outline_revision,start_report_generate
from uuid import uuid4
from datetime import datetime

router = APIRouter()

def convert_outline_dict_2_outline_node(outline:dict)->OutlineNode:

    outline_node = OutlineNode(
        node_id=outline["node_id"],
            title=outline["title"],
            question=outline["question"],
            description=outline["description"],
            children=[convert_outline_dict_2_outline_node(chile_node) for chile_node in outline["children"]] 
    )

    return outline_node

def build_source_from_report_source(source):

    return Source(
        source_id=source["source_id"],
        title=source["title"],
        url = source["url"],
        published_at=source["published_at"],
        source_type=source["source_type"]
    )


@router.post("/research-projects",response_model=ResearchCreateResponse)
async def create_project(research_create_request: ResearchCreateRequest):
    """
    创建项目路由函数
    """
    # 1、创建一个空项目，通过project_repository，将项目的元数据信息，写到数据库
    project_id = await project_repo.create_project(research_create_request)
    # 2、创建一个生成 研究任务书和大纲 的任务，通过后台去启动这个任务
    # 2.1、通过task_repository，在数据库中，写入任务元数据信息
    task_id =  await task_repository.create_task(project_id=project_id,task_type = TaskTypeEnum.OUTLINE_GENERATION.value)
    await project_repo.update_status(project_id,status = ProjectStatusEnum.BRIEF_GENERATING.value)
    # 2.2、后台运行任务
    start_outline_generation(research_project = research_create_request, task_id = task_id,project_id=project_id)

    # 处理逻辑

    return ResearchCreateResponse(
        project_id=project_id,
        initial_task_id=task_id,
        initial_task_type=TaskTypeEnum.OUTLINE_GENERATION.value,
        topic=research_create_request.topic,
        status=ProjectStatusEnum.BRIEF_GENERATING.value,
        next_step=NextStepEnum.WAIT_FOR_OUTLINE.value,
        created_at=datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
    )



# | `/api/v1/research-projects/{project_id}/outline`        | `GET`  | 获取大纲草案        |
@router.get("/research-projects/{project_id}/outline",response_model=GetOutlineResponse)
async def get_outline(project_id: str):
    """
    获取大纲草案：
    project_id去查询数据库
    
    """
    # 1、从数据库中读取到project_id所对应的项目
    project:dict | None= await project_repo.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404,detail="当前项目不存在")
    
    outlines = project["outlines"]
    # 2、将这个项目，转换成GetOutlineResponse
    return GetOutlineResponse(
        project_id=project_id,
        status=project["status"],
        outline=[convert_outline_dict_2_outline_node(outline) for outline in outlines]
    )

    


# | `/api/v1/research-projects/{project_id}/outline`        | `PUT`  | 确认大纲或提交大纲修改意见 |
@router.put("/research-projects/{project_id}/outline",response_model=SaveOutlineResponse)
async def save_outline(project_id: str, request: SaveOutlineRequest):
    """确认大纲或提交大纲修改意见"""
    # 1、获取到用户的操作
    action = request.action
    project = await project_repo.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404,detail="当前项目不存在")
    if action == "confirm":
        # 1、修改项目状态，将项目状态调整成  outline_confirmed
        await project_repo.update_status(project_id,status = ProjectStatusEnum.OUTLINE_CONFIRMED.value)
        # 2、返回结果
        return SaveOutlineResponse(
            project_id=project_id,
            status=ProjectStatusEnum.OUTLINE_CONFIRMED.value,
            next_step=NextStepEnum.GENERATE_REPORT.value
        )
    elif action == "revise":
        # 1、生成一个task
        task_id = await task_repository.create_task(project_id = project_id,task_type = TaskTypeEnum.OUTLINE_REVISION.value)
        # 2、更新项目状态为大纲调整中
        await project_repo.update_status(project_id,status = ProjectStatusEnum.OUTLINE_REVISING.value)
        # 3、后台调度task
        start_outline_revision(research_project =project , task_id = task_id,project_id=project_id,revision_instruction=request.revision_instruction)
        # 3、返给用户新的task id
        return SaveOutlineResponse(
            project_id=project_id,
            status=TaskStatusEnum.QUEUED.value,
            revision_task_id=task_id,
            next_step=NextStepEnum.WAIT_FOR_OUTLINE.value
        )


# | `/api/v1/research-projects/{project_id}/report-tasks`   | `POST` | 提交报告生成任务      |
@router.post("/research-projects/{project_id}/report-tasks")
async def create_report_task(project_id: str, request: GenerateReportRequest):
    """提交报告生成任务"""
    # 1、检查项目是否存在
    project:dict | None= await project_repo.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="没有当前项目")
    # 2、创建一个后台任务
    task_id = await task_repository.create_task(project_id = project_id,task_type = TaskTypeEnum.REPORT_GENERATION.value) 
    await project_repo.update_status(project_id=project_id,status = ProjectStatusEnum.RESEARCH_RUNNING.value)
    start_report_generate(task_id,project_id,request.user_instruction)
    return GenerateReportResponse(task_id=task_id,project_id=project_id,task_type=TaskTypeEnum.REPORT_GENERATION.value,status=TaskStatusEnum.QUEUED.value)


# | `/api/v1/tasks/{task_id}`                               | `GET`  | 查询后台任务状态      |
@router.get("/tasks/{task_id}",response_model=GetTaskStatusResponse)
async def get_task_status(task_id: str,):
    """查询后台任务状态"""
    task:dict = await task_repository.get_task(task_id)
    return GetTaskStatusResponse(
        task_id=task["id"],
        project_id=task["project_id"],
        task_type= task["task_type"],
        status=task["status"],
        message=task["message"],
        created_at=task["created_at"],
        updated_at=task["updated_at"]
    )


# | `/api/v1/research-projects/{project_id}/reports/latest` | `GET`  | 获取最新报告        |
@router.get("/research-projects/{project_id}/reports/latest")
async def get_latest_report(project_id: str):
    """获取最新报告"""
    project:dict | None = await project_repo.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="没有当前项目")
    latest_report :dict =await report_repository.get_latest_report(project_id)
    return GetReportResponse(
        project_id=project_id,
        report_id=latest_report["report_id"],
        version=latest_report["version"],
        title=latest_report["title"],
        html=latest_report["html"],
        sources=[build_source_from_report_source(source) for source in latest_report["sources"]],
        created_at=latest_report["created_at"]
    )
    
