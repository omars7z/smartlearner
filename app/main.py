import uuid
import datetime
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# from sqlalchemy import text
from app.agents.placement_test import PlacementAgent
from app.agents.question_gen import QuestionGenAgent
from app.core.config import Settings
from app.models.schemas import InteractionRequest, InteractionResponse
from app.orchestrator.mcp_server import MCPServer
# from app.core.database import engine, Base, get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartLearner-API")

# Create Database Tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartLearner AI Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mcp_server = MCPServer(openai_api_key=Settings.OPENAI_API_KEY)
placement_agent = PlacementAgent()
question_agent = QuestionGenAgent()


@app.get("/")
async def root():
    return {"message": "API is running"}

@app.post("/interact", response_model=InteractionResponse)
async def interact(request: InteractionRequest):
    try:
        logger.info(f"Received request: {request.interaction_type}")
        
        response_data = {}
        if request.interaction_type == "placement_start":
            # Generate the test
            response_data = await placement_agent.process_request({
                "interaction_type": "start"
            })
            
        elif request.interaction_type == "placement_submit":
            # Grade the test
            submissions = request.context.get("submissions", [])
            response_data = await placement_agent.process_request({
                "interaction_type": "submit",
                "submissions": submissions
            })

        elif request.interaction_type == "generate_question":
            topic = request.context.get("topic", "General")
            response_data = await question_agent.process_request({
                "topic": topic
            })
            
        else:
            response_data = {"error": "Only placement_start and placement_submit are supported in this mode."}

        return InteractionResponse(content=response_data)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


'''@app.post("/interact", response_model=InteractionResponse)
async def interact(request: InteractionRequest):
    try:
        # Pass the request to the Orchestrator
        result = await mcp_server.route_request(
            query=request.query,
            user_id=request.user_id,
            interaction_type=request.interaction_type,
            context_data=request.context
        )
        
        return InteractionResponse(
            response_id=str(uuid.uuid4()),
            content=result["content"],
            agent_trace=result["agent_trace"],
            timestamp=datetime.datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "active", "agents": list(mcp_server.agents.keys())}

app.get("/db-health")
async def test_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1"))
        return {"status": "connected", "result": result.scalar()}
    except Exception as e:
        return {"status": "failed", "error": str(e)}'''