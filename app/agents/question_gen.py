import os
import asyncio
from typing import Dict, Any
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

class QuestionSchema(BaseModel):
    question: str = Field(description="The question text")
    options: list[str] = Field(description="List of 4 options")
    answer: str = Field(description="The correct answer")

class QuestionGenAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        print("the google api key is " + self.api_key)
        self.use_mock = False
        self.active_model = None
        self.chain = None

        self.models_to_try = [
            "gemini-1.5-flash",      # Fastest & Newest Standard
            "gemini-1.5-pro",        # More powerful
        ]

        if not self.api_key:
            print("⚠️  No GOOGLE_API_KEY found. Using Mock Mode.")
            self.use_mock = True

    async def _initialize_chain(self, model_name: str):
        """Helper to setup the chain with a specific model"""
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name, 
                google_api_key=self.api_key,
                temperature=0.7,
                convert_system_message_to_human=True # Helps with older models
            )
            
            parser = PydanticOutputParser(pydantic_object=QuestionSchema)
            
            prompt = PromptTemplate(
                template="""
                You are a computer science tutor. Generate a multiple-choice question about: {topic}.
                Ensure you generate valid JSON exactly matching the instructions.
                
                {format_instructions}
                """,
                input_variables=["topic"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )
            
            return prompt | llm | parser
        except Exception:
            return None

    async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        topic = data.get("topic", "General")
        
        if self.use_mock:
            return self.get_mock_question(topic)

        if not self.chain:
            print(f"🔄 Finding a working Gemini model for your key...")
            for model in self.models_to_try:
                print(f"   👉 Testing model: {model}...")
                try:
                    # Create a temporary chain to test
                    temp_chain = await self._initialize_chain(model)
                    if temp_chain:
                        # Attempt a test generation
                        result = await temp_chain.ainvoke({"topic": topic})
                        
                        print(f"   ✅ SUCCESS! Using model: {model}")
                        self.chain = temp_chain
                        self.active_model = model
                        return result.dict()
                except Exception as e:
                    print(f"   ❌ {model} failed: {str(e)[:100]}...")
                    continue # Try the next model

            print("⚠️  All Gemini models failed. Switching to MOCK MODE.")
            self.use_mock = True
            return self.get_mock_question(topic)

        # If we already have a working chain, just use it
        try:
            result = await self.chain.ainvoke({"topic": topic})
            return result.dict()
        except Exception as e:
            print(f"❌ Error with active model {self.active_model}: {e}")
            return self.get_mock_question(topic)

    def get_mock_question(self, topic: str) -> Dict[str, Any]:
        """Fallback for when the API is down"""
        return {
            "question": f"[MOCK] What characterizes {topic} in computer science?",
            "options": [
                "It optimizes memory",
                "It reduces latency",
                "It scales horizontally",
                "All of the above"
            ],
            "answer": "All of the above"
        }