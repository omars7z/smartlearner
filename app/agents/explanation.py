from typing import Dict, Any, List
from app.core.base_agent import BaseAgent
from app.core.config import settings

# LangChain Imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ExplanationAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="llm_explainer_01")
        
        # 1. Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4", 
            temperature=0.7, 
            api_key=settings.OPENAI_API_KEY
        )
        
        # 2. Define Prompts using LCEL
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert AI tutor. Your student's mastery level is {mastery}. "
                       "Adapt your explanation accordingly. If mastery is low (<0.5), be simple and encouraging. "
                       "If mastery is high (>0.8), be technical and concise."),
            ("user", "Context: {context}\n\nQuestion: {query}")
        ])
        
        # 3. Create the Chain
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        query = data.get("query", "")
        docs = data.get("docs", [])
        mastery = data.get("mastery", 0.5)
        
        # Format context from list to string
        context_str = "\n".join(docs)
        
        # Invoke LangChain
        explanation = await self.chain.ainvoke({
            "mastery": mastery,
            "context": context_str,
            "query": query
        })
        
        return {"explanation": explanation}