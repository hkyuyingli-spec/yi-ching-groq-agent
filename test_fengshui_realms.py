import asyncio
import os

from dotenv import load_dotenv

from core.ascension_ai import AscensionAI

load_dotenv()


async def test_fengshui_responses():
    print("Feng Shui response validation suite...")
    if not os.getenv("GROQ_API_KEY"):
        print("GROQ_API_KEY missing; skipping live API calls.")
        return

    ai = AscensionAI()
    for query in [
        "What does the transition to Period 9 mean for my career in tech?",
        "My office faces South. How do I balance the Luo Shu square?",
        "How do Dragon Veins and Water Mouths relate to land development?",
    ]:
        response = await ai.respond(query)
        print(f"Master's Advice: {response[:200]}...")


if __name__ == "__main__":
    asyncio.run(test_fengshui_responses())
