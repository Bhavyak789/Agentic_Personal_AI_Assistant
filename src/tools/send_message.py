from typing import Optional, Type, Dict
from langchain_core.callbacks import CallbackManagerForToolRun
from langsmith import traceable
from pydantic import BaseModel
from langchain.tools import BaseTool
from src.agents.base import Agent
from src.utils import get_llm_by_provider
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate


class SendMessage(BaseTool):
    name: str = "SendMessage"
    description: str = "Use this to send a message to one of your sub-agents"
    args_schema: Type[BaseModel]
    agent_mapping: Dict[str, "Agent"] = None 

    def send_message(self, recipient: str, message: str) -> str:
        agent = self.agent_mapping.get(recipient)
        if agent:
            # Use the sub-agent's LLM directly to avoid nested tool-calls inside a tool.
            # This returns a plain text reply and prevents missing ToolMessage errors.
            try:
                llm = get_llm_by_provider(agent.model, temperature=agent.temperature)
                prompt_template = ChatPromptTemplate.from_messages([
                    SystemMessage(content=agent.system_prompt),
                    HumanMessage(content=message),
                ])
                chain = prompt_template | llm
                resp = chain.invoke({})
                return getattr(resp, "content", str(resp))
            except Exception:
                # Fallback: invoke the agent graph (may produce nested tool-calls)
                response = agent.invoke({"messages": [{"role": "user", "content": message}]})
                last_msg = response["messages"][-1]
                return getattr(last_msg, "content", last_msg.get("content", str(last_msg)))
        else:
            return f"Invalid recipient: {recipient}"

    @traceable(run_type="tool", name="SendMessage")
    def _run(
        self,
        recipient: str,
        message: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return self.send_message(recipient, message)