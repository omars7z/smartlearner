from typing import Dict, Any, List
from fastapi import HTTPException
import datetime

# from app.agents.predictive import PredictiveAgent
# from app.agents.curriculum import CurriculumAgent
# from app.agents.rag import RAGAgent
# from app.agents.explanation import ExplanationAgent
# from app.agents.exam import ExamAgent
from app.agents.question_gen import QuestionGenAgent

class MCPServer:
    def __init__(self, openai_api_key: str):
        # Registry of initialized agents
        self.agents = {
            # "predictive": PredictiveAgent(),
            # "curriculum": CurriculumAgent(),
            # "rag": RAGAgent(),
            # "explanation": ExplanationAgent(),
            # "exam": ExamAgent(),
            "qgen": QuestionGenAgent()
        }

    '''async def _get_student_state(self, user_id: str) -> Dict[str, Any]:
         # Helper to fetch state from predictive agent
         return await self.agents["predictive"].process_request({
             "action": "get_state", 
             "user_id": user_id
         })'''

    async def route_request(self, query: str, user_id: str, interaction_type: str, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main routing logic. Decides which agents to invoke based on intent.
        """
        agent_trace = []
        response_content = {}
        
        # --- 1. Placement Test Flow ---
        if interaction_type == "placement_start":
            place_agent = self.agents["placement"]
            test_res = await place_agent.process_request({"user_id": user_id})
            agent_trace.append("placement_gen")
            response_content = test_res

        elif interaction_type == "placement_submit":
            place_agent = self.agents["placement"]
            pred_agent = self.agents["predictive"]
            
            submissions = context_data.get("submissions", []) if context_data else []
            
            # Grade
            grading_res = await place_agent.process_request({"submissions": submissions})
            agent_trace.append("placement_grade")
            
            initial_vector = grading_res.get("initial_mastery_vector", {})
            
            # Initialize DKT
            await pred_agent.process_request({
                "action": "initialize",
                "user_id": user_id,
                "vector": initial_vector
            })
            agent_trace.append("predictive_init")
            
            response_content = {"status": "Placement complete", "initial_state": initial_vector}

        # --- 2. Standard Flows ---
        elif interaction_type == "learn":
            # RAG -> Explanation
            rag_agent = self.agents["rag"]
            expl_agent = self.agents["explanation"]
            
            # Retrieve
            rag_res = await rag_agent.process_request({"query": query})
            agent_trace.append("rag")
            
            # Explain
            expl_res = await expl_agent.process_request({
                "query": query,
                "docs": rag_res.get("retrieved_docs", []),
                "mastery": 0.5 
            })
            agent_trace.append("explanation")
            response_content = expl_res

        elif interaction_type == "quiz":
            curr_agent = self.agents["curriculum"]
            qgen_agent = self.agents["qgen"]
            
            # Get state
            state_res = await self._get_student_state(user_id)
            current_state = state_res if isinstance(state_res, dict) else {}

            # Determine Topic
            next_topic = curr_agent.determine_next_topic(current_state)
            agent_trace.append("curriculum")
            
            # Generate Question
            q_res = await qgen_agent.process_request({"topic": next_topic})
            agent_trace.append("qgen")
            response_content = q_res

        elif interaction_type == "exam":
            exam_agent = self.agents["exam"]
            exam_res = await exam_agent.process_request({"submission": query})
            agent_trace.append("exam")
            response_content = exam_res

        else:
            raise HTTPException(status_code=400, detail=f"Unknown interaction type: {interaction_type}")

        return {
            "content": response_content,
            "agent_trace": agent_trace
        }