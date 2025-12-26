from typing import Dict, Any
from app.core.base_agent import BaseAgent
import traceback

class ExamAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="exam_grader_01")

    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        submission = data.get("submission", "")
        # WARNING: In production, use Docker/Sandboxing here
        result = self.execute_unsafe_code(submission) 
        feedback = self.generate_feedback(result["success"], result["output"])
        return {"result": result, "feedback": feedback}

    def execute_unsafe_code(self, code: str) -> Dict[str, Any]:
        buffer = {}
        try:
            exec(code, {}, buffer)
            return {"success": True, "output": str(buffer)}
        except Exception:
            return {"success": False, "output": traceback.format_exc()}

    def generate_feedback(self, success: bool, output: str) -> str:
        if success:
            return "Great job! Your code ran successfully."
        return f"Your code encountered an error: {output[:50]}..."