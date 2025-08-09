# A2A components for agent execution
import ast
from a2a.server.agent_execution import AgentExecutor  # Base class for agent executors
from a2a.server.agent_execution.context import RequestContext  # Handles request data
from a2a.server.events.event_queue import EventQueue  # Manages message events
from a2a.utils import new_agent_parts_message  # Helper for creating responses

# ADK components for running the sentiment agent
from google.adk.sessions import InMemorySessionService  # Manages agent state

from my_a2a.multi_a2a_1.planner_agent.agent import generate_plan

class PlannerAgentExecutor(AgentExecutor):
    def __init__(self):        
        # Simple in-memory session (no persistence needed for stateless agent)
        self.session_service = InMemorySessionService()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        current_session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )

        print(f"\n Session {current_session.id} created successfully.")

        # Extract the text to analyze from the A2A request
        user_input_text = context.get_user_input()
        text, available_agents = user_input_text.split('\n')
        available_agents = ast.literal_eval(available_agents)

        # Process the input through our planner agent
        plan = await generate_plan(
            user_input=text,
            available_agents=available_agents
        )
        
        if plan is not None:
            # Create and send an A2A-compatible message with the result
            # This will be received by the requesting agent
            await event_queue.enqueue_event(
                new_agent_parts_message(plan)
            )
        else:
            raise RuntimeError("No final response received from the agent.")

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise NotImplementedError("Cancellation is not supported for planner agent.")