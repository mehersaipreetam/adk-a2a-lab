# A2A components for agent execution
import json
from typing import List

# Import the LLM completion model
from my_a2a.llm.model import llm_complete

# The LangGraph library is used to define the agent's logic as a stateful graph.
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import re

# 1. Define an asynchronous function for the core logic using an LLM
async def pos_tag_query(text: str) -> List[List[str]]:
    """
    Performs Part-of-Speech tagging on a given text string using an LLM.

    The function prompts the LLM to return a JSON array of arrays, 
    where each inner array contains a word and its POS tag.

    Args:
        text: The input string to be tagged.

    Returns:
        A list of lists, where each inner list contains a word and its POS tag.
    """
    # The prompt for the LLM
    prompt = (
        "Perform Part-of-Speech tagging on the following sentence. "
        "Return the result as a list of dicts, where each inner "
        "dict contains the word and its corresponding POS tag. "
        "Do not include any extra text or formatting outside the JSON."
        f"\n\nText: \"{text}\""
    )

    # Call the LLM completion model
    response = await llm_complete(prompt)
    print(f"LLM response for POS tagging: {response}")
    pattern = r"^```json\n|```$"
    response = re.sub(pattern, "", response, flags=re.MULTILINE).strip()    

    try:
        parsed_response = json.loads(response)
        if isinstance(parsed_response, list):
            return parsed_response
        else:
            raise ValueError("LLM response is not a list.")
    except (json.JSONDecodeError, ValueError) as e:
        raise RuntimeError(f"Failed to parse LLM response as JSON: {e}")

# 2. Define the Graph State
class AgentState(TypedDict):
    """Represents the state of our graph."""
    text_input: str
    pos_tags: List[List[str]]

# 3. Define the Nodes (the logic of the agent)
# The node must be an async function to await the LLM call.
async def pos_tag_node(state: AgentState) -> AgentState:
    """A node that calls the POS tagging function on the input text."""
    print("Executing POS tagging node...")
    
    # Get the text from the current state
    text = state['text_input']
    
    # Await the asynchronous function call
    tags = await pos_tag_query(text)
    
    # Store the result in the state
    state['pos_tags'] = tags
    
    print(f"POS tags generated: {tags}")
    
    return state

# 4. Build the LangGraph
workflow = StateGraph(AgentState)
workflow.add_node("tagger", pos_tag_node)
workflow.add_edge(START, "tagger")
workflow.add_edge("tagger", END)
app = workflow.compile()