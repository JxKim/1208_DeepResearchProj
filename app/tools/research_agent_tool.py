

async def save_research_sections(project_id:str, section) -> dict:
    """
    让模型调用，将section保存到MongoDB当中，并且返回是否保存成功，或失败（失败的原因是模型要保存的section，缺少数据，或者是结构不对）
    """