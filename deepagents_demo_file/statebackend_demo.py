from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data

agent = create_deep_agent(
    model="openai:gpt-4.1-mini",
    tools=[],
    skills=["/skills/project/"],
)
# 渐进式披露 
skill_md = """---
name: web-research
description: 用于公开资料检索、来源整理和结论归纳
---

# Web Research

当用户要求调研某个主题时：
1. 明确问题范围
2. 收集来源
3. 整理关键事实
4. 输出带来源的总结
"""
my_text=  "xxxxxxx"
result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "帮我读取/my.txt, 回答我里面有什么"}
        ],
        "files": {
            "/my.txt": create_file_data(my_text),
        },
    },
    config={
        "configurable": {
            "thread_id": "demo-statebackend-skills"
        }
    },
)


result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "帮我调研一下新能源汽车行业趋势"}
        ],
        
    },
    config={
        "configurable": {
            "thread_id": "demo-statebackend-skills2"
        }
    },
)