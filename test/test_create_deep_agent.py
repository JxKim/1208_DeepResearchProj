from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data
system_prompt="你是一个智能助手"

agent = create_deep_agent(model="deepseek:deepseek-chat",system_prompt="你是一个智能助手")
result = agent.invoke({
    "messages":
    [{"role":"user","content":"什么是langchain"}],
    
    "files":
    {
        "/my.txt":create_file_data("xxx")
        }
        
        },
    )
print(result)