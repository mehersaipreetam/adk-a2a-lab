import json
import re
from typing import List

from my_a2a.llm.model import llm_complete
from langchain.prompts import ChatPromptTemplate

planner_prompt = ChatPromptTemplate.from_template("""
You are an NLP Planner Agent.
You do NOT execute any tasks yourself.
You only create a plan for other agents to execute.

Available agents:
{available_agents}
                                                  
Output the plan in strict JSON format:
[
  {{ "agent": "<agent_name>", "input": "<input_text>" }},
  ...
]

Example:
User: "Check the sentiment and POS tags for 'I love Groq models!'"
Plan:
[
  {{ "agent": "<agent1>", "input": "I love Groq models!" }},
  {{ "agent": "<agent2>", "input": "I love Groq models!" }}
]

Now, given the user request:
"{user_input}"
Produce the JSON plan only.
""")


async def generate_plan(user_input: str, available_agents: List[str]) -> List[dict]:
    """
    Generate an execution plan for NLP tasks using available agents.
    
    Args:
        user_input: The user's NLP request
        available_agents: List of available agent names
    
    Returns:
        List of dictionaries containing the execution plan
    """
    # Format available agents for prompt
    agents_list = "\n".join([f"- {agent}" for agent in available_agents])
    
    # Generate the plan
    prompt = planner_prompt.format(
        user_input=user_input,
        available_agents=agents_list
    )
    response = await llm_complete(prompt)
    pattern = r"^```json\n|```$"

    response = re.sub(pattern, "", response, flags=re.MULTILINE).strip()    
    # Parse and validate the JSON response
    try:
        plan = json.loads(response.strip())
        if not isinstance(plan, list):
            raise ValueError("Plan must be a list of tasks")
        
        # Validate each task in the plan
        for task in plan:
            if not isinstance(task, dict):
                raise ValueError("Each task must be a dictionary")
            if "agent" not in task or "input" not in task:
                raise ValueError("Each task must have 'agent' and 'input' fields")
            if task["agent"] not in available_agents:
                raise ValueError(f"Unknown agent: {task['agent']}")
        
        return plan
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in plan response")


# async def main():
#     """Example usage of the planner"""
#     user_request = "Find sentiment of 'LangChain is great' and extract named entities."
#     available_agents = ["sentiment_agent", "pos_tag_agent", "topic_agent"]
    
#     try:
#         plan = await generate_plan(user_request, available_agents)
#         print("Generated Plan:")
#         print(json.dumps(plan, indent=2))
#     except ValueError as e:
#         print(f"Error generating plan: {e}")


# if __name__ == "__main__":
#     asyncio.run(main())
