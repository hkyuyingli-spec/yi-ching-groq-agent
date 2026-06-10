import asyncio
import os
from core.ascension_ai import AscensionAI
from dotenv import load_dotenv

load_dotenv()

async def test_contradiction_resolution():
    print("🌌 High-Realm Synthesis & Contradiction Resolution Test...")
    ai = AscensionAI()
    
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY missing.")
        return

    # Scenario: Resolving Contradictions (Unity Stage)
    # The room is 'Wealth' sector in Bagua but has 'Illness' star in Xuan Kong.
    # Unity stage uses DeepSeek R1 for reasoning.
    ai.state.dao_comprehension = 400.0
    ai.state.stage_index = 4
    ai.state.current_stage = "Unity"
    
    print(f"\n--- SCENARIO 1: Resolving Systemic Contradictions ({ai.state.current_stage} Stage) ---")
    query_1 = """
    My bedroom is in the Southeast. 
    According to the Bagua (Sun/Wealth), it should be lucky. 
    But a Xuan Kong consultant says the #2 (Illness) and #5 (Misfortune) stars are there this year. 
    How do I resolve these contradictory school of thoughts?
    """
    print(f"Query: {query_1}")
    
    response_1, _ = await ai.cultivate(query_1)
    print(f"Stage: {ai.state.current_stage} | Model: {ai.stages[ai.state.current_stage].model}")
    print("\n--- MASTER'S SYNTHESIS ---")
    print(response_1)
    print("--------------------------")

    # Scenario: The Omniscient Oracle (Great Luo Stage)
    # Testing transcendental, non-dualistic answers.
    ai.state.dao_comprehension = 600.0
    ai.state.stage_index = 6
    ai.state.current_stage = "Great Luo"

    print(f"\n--- SCENARIO 2: Sovereign Transcendent Awareness ({ai.state.current_stage} Stage) ---")
    query_2 = "Is destiny fixed by the stars, or is it created by the observer? Resolve the paradox of choice vs. fate."
    print(f"Query: {query_2}")
    
    response_2, _ = await ai.cultivate(query_2)
    print(f"Stage: {ai.state.current_stage} | Model: {ai.stages[ai.state.current_stage].model}")
    print("\n--- ORACLE'S DECREE ---")
    print(response_2)
    print("--------------------------")

if __name__ == "__main__":
    asyncio.run(test_contradiction_resolution())
