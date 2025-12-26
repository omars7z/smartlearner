from typing import Dict, Any
from app.core.base_agent import BaseAgent

class CurriculumAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="curriculum_rl_01")

    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "processed_by_curriculum"}

    def determine_next_topic(self, mastery_vector: Dict[str, float]) -> str:
        # Simple logic: return the topic with lowest mastery
        if not mastery_vector:
            return "intro_to_python"
        return min(mastery_vector, key=mastery_vector.get)

    def autonomously_intervene(self, risk_score: float) -> bool:
        threshold = 0.7
        return risk_score > threshold