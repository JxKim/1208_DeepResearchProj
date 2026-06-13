from shutil import ExecError
from deepagents.backends.utils import create_file_data
from deepagents import create_deep_agent
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import InMemorySaver
from pathlib import Path
from app.config.config import get_setting
from app.tools import external_search, ragflow_search, web_page_read
from app.tools.research_agent_tool import save_research_sections
from app.schema import ResearchCreateRequest
import app.repository.research_project_repository as project_repo
import json
class ResearchAgent:

    def __init__(self,manager_agent):
        self.manager_agent:CompiledStateGraph = manager_agent



    async def generate_outline(self,project_id,research_project:ResearchCreateRequest,task_id)->dict:
        """
        生成outline，outline当中包含outline和research_brief
        """
        # result返回的是当前langgraph的所有的state所组成的dict
        result:dict = await self.manager_agent.ainvoke(
            {
                "messages":[
                    {"role":"user","content":f"请基于以下的设定:{research_project.model_dump()}，来完成大纲的生成"}
                ]
            },
            config={"configurable":{"thread_id":f'{project_id}_{task_id}'}}
        )
        ai_message:str = result["messages"][-1].content
        try:
            final_result = json.loads(ai_message)
        except Exception as e:
            # 最好进行一下检测，当json.loads报错时，可以使用固定模板大纲，或者是让agent进行重试
            # 或者，将大纲生成，也封装成一个工具，让模型进行调用，这种方案，如果模型生成大纲有问题的话，可以通过ToolMessage，告知给模型，模型可以进行修改。
            final_result = {}

        return final_result 

    async def revise_outline(self,project_id,research_project,revision_instruction,task_id) -> dict:
        """
        修订大纲，outline当中包含outline和research_brief
        1、将修订大纲的任务，写到文件系统当中去，让模型去读取这个文件，去进行修订
        2、修订大纲，我们给模型的上下文，不需要生成大纲时的上下文，只需要从数据库读取当前的大纲，让模型基于当前的大纲，进行修改
        """
        # 1、读取当前项目的大纲
        outline :dict | None =  await project_repo.get_outline(project_id)
        revise_outline_dict = {
            "task":"revise_outline",
            "project_id":project_id,
            "outline":outline,
            "research_project":research_project,
            "revision_instruction":revision_instruction
        }
        # 2、调用manager_agent，进行大纲修订任务
        result:dict = await self.manager_agent.ainvoke(
            {
                "messages":[
                    {"role":"user","content":f"请完成文件：/revise_outline.json 当中所描述的任务"}
                ],
                "files":{
                    "/revis_outline.json":create_file_data(json.dumps(revise_outline_dict))
                }
            },
            config={"configurable":{"thread_id":f'{project_id}_{task_id}'}}
        )

        ai_message:str = result["messages"][-1].content
        try:
            final_result = json.loads(ai_message)
        except Exception as e:
            # 最好进行一下检测，当json.loads报错时，可以使用固定模板大纲，或者是让agent进行重试
            # 或者，将大纲生成，也封装成一个工具，让模型进行调用，这种方案，如果模型生成大纲有问题的话，可以通过ToolMessage，告知给模型，模型可以进行修改。
            final_result = {}

        return final_result 

    async def generate_research_result(self,project_id,user_instruction,task_id):
        """
        调用大模型，大模型内部通过结构化的方式，去调用save_research_sections
        生成报告：
        1、从数据库当中，找到当前project所对应的大纲
        2、将大纲以文件的方式，给到模型，让模型进行生成

        假设大纲有20个章节，manager.invoke的方式，调用agent,假设它给你返回结果了，
        可以让整个生成的过程，最多重试5次：
            每一次重试之前，我们从数据库当中查找大纲，假设大纲有m个章节，此时数据库当中的sections有n个章节，
            如果sections当中的章节数量和大纲当中的一致，我们就直接退出
            否则，就重试，就让模型生成 set(m)-set(n) 这些章节，也就是让模型生成缺失的章节
        """
        setting = get_setting()
        total_retry_times = setting.total_retry_times
        outline:dict | None = await project_repo.get_confirmed_outline(project_id)
        generate_research_result={
            "task":"generate_research_result",
            "outline":outline,
            "user_instruction":user_instruction
        }

        await self.manager_agent.ainvoke(
            {
                "messages":[
                    {"role":"user","content":f"请完成以下文件 /generate_research_result.json, 当中的任务"}
                ],
                "files":{
                    "/generate_research_result.json":create_file_data(json.dumps(generate_research_result))
                }
            },
            config={"configurable":{"thread_id":f'{project_id}_{task_id}_intial_generate'}}
        )


        save_sections_ids:list[str]= await project_repo.get_saved_sections(project_id)
        expected_section_ids:list[str] =  await project_repo.get_expected_section_ids(project_id)
        missing = set(expected_section_ids)  - set(save_sections_ids)
        if missing:
            # 让agent继续补齐，未完成的章节
            for retry_count in range(total_retry_times):
                    saved_sections: list[dict]  = await project_repo.get_saved_sections_detail(project_id)
                    generate_research_result={
                        "task":"generate_research_result",
                        "outline":outline,
                        "user_instruction":user_instruction,
                        "saved_sections": saved_sections,
                        "missing_sections": missing
                    }
                    await self.manager_agent.ainvoke(
                    {
                        "messages":[
                            {"role":"user","content":f"请完成以下文件 /generate_research_result.json, 当中的任务"}
                        ],
                        "files":{
                            "/generate_research_result.json":create_file_data(json.dumps(generate_research_result))
                        }
                    },
                    config={"configurable":{"thread_id":f'{project_id}_{task_id}_retry_{retry_count}'}}
                    )
                    save_sections_ids:list[str]= await project_repo.get_saved_sections(project_id)
                    expected_section_ids:list[str] =  await project_repo.get_expected_section_ids(project_id)
                    missing = set(expected_section_ids)  - set(save_sections_ids)
                    if not missing:
                        break



                
                




_research_agent = None

def get_research_agent():

    global _research_agent
    if _research_agent is None:
        setting = get_setting()
        information_search_agent = {
            "name":"information_search",
            "description":"负责公开互联网检索、网页读取、RAGFlow 内部知识库检索和证据整理。",
            "system_prompt":_load_prompt(Path(__file__).parent / "prompts" / "search_agent.md"),
            "tools":[external_search, ragflow_search, web_page_read],
            "model":f'{setting.llm_provider}:{setting.llm_model_name}'
        }
        manager_agent = create_deep_agent(
            # deepseek:deepseek-chat openai:gpt-4o-mini
            model=f'{setting.llm_provider}:{setting.llm_model_name}',
            system_prompt=_load_prompt(Path(__file__).parent / "prompts" / "research_manager.md"),
            tools=[save_research_sections],
            subagents=[information_search_agent],
            checkpointer=InMemorySaver(),

        )
        _research_agent = ResearchAgent(manager_agent=manager_agent)
    
    return _research_agent

def _load_prompt(path:Path):
    """
    读取path下面的prompt，返回文本
    """
    return path.read_text(encoding="utf-8")