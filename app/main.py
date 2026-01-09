"""
FastAPI application for the Council Agent.
Provides a POST /council endpoint for multi-agent decision making.
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.orchestrator import run_council


# Request/Response models
class AgentConfig(BaseModel):
    """Configuration for a custom agent."""
    name: str
    role: str


class CouncilRequest(BaseModel):
    """Request model for the council endpoint."""
    goal: str = Field(
        ...,
        description="The main goal or decision to be evaluated",
        json_schema_extra={
            "example": "Migrate my career and family to Europe within the next 12 months"
        }
    )
    context: str = Field(
        ...,
        description="Background information and current situation",
        json_schema_extra={
            "example": "Senior software engineer with 8 years experience, married with 2 children (ages 5 and 8), currently based in Istanbul. Wife is a freelance graphic designer. Have visited Berlin and Amsterdam for conferences."
        }
    )
    horizon_days: int = Field(
        default=365,
        description="Planning horizon in days",
        json_schema_extra={"example": 365}
    )
    resources: str = Field(
        ...,
        description="Available resources (financial, skills, network, etc.)",
        json_schema_extra={
            "example": "€45,000 savings, B2 German proficiency, professional network in Berlin tech scene, EU-recognized CS degree, remote-friendly current employer"
        }
    )
    nonnegotiables: str = Field(
        ...,
        description="Requirements that cannot be compromised",
        json_schema_extra={
            "example": "Children must be enrolled in quality schools before move, healthcare coverage must be continuous, minimum €4,000/month family income required"
        }
    )
    tradeoffs: str = Field(
        ...,
        description="Acceptable compromises or sacrifices",
        json_schema_extra={
            "example": "Willing to accept 20% salary reduction initially, can live in smaller apartment for first year, open to cities outside top 3 choices if visa is faster"
        }
    )
    agents: list[AgentConfig] | None = Field(
        default=None,
        description="Optional custom agent configurations"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "goal": "Migrate my career and family to Europe within the next 12 months",
                    "context": "Senior software engineer with 8 years experience, married with 2 children (ages 5 and 8), currently based in Istanbul. Wife is a freelance graphic designer. Have visited Berlin and Amsterdam for conferences.",
                    "horizon_days": 365,
                    "resources": "€45,000 savings, B2 German proficiency, professional network in Berlin tech scene, EU-recognized CS degree, remote-friendly current employer",
                    "nonnegotiables": "Children must be enrolled in quality schools before move, healthcare coverage must be continuous, minimum €4,000/month family income required",
                    "tradeoffs": "Willing to accept 20% salary reduction initially, can live in smaller apartment for first year, open to cities outside top 3 choices if visa is faster"
                }
            ]
        }
    }


class AgentOutput(BaseModel):
    """Output from a single agent."""
    name: str
    role: str
    output: str


class CouncilResponse(BaseModel):
    """Response model for the council endpoint."""
    agents: list[AgentOutput]
    final: str


# FastAPI app
app = FastAPI(
    title="Council Agent",
    description="""
Multi-agent council for strategic decision making.

## How it works

The council consists of three specialized agents:
- **Realist**: Focuses on feasibility, timelines, and practical pathways
- **Critic**: Challenges assumptions and identifies hidden risks  
- **Compassionate Coach**: Ensures sustainability and prevents burnout

### Two-Round Process

**Round 1**: Each agent independently analyzes the goal and produces:
- Assumptions (max 3, labeled as ASSUMPTION)
- Key Questions (max 3)
- Recommendation (exactly 3 concrete actions)
- Red Flags (exactly 2 risks)

**Round 2**: Each agent:
- Critiques the weakest points in other agents' recommendations
- Revises their own recommendations based on the discussion

**Final**: A Moderator synthesizes all perspectives into:
1. 3 Main Conclusions
2. 7-Day Action Plan
3. Risks and Mitigations (2 items)
4. Single Success Metric
""",
    version="0.2.0"
)


@app.post("/council", response_model=CouncilResponse)
def council_endpoint(request: CouncilRequest) -> CouncilResponse:
    """
    Run the two-round council workflow with multiple agents and a moderator.
    
    The council evaluates your goal through three specialized perspectives,
    then synthesizes a final actionable decision.
    """
    result = run_council(
        goal=request.goal,
        context=request.context,
        horizon_days=request.horizon_days,
        resources=request.resources,
        nonnegotiables=request.nonnegotiables,
        tradeoffs=request.tradeoffs,
        custom_agents=request.agents
    )
    return CouncilResponse(**result)


# Serve Static Files
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_root():
    """Serve the main UI."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    return """
    <html>
        <body>
            <h1>Council Agent</h1>
            <p>UI is being generated. Please refresh in a moment.</p>
        </body>
    </html>
    """


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
