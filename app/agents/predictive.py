from typing import Dict, Any
from app.core.base_agent import BaseAgent

class PredictiveAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="predictive_dkt_01")
        # In-memory mock DB for demonstration
        self._mock_db_state = {}

    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Basic routing for internal agent tasks
        action = data.get("action")
        
        if action == "initialize":
             return self.initialize_student_state(data.get("user_id"), data.get("vector", {}))
        
        elif action == "get_state":
             return self._mock_db_state.get(data.get("user_id"), {})
        
        return {"status": "no_action_defined"}

    def initialize_student_state(self, user_id: str, initial_vector: Dict[str, float]) -> Dict[str, Any]:
        """
        Called ONLY after a placement test to set the baseline.
        Overwrites existing state.
        """
        print(f"[{self.agent_id}] INITIALIZING state for {user_id} based on placement results.")
        self._mock_db_state[user_id] = initial_vector
        return {"status": "initialized", "state": initial_vector}

    def update_dkt_mastery(self, user_id: str, log_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Standard incremental update after a regular learning activity.
        """
        print(f"[{self.agent_id}] Incrementally updating DKT vector...")
        current_state = self._mock_db_state.get(user_id, {})
        
        # Mock update logic: increase mastery slightly
        topic = log_data.get("topic")
        if topic:
             current_state[topic] = current_state.get(topic, 0.1) + 0.05
             self._mock_db_state[user_id] = current_state
             
        return current_state

    def get_risk_score(self, user_id: str) -> float:
        # Simply avg mastery to guess risk. Low mastery = high risk.
        state = self._mock_db_state.get(user_id, {})
        if not state: return 0.5
        
        avg_mastery = sum(state.values()) / len(state) if len(state) > 0 else 0.5
        return 1.0 - avg_mastery