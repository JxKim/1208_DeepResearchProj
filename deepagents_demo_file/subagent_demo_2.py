"""
可以作为子agent，传给主智能体的两个条件：

1、它是一个langgraph的可调用的图对象
2、这个可调用的图对象当中的状态当中有messages这个状态键

"""

from deepagents import create_deep_agent, CompiledSubAgent
from langchain.agents import create_agent
from langgraph.graph import StateGraph

graph = StateGraph()
compiled_graph = graph.compile()
# Create a custom agent graph
custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    prompt="You are a specialized agent for data analysis..."
)

# Use it as a custom subagent
custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=custom_graph
)

custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=compiled_graph
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents
)