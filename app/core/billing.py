# Inside app/agents/question_gen.py
from typing import Any, Dict
from app.core.billing import log_usage

async def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
    topic = data.get("topic", "General")
    
    if self.use_mock:
        return self.get_mock_question(topic)

    try:
        # Prepare the prompt string for counting
        prompt_str = self.prompt.format(topic=topic)
        
        result = await self.chain.ainvoke({"topic": topic})
        
        # Log the usage
        log_usage(
            model_name=self.active_model or "gemini", 
            topic=topic, 
            input_txt=prompt_str, 
            output_txt=str(result.dict())
        )
        
        return result.dict()
    except Exception as e:
        print(f"Error: {e}")
        return self.get_mock_question(topic)