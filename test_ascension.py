import asyncio
import os

from dotenv import load_dotenv

from core.ascension_ai import AscensionAI

load_dotenv()


async def test_scenarios():
    print("Initializing I Ching response test...")
    if not os.getenv("GROQ_API_KEY"):
        print("GROQ_API_KEY not found; skipping live API calls.")
        return

    ai = AscensionAI()
    for query in [
        "I seek guidance on Hexagram 1 (The Creative). How does it affect my career?",
        "How can I optimize the flow in my office using the Luo Shu square?",
        "What practical step should I take next?",
    ]:
        response = await ai.respond(query)
        print(f"Response Snippet: {response[:150]}...")


if __name__ == "__main__":
    asyncio.run(test_scenarios())
