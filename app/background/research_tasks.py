import asyncio
from app.repository import research_task_repository as task_repo
from app.repository import research_project_repository as project_repo
from app.repository import report_repository as report_repo
from app.schema import TaskStatusEnum,ProjectStatusEnum
from app.agents.research_agent import get_research_agent
from app.tools.render_html import write_html
def start_outline_generation(research_project , task_id ,project_id):
    """
    启动 大纲生成的后台任务
    """
    task_coroutine  = _start_outline_generation(research_project , task_id ,project_id)
    asyncio.create_task(task_coroutine)
    print(f"task_id:{task_id},project_id:{project_id}:异步任务已提交")

    
def start_outline_revision(research_project  , task_id ,project_id, revision_instruction):

    task_coroutine  = _start_outline_revision(research_project , task_id ,project_id,revision_instruction)
    asyncio.create_task(task_coroutine)
    print(f"task_id:{task_id},project_id:{project_id}:异步任务已提交")

def start_report_generate(task_id:str,project_id:str,user_instruction:str):
    
    task_coroutine  = _start_report_generate(task_id, project_id,user_instruction)
    asyncio.create_task(task_coroutine)
    print(f"task_id:{task_id},project_id:{project_id}:异步任务已提交")
    


async def _start_outline_generation(research_project , task_id ,project_id):
    """
    真正的 大纲生成 协程 需要做的事情
    """

    # 1、修改task_id所对应的任务的状态：queued - > running
    # 2、调用agent，生成大纲
    # 3、把大纲保存到数据库中
    # 4、把项目状态状态调整为：OUTLINE_READY
    # 5、把任务状态改成成功 / 把任务状态改成失败

    try:

        await task_repo.update_status(task_id=task_id,task_status=TaskStatusEnum.RUNNING)
        research_agent = get_research_agent()
        outline:dict = await research_agent.generate_outline(project_id=project_id,research_project=research_project)

        await project_repo.save_outline(outline,project_id)

        await project_repo.update_status(project_id, status=ProjectStatusEnum.OUTLINE_READY.value)
        await task_repo.update_status(task_id=task_id,task_status=TaskStatusEnum.SUCCEEDED)

    except Exception as e:
        # 出了异常，应该如何处理？
        await task_repo.update_status(task_id=task_id,task_status=TaskStatusEnum.FAILED)
        print(f"当前任务:{task_id} 出现异常,异常信息：{str(e)}")
        

async def _start_outline_revision(research_project , task_id ,project_id,revision_instruction):
    """
    大纲修订的协程函数
    """
    # 1、修改task_id所对应的任务的状态：queued - > running
    # 2、调用agent，修订大纲
    # 3、把大纲保存到数据库中
    # 4、把项目状态状态调整为：OUTLINE_READY
    # 5、把任务状态改成成功 / 把任务状态改成失败

    try:

        await task_repo.update_status(task_id=task_id,task_status=TaskStatusEnum.RUNNING)
        research_agent = get_research_agent()
        outline = await research_agent.revise_outline(project_id=project_id,research_project=research_project,revision_instruction=revision_instruction)

        await project_repo.save_outline(outline,project_id)

        await project_repo.update_status(project_id, status=ProjectStatusEnum.OUTLINE_READY.value)
        await task_repo.update_status(task_id=task_id,task_status=TaskStatusEnum.SUCCEEDED)

    except Exception as e:
        # 出了异常，应该如何处理？
        await task_repo.update_status(task_id=task_id,task_status=TaskStatusEnum.FAILED)
        print(f"当前任务:{task_id} 出现异常,异常信息：{str(e)}")
    

async def _start_report_generate(task_id, project_id,user_instruction):
    """
    进行研究，保存报告的协程
    """

    # 1、修改task_id所对应的任务的状态：queued - > running
    # 2、调用agent，生成 结构化的研究结果：research_result
    # 3、使用tool将research_result 渲染成html的结构
    # 4、使用report_repository，将Html结果，保存到数据库当中去
    # 5、把项目状态状态调整为：REPORT_READY
    # 6、把任务状态改成成功 / 把任务状态改成失败

    try:

        await task_repo.update_status(task_id=task_id,task_status=TaskStatusEnum.RUNNING)
        research_agent = get_research_agent()
        # 可以在generate_research_result当中，通过project_id读取到大纲，让agent基于大纲和user_instruction去生成报告
        # 此处可以让大模型通过function call的形式，去构建各个章节的大纲
        await research_agent.generate_research_result(project_id=project_id,user_instruction=user_instruction)

        research_result = await project_repo.get_research_result(project_id)
        # 通过write_html工具，将research_result渲染成一个html的结果
        html_result = write_html(research_result)
        # 将结果，写入到数据库，以及文件系统/对象存储当中去
        await report_repo.save_html_result(html_result,project_id)

        await project_repo.update_status(project_id, status=ProjectStatusEnum.REPORT_READY.value)
        await task_repo.update_status(task_id=task_id,task_status=TaskStatusEnum.SUCCEEDED)

    except Exception as e:
        # 出了异常，应该如何处理？
        await task_repo.update_status(task_id=task_id,task_status=TaskStatusEnum.FAILED)
        print(f"当前任务:{task_id} 出现异常,异常信息：{str(e)}")
