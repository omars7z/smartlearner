from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class InteractionRequest(BaseModel):
    user_id: str
    query: str
    interaction_type: str
    context: Optional[Dict[str, Any]] = None

'''class InteractionResponse(BaseModel):
    response_id: str
    content: Any
    agent_trace: List[str]
    timestamp: str'''
    
class InteractionResponse(BaseModel):
    content: Any