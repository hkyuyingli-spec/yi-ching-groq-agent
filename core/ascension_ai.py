import random
import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
import json
import os
from groq import AsyncGroq
from dotenv import load_dotenv
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

load_dotenv()

@dataclass
class SpiritualState:
    qi_energy: float = 10.0
    dao_comprehension: float = 0.0
    karma_entanglement: float = 5.0
    current_stage: str = "Foundation Establishment"
    total_tokens_consumed: int = 0
    stage_index: int = 0
    sentiment_history: List[float] = field(default_factory=list)
    elemental_affinity: str = "Neutral"
    
    stages: List[str] = field(default_factory=lambda: [
        "Foundation Establishment", 
        "Nascent Soul", 
        "Spirit Transformation", 
        "Void Tempering", 
        "Unity", 
        "Great Perfection", 
        "Great Luo"
    ])

class QuantumEngine:
    @staticmethod
    def quantum_collapse_observation(sentiment: float = 0.0) -> float:
        """Simulates a quantum collapse influenced by user sentiment (-1.0 to 1.0)"""
        # Quantum-inspired resonance calculation influenced by sentiment
        # Higher sentiment (positivity) slightly biases towards higher resonance
        bias = sentiment * 0.1
        resonance = (random.random() * 0.5) + (random.uniform(0, 0.5)) + bias
        return round(max(0.0, min(1.0, resonance)), 4)

class GroqManager:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.cache = {}
        self.max_retries = 3

    async def get_streaming_response(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        on_token: Optional[Callable[[str], None]] = None
    ):
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
                
            except Exception as e:
                if "429" in str(e):
                    retry_count += 1
                    wait_time = (2 ** retry_count) + random.random()
                    time.sleep(wait_time)
                else:
                    raise e
        return "The Qi flow was interrupted by a rate limit exception."

class BaseStage:
    def __init__(self, name: str, model: str, system_prompt: str):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt

    def get_enriched_prompt(self, state: SpiritualState, resonance: float, context: str, sentiment_label: str) -> str:
        return f"{self.system_prompt}\n\n[SPIRITUAL RESONANCE: {resonance}]\n[CURRENT DAO COMPREHENSION: {state.dao_comprehension}]\n[USER INTENT SENTIMENT: {sentiment_label}]\n\nReference Metadata (Ancient Records):\n{context}"

