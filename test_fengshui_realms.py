import asyncio
import os
from core.ascension_ai import AscensionAI
from dotenv import load_dotenv

load_dotenv()

async def test_fengshui_realms():
    print("🔮 Feng Shui Multi-Realm Validation Suite...")
    ai = AscensionAI()
    
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY missing.")
        return

    # Scenario 1: Period 9 Transition (Foundation Stage)
    # Focus: How the AI explains the upcoming 20-year cycle simply.
    print("\n--- SCENARIO 1: Period 9 & Technology (Foundation) ---")
    query_1 = "What does the transition to Period 9 mean for my career in tech? I've heard it's about Fire."
    print(f"Query: {query_1}")
    
    response_1, _ = await ai.cultivate(query_1)
    print(f"Stage: {ai.state.current_stage} | Qi: {ai.state.qi_energy}")
    print(f"Master's Advice: {response_1[:200]}...")

    # Scenario 2: Xuan Kong Flying Stars (Nascent Soul Stage)
    # Trigger breakthrough to Nascent Soul for a more analytical perspective
    ai.state.dao_comprehension = 100.0
    ai.state.stage_index = 1
    ai.state.current_stage = "Nascent Soul"
    
    print("\n--- SCENARIO 2: Xuan Kong & Palace Mapping (Nascent Soul) ---")
    query_2 = "My office faces South. How do I balance the #2 and #5 stars using the Luo Shu square?"
    print(f"Query: {query_2}")
    
    response_2, _ = await ai.cultivate(query_2)
    print(f"Stage: {ai.state.current_stage} | Dao: {ai.state.dao_comprehension:.2f}")
    print(f"Master's Advice: {response_2[:200]}...")

    # Scenario 3: Form School & Dragon Veins (Spirit Transformation Stage)
    # Advance to Spirit Transformation for ethical/spiritual value integration
    ai.state.dao_comprehension = 200.0
    ai.state.stage_index = 2
    ai.state.current_stage = "Spirit Transformation"

    print("\n--- SCENARIO 3: Zang Shu & Dragon Veins (Spirit Transformation) ---")
    query_3 = "How do 'Dragon Veins' and 'Water Mouths' from the Book of Burial relate to the ethics of land development?"
    print(f"Query: {query_3}")
    
    response_3, _ = await ai.cultivate(query_3)
    print(f"Stage: {ai.state.current_stage} | Model: {ai.stages[ai.state.current_stage].model}")
    print(f"Master's Advice: {response_3[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_fengshui_realms())
