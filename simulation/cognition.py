from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ThoughtType(Enum):
    # Basic thoughts
    OBSERVATION = "observation"
    QUESTION = "question"
    HYPOTHESIS = "hypothesis"
    CONCLUSION = "conclusion"
    
    # Complex thoughts
    PHILOSOPHICAL = "philosophical"
    SCIENTIFIC = "scientific"
    RELIGIOUS = "religious"
    MORAL = "moral"
    CULTURAL = "cultural"
    
    # Social thoughts
    EMPATHY = "empathy"
    JUDGMENT = "judgment"
    TRUST = "trust"
    LOYALTY = "loyalty"
    
    # Creative thoughts
    ARTISTIC = "artistic"
    MUSICAL = "musical"
    LITERARY = "literary"
    INVENTIVE = "inventive"

class CognitiveState(Enum):
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    EMOTIONAL = "emotional"
    RATIONAL = "rational"
    TIRED = "tired"
    ALERT = "alert"

@dataclass
class Memory:
    event: str
    importance: float  # 0-1 scale
    emotional_impact: float  # 0-1 scale
    timestamp: float
    context: Dict[str, float]  # Contextual information
    associations: Set[str]  # Associated concepts/events

@dataclass
class Thought:
    type: ThoughtType
    content: str
    confidence: float  # 0-1 scale
    source: str  # What triggered this thought
    timestamp: datetime
    associated_memories: List[str] = field(default_factory=list)
    associated_concepts: Set[str] = field(default_factory=set)
    emotional_impact: float = 0.0
    philosophical_impact: float = 0.0
    social_impact: float = 0.0
    cultural_impact: float = 0.0

@dataclass
class Decision:
    action: str
    reasoning: str
    confidence: float  # 0-1 scale
    alternatives: List[str]
    expected_outcomes: Dict[str, float]
    timestamp: float

class BeliefSystem:
    def __init__(self):
        self.beliefs: Dict[str, float] = {}  # belief -> confidence
        self.moral_values: Dict[str, float] = {}  # value -> strength
        self.cultural_norms: Dict[str, float] = {}  # norm -> adherence
        self.religious_beliefs: Dict[str, float] = {}  # belief -> faith
        self.scientific_theories: Dict[str, float] = {}  # theory -> confidence
        
    def update_beliefs(self, thought: Thought, agent_state: Dict):
        """Update beliefs based on new thoughts and experiences."""
        if thought.type == ThoughtType.CONCLUSION:
            self.beliefs[thought.content] = thought.confidence
            
        elif thought.type == ThoughtType.MORAL:
            self.moral_values[thought.content] = thought.confidence
            
        elif thought.type == ThoughtType.CULTURAL:
            self.cultural_norms[thought.content] = thought.confidence
            
        elif thought.type == ThoughtType.RELIGIOUS:
            self.religious_beliefs[thought.content] = thought.confidence
            
        elif thought.type == ThoughtType.SCIENTIFIC:
            self.scientific_theories[thought.content] = thought.confidence
            
    def get_belief_summary(self) -> Dict:
        """Get a summary of current beliefs."""
        return {
            "beliefs": self.beliefs,
            "moral_values": self.moral_values,
            "cultural_norms": self.cultural_norms,
            "religious_beliefs": self.religious_beliefs,
            "scientific_theories": self.scientific_theories
        }

