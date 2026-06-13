


from pathlib import Path


async def save_report_html_to_file(html:str) -> str:
    """
    把一个html保存到对象存储，或者是文件系统中，返回地址 uri信息
    """

    raise NotImplementedError("save_report_html_to_file 尚未实现")


async def read_report_html_from_file(html_uri:str) -> str:
    """
    根据html_uri读取报告正文
    """
    return Path(html_uri).read_text(encoding="utf-8")
