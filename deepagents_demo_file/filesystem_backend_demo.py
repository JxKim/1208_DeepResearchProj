from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

backend = FilesystemBackend(
    root_dir="/home/m1881/pycharm_projects/DeepResearch",
)

agent = create_deep_agent(
    model="openai:gpt-4.1-mini",
    tools=[],
    backend=backend,
    skills=["/agent_skills/"],
)

result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "帮我调研一下新能源汽车行业趋势"}
        ],
    },
    config={
        "configurable": {
            "thread_id": "demo-filesystembackend-skills"
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
            "thread_id": "demo-filesystembackend-skills2"
        }
    },
)