class CognitiveSystem:
    def __init__(self):
        self.memories: List[Memory] = []
        self.thoughts: List[Thought] = []
        self.decisions: List[Decision] = []
        self.current_state = CognitiveState.FOCUSED
        self.attention_level = 1.0  # 0-1 scale
        self.creativity_level = 0.5  # 0-1 scale
        self.analytical_level = 0.5  # 0-1 scale
        self.learning_rate = 0.5  # 0-1 scale
        self.belief_system = BeliefSystem()
        self.understanding_levels: Dict[str, float] = {}
        self.creative_works: Dict[str, Dict] = {}
        self.cultural_contributions: Dict[str, Dict] = {}
        self._initialize_cognitive_state()
        
    def _initialize_cognitive_state(self) -> None:
        """Initialize cognitive state with random variations"""
        self.attention_level = random.uniform(0.7, 1.0)
        self.creativity_level = random.uniform(0.3, 0.7)
        self.analytical_level = random.uniform(0.3, 0.7)
        self.learning_rate = random.uniform(0.4, 0.6)
        
    def add_memory(self, event: str, importance: float, emotional_impact: float,
                  context: Dict[str, float], associations: Set[str]) -> None:
        """Add a new memory"""
        memory = Memory(
            event=event,
            importance=importance,
            emotional_impact=emotional_impact,
            timestamp=0.0,  # Set to current time
            context=context,
            associations=associations
        )
        
        # Add to memories and maintain memory limit
        self.memories.append(memory)
        if len(self.memories) > 1000:  # Limit total memories
            self.memories.sort(key=lambda m: m.importance)
            self.memories = self.memories[-1000:]
            
        logger.info(f"Added memory: {event}")
        
    def add_thought(self, content: str, thought_type: str, priority: float,
                   emotional_tone: float) -> None:
        """Add a new thought"""
        thought = Thought(
            type=thought_type,
            content=content,
            confidence=0.0,  # Confidence will be updated later
            source="",  # Source will be updated later
            timestamp=datetime.now(),
            emotional_impact=emotional_tone,
            associated_memories=[],
            associated_concepts=set()
        )
        
        # Add to thoughts and maintain thought limit
        self.thoughts.append(thought)
        if len(self.thoughts) > 100:  # Limit active thoughts
            self.thoughts.sort(key=lambda t: t.confidence)
            self.thoughts = self.thoughts[-100:]
            
        logger.info(f"Added thought: {content}")
        
    def make_decision(self, action: str, reasoning: str, confidence: float,
                     alternatives: List[str], expected_outcomes: Dict[str, float]) -> None:
        """Record a decision"""
        decision = Decision(
            action=action,
            reasoning=reasoning,
            confidence=confidence,
            alternatives=alternatives,
            expected_outcomes=expected_outcomes,
            timestamp=0.0  # Set to current time
        )
        
        # Add to decisions and maintain decision history
        self.decisions.append(decision)
        if len(self.decisions) > 100:  # Limit decision history
            self.decisions = self.decisions[-100:]
            
        logger.info(f"Made decision: {action}")
        
    def update_cognitive_state(self, time_delta: float) -> None:
        """Update cognitive state based on time and conditions"""
        # Update attention level
        self.attention_level = max(0.0, min(1.0,
            self.attention_level - time_delta * 0.1))  # Natural decay
            
        # Update creativity and analytical levels
        self.creativity_level = max(0.0, min(1.0,
            self.creativity_level + random.uniform(-0.1, 0.1) * time_delta))
        self.analytical_level = max(0.0, min(1.0,
            self.analytical_level + random.uniform(-0.1, 0.1) * time_delta))
            
        # Determine current cognitive state
        if self.attention_level < 0.3:
            self.current_state = CognitiveState.DISTRACTED
        elif self.creativity_level > 0.7:
            self.current_state = CognitiveState.CREATIVE
        elif self.analytical_level > 0.7:
            self.current_state = CognitiveState.ANALYTICAL
        else:
            self.current_state = CognitiveState.FOCUSED
            
    def recall_memory(self, query: str) -> List[Memory]:
        """Recall memories based on a query"""
        # Simple keyword matching for now
        return [
            memory for memory in self.memories
            if query.lower() in memory.event.lower() or
            any(query.lower() in assoc.lower() for assoc in memory.associations)
        ]
        
    def get_recent_thoughts(self, count: int = 10) -> List[Thought]:
        """Get most recent thoughts"""
        return sorted(self.thoughts, key=lambda t: t.timestamp)[-count:]
        
    def get_recent_decisions(self, count: int = 10) -> List[Decision]:
        """Get most recent decisions"""
        return sorted(self.decisions, key=lambda d: d.timestamp)[-count:]
        
    def get_cognitive_state(self) -> Dict[str, float]:
        """Get current cognitive state metrics"""
        return {
            "attention": self.attention_level,
            "creativity": self.creativity_level,
            "analytical": self.analytical_level,
            "learning": self.learning_rate
        }
        
    def process_information(self, information: str, importance: float) -> None:
        """Process new information and update cognitive state"""
        # Add as memory
        self.add_memory(
            event=information,
            importance=importance,
            emotional_impact=0.5,  # Neutral emotional impact
            context={"source": "observation"},
            associations=set()
        )
        
        # Generate thoughts based on information
        if importance > 0.7:
            self.add_thought(
                content=f"Important observation: {information}",
                thought_type="observation",
                priority=importance,
                emotional_tone=0.0
            )
            
    def learn_from_experience(self, experience: str, success: bool) -> None:
        """Learn from an experience and update learning rate"""
        # Adjust learning rate based on success
        if success:
            self.learning_rate = min(1.0, self.learning_rate + 0.1)
        else:
            self.learning_rate = max(0.0, self.learning_rate - 0.05)
            
        # Add as memory with appropriate importance
        self.add_memory(
            event=experience,
            importance=0.8 if success else 0.6,
            emotional_impact=0.7 if success else -0.3,
            context={"success": success},
            associations={"learning", "experience"}
        )
        
    def generate_thoughts(self, context: Dict[str, float]) -> List[Thought]:
        """Generate new thoughts based on current state and context"""
        thoughts = []
        
        # Generate thoughts based on cognitive state
        if self.current_state == CognitiveState.CREATIVE:
            thoughts.append(Thought(
                type=ThoughtType.INVENTIVE,
                content="Exploring new possibilities...",
                confidence=0.7,
                source="",
                timestamp=datetime.now(),
                emotional_impact=0.5,
                associated_memories=[],
                associated_concepts=set()
            ))
        elif self.current_state == CognitiveState.ANALYTICAL:
            thoughts.append(Thought(
                type=ThoughtType.OBSERVATION,
                content="Analyzing current situation...",
                confidence=0.8,
                source="",
                timestamp=datetime.now(),
                emotional_impact=0.0,
                associated_memories=[],
                associated_concepts=set()
            ))
            
        # Add thoughts based on context
        for key, value in context.items():
            if value > 0.7:
                thoughts.append(Thought(
                    type=ThoughtType.OBSERVATION,
                    content=f"Noticing significant {key}...",
                    confidence=value,
                    source="",
                    timestamp=datetime.now(),
                    emotional_impact=0.3,
                    associated_memories=[],
                    associated_concepts=set()
                ))
                
        return thoughts
        
    def process_experience(self, event: str, context: Dict, agent_state: Dict) -> List[Thought]:
        """Process a new experience and generate thoughts."""
        new_thoughts = []
        
        # Get agent's current state
        memories = agent_state.get("memories", [])
        discovered_concepts = agent_state.get("discovered_concepts", set())
        emotional_state = agent_state.get("emotions", {}).get("current_emotions", {})
        
        # Generate thoughts based on event type
        if "death" in event.lower():
            thoughts = self._process_death_event(event, context, emotional_state)
            new_thoughts.extend(thoughts)
        elif "birth" in event.lower():
            thoughts = self._process_birth_event(event, context, emotional_state)
            new_thoughts.extend(thoughts)
        elif "discovery" in event.lower():
            thoughts = self._process_discovery_event(event, context, emotional_state)
            new_thoughts.extend(thoughts)
        elif "social" in event.lower():
            thoughts = self._process_social_event(event, context, emotional_state)
            new_thoughts.extend(thoughts)
            
        # Update belief system
        for thought in new_thoughts:
            self.belief_system.update_beliefs(thought, agent_state)
            
        # Update thought history
        self.thoughts.extend(new_thoughts)
        
        # Limit history size
        if len(self.thoughts) > 1000:
            self.thoughts = self.thoughts[-1000:]
            
        return new_thoughts
        
    def _process_death_event(self, event: str, context: Dict, 
                           emotional_state: Dict) -> List[Thought]:
        """Process thoughts about death and mortality."""
        thoughts = []
        
        # Basic observations
        thoughts.append(Thought(
            type=ThoughtType.OBSERVATION,
            content="Life ends with death",
            confidence=0.9,
            source=event,
            timestamp=datetime.now(),
            emotional_impact=0.8,
            associated_memories=[],
            associated_concepts=set()
        ))
        
        # Philosophical questions
        if random.random() < 0.7:  # 70% chance to question
            thoughts.append(Thought(
                type=ThoughtType.PHILOSOPHICAL,
                content="What happens after death?",
                confidence=0.5,
                source=event,
                timestamp=datetime.now(),
                emotional_impact=0.9,
                associated_memories=[],
                associated_concepts=set()
            ))
            
        # Religious thoughts
        if random.random() < 0.5:  # 50% chance
            thoughts.append(Thought(
                type=ThoughtType.RELIGIOUS,
                content="Perhaps there is something beyond death",
                confidence=0.4,
                source=event,
                timestamp=datetime.now(),
                emotional_impact=0.7,
                associated_memories=[],
                associated_concepts=set()
            ))
            
        return thoughts
        
    def _process_birth_event(self, event: str, context: Dict,
                           emotional_state: Dict) -> List[Thought]:
        """Process thoughts about birth and new life."""
        thoughts = []
        
        # Basic observations
        thoughts.append(Thought(
            type=ThoughtType.OBSERVATION,
            content="New life begins with birth",
            confidence=0.9,
            source=event,
            timestamp=datetime.now(),
            emotional_impact=0.7,
            associated_memories=[],
            associated_concepts=set()
        ))
        
        # Scientific thoughts
        if random.random() < 0.6:  # 60% chance
            thoughts.append(Thought(
                type=ThoughtType.SCIENTIFIC,
                content="Life emerges from life",
                confidence=0.8,
                source=event,
                timestamp=datetime.now(),
                emotional_impact=0.8,
                associated_memories=[],
                associated_concepts=set()
            ))
            
        # Cultural thoughts
        if random.random() < 0.5:  # 50% chance
            thoughts.append(Thought(
                type=ThoughtType.CULTURAL,
                content="Birth is a sacred event",
                confidence=0.6,
                source=event,
                timestamp=datetime.now(),
                emotional_impact=0.7,
                associated_memories=[],
                associated_concepts=set()
            ))
            
        return thoughts
        
    def _process_discovery_event(self, event: str, context: Dict,
                               emotional_state: Dict) -> List[Thought]:
        """Process thoughts about discoveries and new knowledge."""
        thoughts = []
        
        # Scientific thoughts
        thoughts.append(Thought(
            type=ThoughtType.SCIENTIFIC,
            content=f"Discovered {context.get('discovery', 'something new')}",
            confidence=0.8,
            source=event,
            timestamp=datetime.now(),
            emotional_impact=0.8,
            associated_memories=[],
            associated_concepts=set()
        ))
        
        # Creative thoughts
        if random.random() < 0.4:  # 40% chance
            thoughts.append(Thought(
                type=ThoughtType.INVENTIVE,
                content="This could be used to create something new",
                confidence=0.6,
                source=event,
                timestamp=datetime.now(),
                emotional_impact=0.7,
                associated_memories=[],
                associated_concepts=set()
            ))
            
        return thoughts
        
    def _process_social_event(self, event: str, context: Dict,
                            emotional_state: Dict) -> List[Thought]:
        """Process thoughts about social interactions."""
        thoughts = []
        
        # Empathetic thoughts
        if "sadness" in emotional_state or "joy" in emotional_state:
            thoughts.append(Thought(
                type=ThoughtType.EMPATHY,
                content="I understand how others feel",
                confidence=0.7,
                source=event,
                timestamp=datetime.now(),
                emotional_impact=0.8,
                associated_memories=[],
                associated_concepts=set()
            ))
            
        # Cultural thoughts
        if random.random() < 0.5:  # 50% chance
            thoughts.append(Thought(
                type=ThoughtType.CULTURAL,
                content="Our way of life is unique",
                confidence=0.6,
                source=event,
                timestamp=datetime.now(),
                emotional_impact=0.7,
                associated_memories=[],
                associated_concepts=set()
            ))
            
        return thoughts
        
    def generate_creative_work(self, thought: Thought) -> Optional[Dict]:
        """Generate a creative work based on a thought."""
        if thought.type in [ThoughtType.ARTISTIC, ThoughtType.MUSICAL, 
                          ThoughtType.LITERARY, ThoughtType.INVENTIVE]:
            work = {
                "type": thought.type.value,
                "content": thought.content,
                "inspiration": thought.source,
                "emotional_impact": thought.emotional_impact,
                "cultural_impact": thought.cultural_impact,
                "timestamp": datetime.now().isoformat()
            }
            
            self.creative_works[thought.content] = work
            return work
            
        return None
        
    def generate_cultural_contribution(self, thought: Thought) -> Optional[Dict]:
        """Generate a cultural contribution based on a thought."""
        if thought.type in [ThoughtType.CULTURAL, ThoughtType.RELIGIOUS, 
                          ThoughtType.MORAL]:
            contribution = {
                "type": thought.type.value,
                "content": thought.content,
                "inspiration": thought.source,
                "cultural_impact": thought.cultural_impact,
                "social_impact": thought.social_impact,
                "timestamp": datetime.now().isoformat()
            }
            
            self.cultural_contributions[thought.content] = contribution
            return contribution
            
        return None
        
    def to_dict(self) -> Dict:
        """Convert cognitive system state to dictionary for serialization."""
        return {
            "thoughts": [
                {
                    "type": t.type.value,
                    "content": t.content,
                    "confidence": t.confidence,
                    "source": t.source,
                    "timestamp": t.timestamp.isoformat(),
                    "associated_memories": t.associated_memories,
                    "associated_concepts": list(t.associated_concepts),
                    "emotional_impact": t.emotional_impact,
                    "philosophical_impact": t.philosophical_impact,
                    "social_impact": t.social_impact,
                    "cultural_impact": t.cultural_impact
                }
                for t in self.thoughts
            ],
            "belief_system": self.belief_system.get_belief_summary(),
            "understanding_levels": self.understanding_levels,
            "creative_works": self.creative_works,
            "cultural_contributions": self.cultural_contributions
        } 