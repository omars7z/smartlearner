from typing import Dict, Any
from app.agents.question_gen import QuestionGenAgent

class PlacementAgent:
    def __init__(self):
        self.qgen_agent = QuestionGenAgent()
        # The topics we want to generate questions for
        self.syllabus = ["machine learning"]

    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        interaction_type = data.get("interaction_type")

        if interaction_type == "submit":
            # Simple grading logic
            return {
                "status": "graded", 
                "initial_state": {"Python": 0.8, "Algorithms": 0.4} 
            }
        
        return await self.generate_placement_test()

    async def generate_placement_test(self) -> Dict[str, Any]:
        questions = []
        
        print("Generating questions... this may take a few seconds.")
        
        for i, topic in enumerate(self.syllabus):
            q_data = await self.qgen_agent.process_request({"topic": topic})
            
            questions.append({
                "id": i + 1,
                "question": q_data.get("question"),
                "options": q_data.get("options"),
                "answer": q_data.get("answer"),
                "assessed_topic": topic
            })
            
        return {"questions": questions}