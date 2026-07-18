import random
import time
from typing import Dict, List, Optional, Callable
import json
import os

from dotenv import load_dotenv
from groq import AsyncGroq
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

load_dotenv()


class GroqManager:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.cache = {}
        self.max_retries = 3

    async def get_streaming_response(
        self,
        model: str,
        messages: List[Dict[str, str]],
        on_token: Optional[Callable[[str], None]] = None,
    ) -> str:
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                stream = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                )

                full_content = ""
                async for chunk in stream:
                    token = chunk.choices[0].delta.content or ""
                    full_content += token
                    if on_token:
                        on_token(token)
                return full_content
            except Exception as error:
                if "429" in str(error):
                    retry_count += 1
                    time.sleep((2 ** retry_count) + random.random())
                else:
                    raise
        return "The request was interrupted by a rate limit exception."


class AscensionAI:
    """Groq-backed I Ching response service.

    The class name remains temporarily for import compatibility. It contains no
    cultivation state or progression mechanics.
    """

    def __init__(self, hexagrams_path="data/hexagrams.json", cosmology_path="data/cosmology.json"):
        self.groq = GroqManager()
        self.hexagrams = self._load_json(hexagrams_path)
        self.cosmology = self._load_json(cosmology_path)
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self._prepare_vector_index()

    def _load_json(self, path: str) -> Dict:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def _prepare_vector_index(self) -> None:
        """Build a TF-IDF index of reference material for contextual retrieval."""
        self.corpus = []
        self.corpus_metadata = []

        for hexagram_id, data in self.hexagrams.items():
            text = (
                f"Hexagram {hexagram_id} {data.get('name')} {data.get('english')} "
                f"{data.get('judgment')} {data.get('image')} "
                f"{' '.join(data.get('keywords', []))}"
            )
            self.corpus.append(text)
            self.corpus_metadata.append({
                "type": "hexagram",
                "id": hexagram_id,
                "content": (
                    f"Hexagram {hexagram_id} ({data.get('name')} - "
                    f"{data.get('english')}): {data.get('judgment')}"
                ),
            })

        for key, value in self.cosmology.items():
            if isinstance(value, dict):
                self.corpus.append(f"Cosmology {key} {value}")
                self.corpus_metadata.append({
                    "type": "cosmology",
                    "id": key,
                    "content": f"Cosmological Insight ({key}): {str(value)[:200]}...",
                })

        if self.corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def _get_rag_context(self, query: str) -> str:
        if not self.corpus:
            return "General I Ching background applies."

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        top_indices = np.argsort(similarities)[-3:][::-1]
        context = [
            self.corpus_metadata[index]["content"]
            for index in top_indices
            if similarities[index] > 0.1
        ]
        return "\n\n".join(context) if context else "The reference material offers no close textual match."

    async def respond(self, query: str, on_token: Optional[Callable[[str], None]] = None) -> str:
        """Return a grounded I Ching response without progression mechanics."""
        context = self._get_rag_context(query)
        system_message = (
            "You are a careful I Ching interpreter. Base your response on the "
            "provided reading context and avoid gamified cultivation language."
            f"\n\nReference Metadata:\n{context}"
        )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ]
        return await self.groq.get_streaming_response("qwen/qwen3.6-27b", messages, on_token)
