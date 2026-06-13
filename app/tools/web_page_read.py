from typing import Any

async def read_web_page(url: str, max_chars: int ) -> dict[str, Any]:
    """
    让模型，读取url所对应的网页的详细信息
    """