from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import random
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class BeliefType(Enum):
    RELIGIOUS = "religious"
    MORAL = "moral"
    POLITICAL = "political"
    SCIENTIFIC = "scientific"
    PHILOSOPHICAL = "philosophical"
    CULTURAL = "cultural"

@dataclass
class Belief:
    type: BeliefType
    content: str
    strength: float  # 0.0 to 1.0
    source: str
    formation_time: float
    supporting_evidence: List[str] = field(default_factory=list)
    opposing_evidence: List[str] = field(default_factory=list)
    related_beliefs: Set[str] = field(default_factory=set)

@dataclass
class Value:
    name: str
    importance: float  # 0.0 to 1.0
    description: str
    related_beliefs: Set[str] = field(default_factory=set)
    conflicts_with: Set[str] = field(default_factory=set)

@dataclass
class Philosophy:
    # Core beliefs
    purpose: str = "survive"  # Current life purpose
    values: List[str] = None  # Core values
    beliefs: Dict[str, float] = None  # Beliefs and their strength (0-1)
    
    # Knowledge
    concepts: Set[str] = None  # Known concepts
    theories: Dict[str, float] = None  # Theories and confidence (0-1)
    questions: List[str] = None  # Philosophical questions
    
    # Worldview
    worldview: str = "neutral"  # Current worldview
    morality: Dict[str, float] = None  # Moral principles
    ethics: Dict[str, float] = None  # Ethical principles
    
    # New additions from the code block
    spirituality: float = 0.5  # 0 = materialist, 1 = spiritual
    individualism: float = 0.5  # 0 = collectivist, 1 = individualist
    tradition: float = 0.5  # 0 = progressive, 1 = traditional
    authority: float = 0.5  # 0 = anarchist, 1 = authoritarian
    
    # Worldview aspects
    nature_relationship: float = 0.5  # 0 = exploitative, 1 = harmonious
    technology_attitude: float = 0.5  # 0 = technophobic, 1 = technophilic
    change_attitude: float = 0.5  # 0 = conservative, 1 = revolutionary
    knowledge_attitude: float = 0.5  # 0 = skeptical, 1 = trusting
    
    # Philosophical concepts
    free_will: float = 0.5  # 0 = deterministic, 1 = free will
    meaning_of_life: float = 0.5  # 0 = nihilistic, 1 = purposeful
    human_nature: float = 0.5  # 0 = pessimistic, 1 = optimistic
    truth_attitude: float = 0.5  # 0 = relativistic, 1 = absolutist
    
    # Philosophical influences
    influences: List[Dict] = field(default_factory=list)
    original_thoughts: List[Dict] = field(default_factory=list)
    contradictions: List[Tuple[str, str]] = field(default_factory=list)
    
    # Philosophical development
    complexity: float = 0.3  # How complex/deep the philosophy is
    consistency: float = 0.7  # How internally consistent the philosophy is
    openness: float = 0.5  # How open to new ideas
    
    def __init__(self):
        """Initialize philosophy with basic state."""
        self.purpose = "survive"
        self.values = ["survival", "knowledge", "growth"]
        self.beliefs = {
            "existence": 0.5,
            "purpose": 0.5,
            "morality": 0.5
        }
        self.concepts = set()
        self.theories = {}
        self.questions = []
        self.worldview = "neutral"
        self.morality = {
            "good": 0.5,
            "evil": 0.5,
            "right": 0.5,
            "wrong": 0.5
        }
        self.ethics = {
            "honesty": 0.5,
            "fairness": 0.5,
            "compassion": 0.5,
            "justice": 0.5
        }
        
    def update(self, time_delta: float, experiences: List[Dict]):
        """Update philosophy based on experiences and time"""
        # Process new experiences
        for experience in experiences:
            self._process_experience(experience)
        
        # Evolve philosophy over time
        self._evolve_philosophy(time_delta)
        
        # Check for contradictions
        self._check_contradictions()
        
        # Update complexity and consistency
        self._update_metrics()
    
    def _process_experience(self, experience: Dict):
        """Process a new experience and update philosophy accordingly"""
        # Extract relevant aspects from experience
        event_type = experience.get("type", "")
        impact = experience.get("impact", 0.0)
        context = experience.get("context", {})
        
        # Update relevant beliefs based on experience
        if event_type == "moral_decision":
            self.morality = self._adjust_belief(self.morality, impact)
        elif event_type == "spiritual_experience":
            self.spirituality = self._adjust_belief(self.spirituality, impact)
        elif event_type == "social_interaction":
            self.individualism = self._adjust_belief(self.individualism, impact)
        elif event_type == "technological_discovery":
            self.technology_attitude = self._adjust_belief(self.technology_attitude, impact)
        
        # Add to influences if significant
        if abs(impact) > 0.3:
            self.influences.append({
                "event": event_type,
                "impact": impact,
                "context": context
            })
    
    def _evolve_philosophy(self, time_delta: float):
        """Allow philosophy to evolve naturally over time"""
        # Small random changes to beliefs
        for belief in self._get_beliefs():
            current_value = getattr(self, belief)
            change = random.uniform(-0.01, 0.01) * time_delta
            setattr(self, belief, max(0.0, min(1.0, current_value + change)))
        
        # Increase complexity over time
        self.complexity = min(1.0, self.complexity + 0.001 * time_delta)
    
    def _check_contradictions(self):
        """Check for and resolve philosophical contradictions"""
        contradictions = []
        
        # Check for contradictions between related beliefs
        if abs(self.individualism - self.authority) > 0.7:
            contradictions.append(("individualism", "authority"))
        if abs(self.tradition - self.change_attitude) > 0.7:
            contradictions.append(("tradition", "change_attitude"))
        if abs(self.spirituality - self.technology_attitude) > 0.7:
            contradictions.append(("spirituality", "technology_attitude"))
        
        # Resolve contradictions by adjusting beliefs
        for belief1, belief2 in contradictions:
            val1 = getattr(self, belief1)
            val2 = getattr(self, belief2)
            avg = (val1 + val2) / 2
            setattr(self, belief1, avg)
            setattr(self, belief2, avg)
        
        self.contradictions = contradictions
    
    def _update_metrics(self):
        """Update complexity and consistency metrics"""
        # Calculate consistency based on contradictions
        self.consistency = max(0.0, 1.0 - len(self.contradictions) * 0.2)
        
        # Complexity increases with number of influences and original thoughts
        self.complexity = min(1.0, 0.3 + (len(self.influences) + len(self.original_thoughts)) * 0.05)
    
    def _adjust_belief(self, current_value: float, impact: float) -> float:
        """Adjust a belief value based on impact"""
        # More impact on beliefs when they're less extreme
        adjustment = impact * (1.0 - abs(current_value - 0.5) * 2)
        return max(0.0, min(1.0, current_value + adjustment))
    
    def _get_beliefs(self) -> List[str]:
        """Get list of all belief attributes"""
        return [
            "morality", "spirituality", "individualism", "tradition", "authority",
            "nature_relationship", "technology_attitude", "change_attitude", "knowledge_attitude",
            "free_will", "meaning_of_life", "human_nature", "truth_attitude"
        ]
    
    def get_philosophical_position(self) -> Dict:
        """Get a summary of the agent's philosophical position"""
        return {
            "core_beliefs": {
                "morality": self.morality,
                "spirituality": self.spirituality,
                "individualism": self.individualism,
                "tradition": self.tradition,
                "authority": self.authority
            },
            "worldview": {
                "nature_relationship": self.nature_relationship,
                "technology_attitude": self.technology_attitude,
                "change_attitude": self.change_attitude,
                "knowledge_attitude": self.knowledge_attitude
            },
            "philosophical_concepts": {
                "free_will": self.free_will,
                "meaning_of_life": self.meaning_of_life,
                "human_nature": self.human_nature,
                "truth_attitude": self.truth_attitude
            },
            "development": {
                "complexity": self.complexity,
                "consistency": self.consistency,
                "openness": self.openness
            }
        }
    
    def to_dict(self) -> Dict:
        """Convert philosophy to dictionary"""
        return {
            "purpose": self.purpose,
            "values": self.values,
            "beliefs": self.beliefs,
            "concepts": list(self.concepts),
            "theories": self.theories,
            "questions": self.questions,
            "worldview": self.worldview,
            "morality": self.morality,
            "ethics": self.ethics,
            "spirituality": self.spirituality,
            "individualism": self.individualism,
            "tradition": self.tradition,
            "authority": self.authority,
            "nature_relationship": self.nature_relationship,
            "technology_attitude": self.technology_attitude,
            "change_attitude": self.change_attitude,
            "knowledge_attitude": self.knowledge_attitude,
            "free_will": self.free_will,
            "meaning_of_life": self.meaning_of_life,
            "human_nature": self.human_nature,
            "truth_attitude": self.truth_attitude,
            "complexity": self.complexity,
            "consistency": self.consistency,
            "openness": self.openness,
            "influences": self.influences,
            "original_thoughts": self.original_thoughts,
            "contradictions": self.contradictions
        }
        
    def update_from_dict(self, data: Dict):
        """Update philosophy from saved data."""
        self.purpose = data.get("purpose", self.purpose)
        self.values = data.get("values", self.values)
        self.beliefs = data.get("beliefs", self.beliefs)
        self.concepts = set(data.get("concepts", []))
        self.theories = data.get("theories", self.theories)
        self.questions = data.get("questions", self.questions)
        self.worldview = data.get("worldview", self.worldview)
        self.morality = data.get("morality", self.morality)
        self.ethics = data.get("ethics", self.ethics)
        self.spirituality = data.get("spirituality", self.spirituality)
        self.individualism = data.get("individualism", self.individualism)
        self.tradition = data.get("tradition", self.tradition)
        self.authority = data.get("authority", self.authority)
        self.nature_relationship = data.get("nature_relationship", self.nature_relationship)
        self.technology_attitude = data.get("technology_attitude", self.technology_attitude)
        self.change_attitude = data.get("change_attitude", self.change_attitude)
        self.knowledge_attitude = data.get("knowledge_attitude", self.knowledge_attitude)
        self.free_will = data.get("free_will", self.free_will)
        self.meaning_of_life = data.get("meaning_of_life", self.meaning_of_life)
        self.human_nature = data.get("human_nature", self.human_nature)
        self.truth_attitude = data.get("truth_attitude", self.truth_attitude)
        self.complexity = data.get("complexity", self.complexity)
        self.consistency = data.get("consistency", self.consistency)
        self.openness = data.get("openness", self.openness)
        self.influences = data.get("influences", self.influences)
        self.original_thoughts = data.get("original_thoughts", self.original_thoughts)
        self.contradictions = data.get("contradictions", self.contradictions)

    def ponder_existence(self, context: Dict) -> Optional[Dict]:
        """Ponder philosophical questions and develop new insights."""
        # Extract context information
        memories = context.get("memories", [])
        discovered_concepts = context.get("discovered_concepts", set())
        understanding_levels = context.get("understanding_levels", {})
        current_question = context.get("current_question", "What is the meaning of life?")
        memory_context = context.get("context", {})
        
        # Add question to existential questions if new
        if current_question not in self.questions:
            self.questions.append(current_question)
            
        # Consider the question based on memories and understanding
        insights = []
        
        # Analyze memories for relevant insights
        for memory in memories:
            if memory.importance > 0.7:  # Focus on significant memories
                # Extract concepts from memory
                for concept in memory.concepts:
                    if concept in understanding_levels:
                        confidence = understanding_levels[concept]
                        if confidence > 0.7:  # Only use well-understood concepts
                            insights.append({
                                "concept": concept,
                                "confidence": confidence,
                                "source": "memory",
                                "memory": memory.event
                            })
                            
        # Consider philosophical implications
        if insights:
            # Develop new understanding
            new_understanding = {
                "question": current_question,
                "insights": insights,
                "confidence": sum(insight["confidence"] for insight in insights) / len(insights),
                "timestamp": datetime.now()
            }
            
            # Update philosophical concepts
            concept_key = f"understanding_{len(self.theories)}"
            self.theories[concept_key] = new_understanding
            
            # Update related beliefs
            if "meaning" in current_question.lower():
                self.beliefs["existence"] = min(1.0, self.beliefs["existence"] + 0.1)
            if "purpose" in current_question.lower():
                self.purpose = min(1.0, self.purpose + 0.1)
            if "happiness" in current_question.lower():
                self.beliefs["existence"] = min(1.0, self.beliefs["existence"] + 0.1)
            if "morality" in current_question.lower():
                self.morality["good"] = min(1.0, self.morality["good"] + 0.1)
            if "consciousness" in current_question.lower():
                self.beliefs["existence"] = min(1.0, self.beliefs["existence"] + 0.1)
                
            # Update wisdom based on new understanding
            self.theories[concept_key]["confidence"] = min(1.0, self.theories[concept_key]["confidence"] + 0.05)
            
            return new_understanding
            
        return None 