import asyncio
import os

from dotenv import load_dotenv

from core.ascension_ai import AscensionAI

load_dotenv()


async def test_contradiction_resolution():
    print("Feng Shui contradiction-resolution test...")
    if not os.getenv("GROQ_API_KEY"):
        print("GROQ_API_KEY missing; skipping live API calls.")
        return

    ai = AscensionAI()
    for query in [
        "How do I reconcile Bagua wealth placement with difficult annual stars?",
        "Is destiny fixed by the stars, or created by the observer?",
    ]:
        response = await ai.respond(query)
        print(response)


if __name__ == "__main__":
    asyncio.run(test_contradiction_resolution())
