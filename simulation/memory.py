from typing import Dict, List, Set
from datetime import datetime
import json

class Memory:
    def __init__(self):
        self.memories: List[Dict] = []
        self.concepts: Set[str] = set()
        self.animal_interactions: List[Dict] = []
        self.domesticated_animals: List[str] = []
        self.max_memories = 1000  # Maximum number of memories to store
    
    def add_memory(self, event: str, importance: float, context: Dict = None):
        """Add a new memory"""
        memory = {
            "event": event,
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "concepts": set()
        }
        
        # Extract concepts from event and context
        self._extract_concepts(memory)
        
        # Add to memories list
        self.memories.append(memory)
        
        # Keep only most important memories if over limit
        if len(self.memories) > self.max_memories:
            self.memories.sort(key=lambda x: x["importance"], reverse=True)
            self.memories = self.memories[:self.max_memories]
    
    def _extract_concepts(self, memory: Dict):
        """Extract concepts from memory text"""
        # Simple concept extraction (can be enhanced with NLP)
        words = memory["event"].lower().split()
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 characters
                self.concepts.add(word)
                memory["concepts"].add(word)
    
    def get_recent_memories(self, count: int = 10) -> List[Dict]:
        """Get most recent memories"""
        return sorted(
            self.memories,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:count]
    
    def get_important_memories(self, count: int = 10) -> List[Dict]:
        """Get most important memories"""
        return sorted(
            self.memories,
            key=lambda x: x["importance"],
            reverse=True
        )[:count]
    
    def get_memories_by_concept(self, concept: str) -> List[Dict]:
        """Get memories containing a specific concept"""
        return [
            memory for memory in self.memories
            if concept in memory["concepts"]
        ]
    
    def add_animal_interaction(self, animal_id: str, interaction_type: str, success: bool):
        """Record an interaction with an animal"""
        interaction = {
            "animal_id": animal_id,
            "type": interaction_type,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        self.animal_interactions.append(interaction)
    
    def add_domesticated_animal(self, animal_id: str):
        """Record a domesticated animal"""
        if animal_id not in self.domesticated_animals:
            self.domesticated_animals.append(animal_id)
    
    def to_dict(self) -> Dict:
        """Convert memory to dictionary"""
        return {
            "memories": self.memories,
            "concepts": list(self.concepts),
            "animal_interactions": self.animal_interactions,
            "domesticated_animals": self.domesticated_animals
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Memory':
        """Create memory from dictionary"""
        memory = cls()
        memory.memories = data.get("memories", [])
        memory.concepts = set(data.get("concepts", []))
        memory.animal_interactions = data.get("animal_interactions", [])
        memory.domesticated_animals = data.get("domesticated_animals", [])
        return memory 