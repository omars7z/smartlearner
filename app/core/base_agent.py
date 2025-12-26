from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Abstract base class for all SmartLearner agents.
    Enforces a standard interface for the MCP Orchestrator.
    """
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    @abstractmethod
    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard entry point for the agent.
        Must return a dictionary containing the result.
        """
        pass