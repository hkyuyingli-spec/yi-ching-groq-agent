import asyncio
import os
from core.ascension_ai import AscensionAI
from dotenv import load_dotenv

load_dotenv()

async def test_scenarios():
    print("🚀 Initializing Ascension AI Test Suite...")
    ai = AscensionAI()
    
    # Check for API Key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY not found in .env. Skipping actual API calls.")
        return

    # Scenario 1: Fundamental I Ching Query (Foundation Stage)
    print("\n--- SCENARIO 1: Fundamental I Ching Query (Foundation Stage) ---")
    query_1 = "I seek guidance on Hexagram 1 (The Creative). How does it affect my career?"
    print(f"Query: {query_1}")
    
    response_1, breakthrough_1 = await ai.cultivate(query_1)
    print(f"Current Stage: {ai.state.current_stage}")
    print(f"Qi: {ai.state.qi_energy}, Dao: {ai.state.dao_comprehension:.2f}")
    print(f"Breakthrough: {breakthrough_1}")
    print(f"Response Snippet: {response_1[:150]}...")

    # Scenario 2: Direct Metaphysical Consultation (RAG Check)
    print("\n--- SCENARIO 2: Feng Shui Consultation (RAG Context Check) ---")
    query_2 = "How can I optimize the Qi flow in my office using the Luo Shu square?"
    print(f"Query: {query_2}")
    
    response_2, breakthrough_2 = await ai.cultivate(query_2)
    print(f"Current Stage: {ai.state.current_stage}")
    print(f"Qi: {ai.state.qi_energy}, Dao: {ai.state.dao_comprehension:.2f}")
    print(f"Breakthrough: {breakthrough_2}")
    print(f"Response Snippet: {response_2[:150]}...")

    # Scenario 3: Rapid Cultivation to Breakthrough
    print("\n--- SCENARIO 3: Rapid Cultivation Sequence (Testing Breakthrough) ---")
    # Artificially boost Dao to trigger breakthrough if not already there
    ai.state.dao_comprehension = 95.0 
    print(f"Simulating near-breakthrough state (Dao: {ai.state.dao_comprehension})")
    
    query_3 = "Show me the path to the Nascent Soul realm."
    print(f"Query: {query_3}")
    
    response_3, breakthrough_3 = await ai.cultivate(query_3)
    print(f"Current Stage: {ai.state.current_stage}")
    print(f"Qi: {ai.state.qi_energy}, Dao: {ai.state.dao_comprehension:.2f}")
    print(f"Breakthrough: {breakthrough_3}")
    
    if breakthrough_3:
        print("✨ SUCCESS: Breakthrough triggered and stage advanced!")
    else:
        print("⚠️ NOTE: Breakthrough not triggered (Dao threshold not reached).")

if __name__ == "__main__":
    asyncio.run(test_scenarios())