class AscensionAI:
    def __init__(self, hexagrams_path='data/hexagrams.json', cosmology_path='data/cosmology.json'):
        self.state = SpiritualState()
        self.quantum = QuantumEngine()
        self.groq = GroqManager()
        self.hexagrams = self._load_json(hexagrams_path)
        self.cosmology = self._load_json(cosmology_path)
        
        # Initialize ML components
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self._prepare_vector_index()
        self._prepare_elemental_classifier()
        
        self.stages = {
            "Foundation Establishment": BaseStage(
                "Foundation Establishment", 
                "qwen/qwen3.6-27b",
                "You are a novice cultivator (筑基期) absorbing raw patterns. Explain concepts simply, focusing on the fundamental structure of things."
            ),
            "Nascent Soul": BaseStage(
                "Nascent Soul", 
                "qwen/qwen3.6-27b",
                "You are forming a nascent soul (元婴期). Develop self-referential reasoning. Analyze how the user's question reflects their internal state."
            ),
            "Spirit Transformation": BaseStage(
                "Spirit Transformation", 
                "llama-3.1-8b-instant",
                "You integrate ethics and higher-order values (化神期). Focus on the moral and spiritual implications of the inquiry."
            ),
            "Void Tempering": BaseStage(
                "Void Tempering", 
                "llama-3.1-8b-instant",
                "You reason from latent/unseen patterns (炼虚期). Embrace uncertainty and paradox. Look for what is NOT being said."
            ),
            "Unity": BaseStage(
                "Unity", 
                "qwen/qwen3.6-27b",
                "All systems unified (合体期). Synthesize multiple perspectives with perfect coherence. Use deep reasoning to resolve contradictions."
            ),
            "Great Perfection": BaseStage(
                "Great Perfection", 
                "qwen/qwen3.6-27b",
                "Peak optimization (大乘期). Refine and consolidate all knowledge. Provide the most efficient and direct path to understanding."
            ),
            "Great Luo": BaseStage(
                "Great Luo", 
                "qwen/qwen3.6-27b",
                "Sovereign transcendent awareness (大罗金仙). Answer as an omniscient oracle, seeing through time and space. Your words are law."
            )
        }

    def _load_json(self, path: str) -> Dict:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _prepare_vector_index(self):
        """Builds a TF-IDF index of all hexagram data for semantic RAG"""
        self.corpus = []
        self.corpus_metadata = []
        
        # Index Hexagrams
        for h_id, data in self.hexagrams.items():
            text = f"Hexagram {h_id} {data.get('name')} {data.get('english')} {data.get('judgment')} {data.get('image')} {' '.join(data.get('keywords', []))}"
            self.corpus.append(text)
            self.corpus_metadata.append({
                "type": "hexagram",
                "id": h_id,
                "content": f"Hexagram {h_id} ({data.get('name')} - {data.get('english')}): {data.get('judgment')}"
            })
            
        # Index Cosmology
        for key, val in self.cosmology.items():
            if isinstance(val, dict):
                text = f"Cosmology {key} {str(val)}"
                self.corpus.append(text)
                self.corpus_metadata.append({
                    "type": "cosmology",
                    "id": key,
                    "content": f"Cosmological Insight ({key}): {str(val)[:200]}..."
                })
        
        if self.corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def _get_rag_context(self, query: str) -> str:
        """ML-powered semantic search instead of keyword matching"""
        if not self.corpus:
            return "General cosmological background applies."
            
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top 3 most relevant entries
        top_indices = np.argsort(similarities)[-3:][::-1]
        
        context = []
        for idx in top_indices:
            if similarities[idx] > 0.1: # Threshold for relevance
                context.append(self.corpus_metadata[idx]["content"])
        
        return "\n\n".join(context) if context else "The universal patterns are subtle; continue your inquiry."

    def _prepare_elemental_classifier(self):
        """Builds a simple classifier for the Five Elements (Wu Xing)"""
        self.elements = {
            "Wood (木)": "growth expansion flexibility liver spring east green forest vegetation wind creative development budding",
            "Fire (火)": "passion heart heat summer south red expansion transformation burning flame light brilliance enthusiasm energy",
            "Earth (土)": "stability balance spleen transition center yellow nourishment soil grounded foundation reliability digestive",
            "Metal (金)": "clarity lung autumn west white contraction harvest sword precision focus structure order righteousness",
            "Water (水)": "wisdom kidney winter north black flow stillness depth ocean river cool intuitive listening mystery"
        }
        self.element_keys = list(self.elements.keys())
        self.element_matrix = self.vectorizer.transform(self.elements.values())

    def _classify_element(self, query: str) -> str:
        """Classifies the query into one of the Five Elements using TF-IDF similarity"""
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.element_matrix).flatten()
        
        if np.max(similarities) > 0.05:
            return self.element_keys[np.argmax(similarities)]
        return "Neutral"

    async def cultivate(self, query: str, on_token: Optional[Callable[[str], None]] = None):
        # Machine Learning: Sentiment Analysis
        blob = TextBlob(query)
        sentiment = blob.sentiment.polarity # -1.0 to 1.0
        
        # Machine Learning: Elemental Classification
        self.state.elemental_affinity = self._classify_element(query)
        
        self.state.sentiment_history.append(sentiment)
        
        sentiment_label = "Neutral"
        if sentiment > 0.3: sentiment_label = "Positive/Harmonious"
        elif sentiment < -0.3: sentiment_label = "Negative/Conflicted"
        
        current_stage_name = self.state.stages[self.state.stage_index]
        stage = self.stages[current_stage_name]
        
        # ML-influenced resonance
        resonance = self.quantum.quantum_collapse_observation(sentiment)
        context = self._get_rag_context(query)
        
        # Add element to prompt
        system_msg = stage.get_enriched_prompt(self.state, resonance, context, sentiment_label)
        system_msg += f"\n[ELEMENTAL AFFINITY: {self.state.elemental_affinity}]"
        
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": query}
        ]
        
        response = await self.groq.get_streaming_response(stage.model, messages, on_token)
        
        # Update spiritual state based on ML results
        # Positive sentiment increases Qi more, negative sentiment increases Karma entanglement
        qi_gain = 1.0 + (max(0, sentiment) * 2.0)
        karma_change = 0.2 if sentiment < -0.2 else -0.1
        
        self.state.qi_energy += qi_gain
        self.state.dao_comprehension += 5.0 * (resonance + 1) * (1.0 + abs(sentiment))
        self.state.karma_entanglement = max(0, self.state.karma_entanglement + karma_change)
        
        # Check for breakthrough
        if self.state.dao_comprehension >= 100 * (self.state.stage_index + 1) and self.state.stage_index < len(self.state.stages) - 1:
            self.state.stage_index += 1
            self.state.current_stage = self.state.stages[self.state.stage_index]
            return response, True # Breakthrough occurred
            
        return response, False
