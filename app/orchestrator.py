"""
Orchestrator that runs the two-round council workflow.
Coordinates agents and moderator to produce final decision.
"""
from app.agents import AGENTS, MODERATOR, get_round2_prompt, create_agent
from app.llm_client import call_gemini


def build_user_message(
    goal: str,
    context: str,
    horizon_days: int,
    resources: str,
    nonnegotiables: str,
    tradeoffs: str
) -> str:
    """Construct the user message from input fields."""
    return f"""Goal: {goal}

Context: {context}

Time Horizon: {horizon_days} days

Available Resources: {resources}

Non-Negotiables: {nonnegotiables}

Acceptable Tradeoffs: {tradeoffs}"""


def run_agent_round1(agent, user_message: str) -> dict:
    """Run a single agent in Round 1 and return its response."""
    output = call_gemini(
        system_prompt=agent.system_prompt,
        user_message=user_message
    )
    return {
        "name": agent.name,
        "role": agent.role,
        "round1_output": output
    }


def run_agent_round2(agent, user_message: str, all_round1_outputs: dict[str, str]) -> str:
    """
    Run a single agent in Round 2.
    Agent critiques others and revises their own recommendation.
    """
    # Build context with all round 1 outputs
    round2_prompt = get_round2_prompt(agent)
    
    other_outputs = {
        name: output 
        for name, output in all_round1_outputs.items() 
        if name != agent.name
    }
    
    output = call_gemini(
        system_prompt=round2_prompt,
        user_message=f"Shared context:\n{user_message}\n\nOther agents' outputs:\n{other_outputs}"
    )
    return output


def run_moderator(agent_results: list[dict], user_message: str) -> str:
    """
    Run the moderator to synthesize all agent outputs from both rounds.
    """
    # Build context from all agent outputs (both rounds)
    agents_context = "\n\n---\n\n".join([
        f"### {a['name']} ({a['role']})\n\n**Round 1:**\n{a['round1_output']}\n\n**Round 2:**\n{a['round2_output']}"
        for a in agent_results
    ])
    
    moderator_input = f"""{user_message}

===
AGENT OUTPUTS (Both Rounds):
{agents_context}
===

Please synthesize these perspectives into a final decision following your exact output format."""
    
    return call_gemini(
        system_prompt=MODERATOR.system_prompt,
        user_message=moderator_input
    )


def run_council(
    goal: str,
    context: str,
    horizon_days: int,
    resources: str,
    nonnegotiables: str,
    tradeoffs: str,
    custom_agents: list = None
) -> dict:
    """
    Run the full two-round council workflow:
    
    Round 1: Each agent independently produces structured output
    Round 2: Each agent critiques others and revises their recommendation
    Moderator: Synthesizes all outputs into final decision
    """
    # Build the shared user message
    user_message = build_user_message(
        goal=goal,
        context=context,
        horizon_days=horizon_days,
        resources=resources,
        nonnegotiables=nonnegotiables,
        tradeoffs=tradeoffs
    )
    
    # Determine agents to use
    if custom_agents:
        active_agents = [create_agent(a.name, a.role) for a in custom_agents]
    else:
        active_agents = AGENTS

    # === ROUND 1 ===
    # Each agent independently produces structured output
    agent_results = [run_agent_round1(agent, user_message) for agent in active_agents]
    
    # Collect round 1 outputs for cross-reference in round 2
    round1_outputs = {
        result["name"]: result["round1_output"]
        for result in agent_results
    }
    
    # === ROUND 2 ===
    # Each agent critiques others and revises their recommendation
    for i, agent in enumerate(active_agents):
        round2_output = run_agent_round2(agent, user_message, round1_outputs)
        agent_results[i]["round2_output"] = round2_output
    
    # === MODERATOR ===
    # Synthesize all outputs into final decision
    final_decision = run_moderator(agent_results, user_message)
    
    # Format output for API response
    agents_output = [
        {
            "name": r["name"],
            "role": r["role"],
            "output": f"## Round 1\n{r['round1_output']}\n\n## Round 2\n{r['round2_output']}"
        }
        for r in agent_results
    ]
    
    return {
        "agents": agents_output,
        "final": final_decision
    }
