from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

# store: 存储长期记忆，分为不同的命令空间，每个命名空间，可以存储多个Key-Value键值对
store = InMemoryStore()

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

namespace = ("user-123", "agent-files")
namespapce2=  ("user-456","agent-files")

# 先把 skill 文件写入 LangGraph store
# 存储：调用store.put，指定存储在哪个命令空间，key是什么，value是什么
# 存储在("user-123","agent-files")下面，key是/skills/project/web-research/SKILL.md，value是具体的skill的内容
store.put(
    namespace,
    "/skills/project/web-research/SKILL.md",
    {
        "content": skill_md,
        "encoding": "utf-8",
    },
)

backend = StoreBackend(
    store=store,
    namespace=lambda rt: namespace,
)

agent = create_deep_agent(
    model="openai:gpt-4.1-mini",
    tools=[],
    backend=backend,
    store=store,
    skills=["/skills/project/"],
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "帮我调研一下新能源汽车行业趋势，并整理成简短报告",
            }
        ],
    },
    config={
        "configurable": {
            "thread_id": "demo-storebackend-skills"
        }
    },
)

result = store.get(namespace, "/skills/project/web-research/SKILL.md")