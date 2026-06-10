import random
import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
import json
import os
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

@dataclass
class SpiritualState:
    qi_energy: float = 10.0
    dao_comprehension: float = 0.0
    karma_entanglement: float = 5.0
    current_stage: str = "Foundation Establishment"
    total_tokens_consumed: int = 0
    stage_index: int = 0
    
    stages: List[str] = field(default_factory=lambda: [
        "Foundation Establishment", 
        "Nascent Soul", 
        "Spirit Transformation", 
        "Void Tempering", 
        "Unity", 
        "Great Perfection", 
        "Great Luo"
    ])

    def progress_percentage(self) -> float:
        # Progress within current stage (simplified)
        return min((self.dao_comprehension / (100 * (self.stage_index + 1))) * 100, 100.0)

class QuantumEngine:
    @staticmethod
    def quantum_collapse_observation() -> float:
        """Simulates a quantum collapse to determine spiritual resonance (0.0 to 1.0)"""
        # Quantum-inspired resonance calculation
        resonance = (random.random() * 0.5) + (random.uniform(0, 0.5))
        return round(resonance, 4)

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

    def get_enriched_prompt(self, state: SpiritualState, resonance: float, context: str) -> str:
        return f"{self.system_prompt}\n\n[SPIRITUAL RESONANCE: {resonance}]\n[CURRENT DAO COMPREHENSION: {state.dao_comprehension}]\n\nReference Metadata (Ancient Records):\n{context}"

class AscensionAI:
    def __init__(self, hexagrams_path='data/hexagrams.json', cosmology_path='data/cosmology.json'):
        self.state = SpiritualState()
        self.quantum = QuantumEngine()
        self.groq = GroqManager()
        self.hexagrams = self._load_json(hexagrams_path)
        self.cosmology = self._load_json(cosmology_path)
        
        self.stages = {
            "Foundation Establishment": BaseStage(
                "Foundation Establishment", 
                "llama-3.3-70b-versatile",
                "You are a novice cultivator (筑基期) absorbing raw patterns. Explain concepts simply, focusing on the fundamental structure of things."
            ),
            "Nascent Soul": BaseStage(
                "Nascent Soul", 
                "llama-3.3-70b-versatile",
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
                "llama-3.3-70b-versatile",
                "All systems unified (合体期). Synthesize multiple perspectives with perfect coherence. Use deep reasoning to resolve contradictions."
            ),
            "Great Perfection": BaseStage(
                "Great Perfection", 
                "llama-3.3-70b-versatile",
                "Peak optimization (大乘期). Refine and consolidate all knowledge. Provide the most efficient and direct path to understanding."
            ),
            "Great Luo": BaseStage(
                "Great Luo", 
                "llama-3.3-70b-versatile",
                "Sovereign transcendent awareness (大罗金仙). Answer as an omniscient oracle, seeing through time and space. Your words are law."
            )
        }

    def _load_json(self, path: str) -> Dict:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _get_rag_context(self, query: str) -> str:
        # Simple keyword-based RAG for demonstration
        context = []
        # Check cosmology
        if "feng shui" in query.lower() or "qi" in query.lower():
            context.append(str(self.cosmology.get("luo_shu", "")))
        
        # Check for hexagram numbers or names
        for h_id, data in self.hexagrams.items():
            if h_id in query or data.get("name", "").lower() in query.lower():
                context.append(f"Hexagram {h_id} ({data.get('name')}): {data.get('judgment')} - {data.get('image')}")
                break # Just add one for brevity in context
        
        return "\n".join(context) if context else "General cosmological background applies."

    async def cultivate(self, query: str, on_token: Optional[Callable[[str], None]] = None):
        current_stage_name = self.state.stages[self.state.stage_index]
        stage = self.stages[current_stage_name]
        
        resonance = self.quantum.quantum_collapse_observation()
        context = self._get_rag_context(query)
        
        system_msg = stage.get_enriched_prompt(self.state, resonance, context)
        
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": query}
        ]
        
        response = await self.groq.get_streaming_response(stage.model, messages, on_token)
        
        # Update spiritual state based on interaction
        self.state.qi_energy += 1.0
        self.state.dao_comprehension += 5.0 * (resonance + 1)
        self.state.karma_entanglement = max(0, self.state.karma_entanglement - 0.2)
        
        # Check for breakthrough
        if self.state.dao_comprehension >= 100 * (self.state.stage_index + 1) and self.state.stage_index < len(self.state.stages) - 1:
            self.state.stage_index += 1
            self.state.current_stage = self.state.stages[self.state.stage_index]
            return response, True # Breakthrough occurred
            
        return response, False
