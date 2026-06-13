

async def external_search(
            query: str,
    max_results: int = 5,
    search_depth: str = "basic",
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    time_range: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
)->dict:
    """
    让agent进行外部搜索的工具
    """
