from app.repository.mongodb import get_database
from app.config.config import get_setting
from app.tools.storage_tool import save_report_html_to_file, read_report_html_from_file
from datetime import datetime
from uuid import uuid4

async def save_html_result(html_result:dict,project_id):
    """
    1、会调用storage_tool：把这个html_result，存储到 对象存储服务当中 / 文件系统里面，返回html_url
    2、存储在mongo当中的就是一个html_uri

    3、接口读取html的时候，先从mongo获取到html_uri，然后再通过对象存储服务/文件系统，读取到整个html的正文，
    """
    report_id = str(uuid4())
    setting = get_setting()
    report : dict | None=  await get_database()[setting.research_report_collection_name].find_one(
        {"project_id":project_id},
        sort = [("version", -1)]

    )
    html_uri = await save_report_html_to_file(html=html_result["html"])
    next_version =report["version"]+1 if report else 1

    report_version = {
        "_id":report_id,
        "project_id":project_id,
        "version":next_version,
        "title":html_result["title"],
        "html_uri": html_uri,
        "sources":html_result["sources"],
        "created_at": datetime.now()
    }

    await get_database()[setting.research_report_collection_name].insert_one(report_version)


async def get_latest_report(project_id:str) -> dict | None:
    """
    获取项目最新报告
    """
    setting = get_setting()
    report = await get_database()[setting.research_report_collection_name].find_one(
        {"project_id":project_id},
        sort=[("version", -1)]
    )
    if report is None:
        return None
    report["html"] = await read_report_html_from_file(report["html_uri"])
    return report
