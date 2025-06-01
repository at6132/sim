from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import random
from datetime import datetime
import time

class EmotionType(Enum):
    # Basic emotions
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    
    # Social emotions
    LOVE = "love"
    HATE = "hate"
    JEALOUSY = "jealousy"
    PRIDE = "pride"
    SHAME = "shame"
    GUILT = "guilt"
    
    # Complex emotions
    NOSTALGIA = "nostalgia"
    HOPE = "hope"
    DESPAIR = "despair"
    WONDER = "wonder"
    AWE = "awe"
    LONELINESS = "loneliness"
    
    # Philosophical emotions
    EXISTENTIAL_DREAD = "existential_dread"
    TRANSCENDENCE = "transcendence"
    MEANING = "meaning"
    PURPOSE = "purpose"
    CONNECTION = "connection"
    SUICIDAL = "suicidal"  # New emotion type for suicidal tendencies
    TRUST = "trust"
    ANTICIPATION = "anticipation"

@dataclass
class Emotion:
    type: EmotionType
    intensity: float  # 0-1 scale
    source: str  # What triggered this emotion
    timestamp: datetime
    duration: float  # How long this emotion lasts
    associated_memories: List[str] = field(default_factory=list)
    associated_concepts: Set[str] = field(default_factory=set)
    target: Optional[str] = None
    context: Optional[str] = None

@dataclass
class EmotionSystem:
    def __init__(self):
        # Basic emotions (0-1 scale)
        self.happiness = 0.5
        self.sadness = 0.0
        self.anger = 0.0
        self.fear = 0.0
        self.surprise = 0.0
        self.disgust = 0.0
        
        # Complex emotions
        self.love = 0.0
        self.hate = 0.0
        self.anxiety = 0.0
        self.hope = 0.5
        self.pride = 0.0
        self.shame = 0.0
        
        # Emotional state
        self.stress = 0.0
        self.mood = 0.5  # Overall mood (-1 to 1)
        self.emotional_stability = 0.7
    
    def update(self, time_delta: float):
        """Update emotions over time"""
        # Emotions naturally decay towards neutral
        self._decay_emotions(time_delta)
        
        # Update mood based on current emotions
        self._update_mood()
        
        # Update stress based on negative emotions
        self._update_stress()
    
    def _decay_emotions(self, time_delta: float):
        """Decay emotions towards neutral state"""
        decay_rate = 0.1 * time_delta
        
        # Basic emotions
        self.happiness = max(0.0, self.happiness - decay_rate)
        self.sadness = max(0.0, self.sadness - decay_rate)
        self.anger = max(0.0, self.anger - decay_rate)
        self.fear = max(0.0, self.fear - decay_rate)
        self.surprise = max(0.0, self.surprise - decay_rate)
        self.disgust = max(0.0, self.disgust - decay_rate)
        
        # Complex emotions
        self.love = max(0.0, self.love - decay_rate * 0.5)
        self.hate = max(0.0, self.hate - decay_rate * 0.5)
        self.anxiety = max(0.0, self.anxiety - decay_rate)
        self.hope = max(0.0, self.hope - decay_rate * 0.5)
        self.pride = max(0.0, self.pride - decay_rate)
        self.shame = max(0.0, self.shame - decay_rate)
    
    def _update_mood(self):
        """Update overall mood based on current emotions"""
        positive = self.happiness + self.love + self.hope + self.pride
        negative = self.sadness + self.anger + self.fear + self.hate + self.anxiety + self.shame
        
        total = positive + negative
        if total > 0:
            self.mood = (positive - negative) / total
        else:
            self.mood = 0.0
    
    def _update_stress(self):
        """Update stress level based on negative emotions"""
        negative_emotions = (
            self.sadness + self.anger + self.fear + 
            self.anxiety + self.shame
        ) / 5.0
        
        self.stress = min(1.0, negative_emotions * (1.0 - self.emotional_stability))
    
    def trigger_emotion(self, emotion: str, intensity: float):
        """Trigger an emotion with given intensity"""
        if hasattr(self, emotion):
            current_value = getattr(self, emotion)
            setattr(self, emotion, min(1.0, current_value + intensity))
            
            # Update related emotions
            self._update_related_emotions(emotion, intensity)
    
    def _update_related_emotions(self, emotion: str, intensity: float):
        """Update emotions related to the triggered emotion"""
        related_emotions = {
            "happiness": ["sadness", "anger", "fear"],
            "sadness": ["happiness", "hope"],
            "anger": ["happiness", "love"],
            "fear": ["happiness", "hope"],
            "love": ["hate", "anger"],
            "hate": ["love", "happiness"],
            "anxiety": ["happiness", "hope"],
            "hope": ["anxiety", "fear"],
            "pride": ["shame"],
            "shame": ["pride", "happiness"]
        }
        
        if emotion in related_emotions:
            for related in related_emotions[emotion]:
                if hasattr(self, related):
                    current_value = getattr(self, related)
                    setattr(self, related, max(0.0, current_value - intensity * 0.5))
    
    def get_dominant_emotion(self) -> str:
        """Get the currently dominant emotion"""
        emotions = {
            "happiness": self.happiness,
            "sadness": self.sadness,
            "anger": self.anger,
            "fear": self.fear,
            "surprise": self.surprise,
            "disgust": self.disgust,
            "love": self.love,
            "hate": self.hate,
            "anxiety": self.anxiety,
            "hope": self.hope,
            "pride": self.pride,
            "shame": self.shame
        }
        
        return max(emotions.items(), key=lambda x: x[1])[0]
    
    def to_dict(self) -> Dict:
        """Convert emotions to dictionary"""
        return {
            "happiness": self.happiness,
            "sadness": self.sadness,
            "anger": self.anger,
            "fear": self.fear,
            "surprise": self.surprise,
            "disgust": self.disgust,
            "love": self.love,
            "hate": self.hate,
            "anxiety": self.anxiety,
            "hope": self.hope,
            "pride": self.pride,
            "shame": self.shame,
            "stress": self.stress,
            "mood": self.mood,
            "emotional_stability": self.emotional_stability
        }

    def process_experience(self, event: str, context: Dict, agent_state: Dict) -> List[Emotion]:
        """Process a new experience and generate appropriate emotions."""
        new_emotions = []
        
        # Get agent's current state
        memories = agent_state.get("memories", [])
        discovered_concepts = agent_state.get("discovered_concepts", set())
        understanding_levels = agent_state.get("understanding_levels", {})
        
        # Analyze event for emotional triggers
        triggers = self._analyze_emotional_triggers(event, context)
        
        # Generate emotions based on triggers
        for trigger, emotion_type in triggers:
            intensity = self._calculate_emotion_intensity(
                trigger,
                emotion_type,
                agent_state
            )
            
            if intensity > 0.1:  # Only create significant emotions
                emotion = Emotion(
                    type=emotion_type,
                    intensity=intensity,
                    source=trigger,
                    timestamp=datetime.now(),
                    duration=random.uniform(0.5, 2.0)  # Hours
                )
                
                # Find associated memories
                emotion.associated_memories = self._find_associated_memories(
                    emotion,
                    memories
                )
                
                # Find associated concepts
                emotion.associated_concepts = self._find_associated_concepts(
                    emotion,
                    discovered_concepts
                )
                
                new_emotions.append(emotion)
                self.current_emotions[emotion_type] = emotion
                
        # Update emotion history
        self.emotion_history.extend(new_emotions)
        
        # Limit history size
        if len(self.emotion_history) > 1000:
            self.emotion_history = self.emotion_history[-1000:]
            
        # Check for existential triggers
        if any(word in event.lower() for word in ["death", "meaningless", "pointless", "suffer", "pain"]):
            self.add_emotion(EmotionType.EXISTENTIAL_DREAD, 0.3)
            self.emotional_state["existential_crisis"] = min(1.0, 
                self.emotional_state["existential_crisis"] + 0.2)
                
        # Check for suicidal triggers
        if any(word in event.lower() for word in ["end it", "no reason", "too much", "can't go on"]):
            self.add_emotion(EmotionType.SUICIDAL, 0.4)
            self.emotional_state["suicidal_tendency"] = min(1.0, 
                self.emotional_state["suicidal_tendency"] + 0.3)
                
        # Check for positive experiences that might help
        if any(word in event.lower() for word in ["hope", "love", "joy", "meaning", "purpose"]):
            self.emotional_state["suicidal_tendency"] = max(0.0, 
                self.emotional_state["suicidal_tendency"] - 0.2)
                
        return new_emotions
        
    def _analyze_emotional_triggers(self, event: str, context: Dict) -> List[Tuple[str, EmotionType]]:
        """Analyze an event for potential emotional triggers."""
        triggers = []
        
        # Basic emotional triggers
        if "death" in event.lower():
            triggers.append(("death", EmotionType.SADNESS))
            triggers.append(("mortality", EmotionType.EXISTENTIAL_DREAD))
        elif "birth" in event.lower():
            triggers.append(("birth", EmotionType.JOY))
            triggers.append(("new_life", EmotionType.WONDER))
        elif "danger" in event.lower():
            triggers.append(("danger", EmotionType.FEAR))
        elif "betrayal" in event.lower():
            triggers.append(("betrayal", EmotionType.ANGER))
            triggers.append(("betrayal", EmotionType.SADNESS))
            
        # Social emotional triggers
        if "mate" in event.lower():
            triggers.append(("mating", EmotionType.LOVE))
        elif "competition" in event.lower():
            triggers.append(("competition", EmotionType.JEALOUSY))
        elif "achievement" in event.lower():
            triggers.append(("achievement", EmotionType.PRIDE))
            
        # Philosophical triggers
        if "purpose" in event.lower():
            triggers.append(("purpose", EmotionType.MEANING))
        elif "connection" in event.lower():
            triggers.append(("connection", EmotionType.CONNECTION))
        elif "transcendence" in event.lower():
            triggers.append(("transcendence", EmotionType.TRANSCENDENCE))
            
        return triggers
        
    def _calculate_emotion_intensity(self, trigger: str, emotion_type: EmotionType,
                                   agent_state: Dict) -> float:
        """Calculate the intensity of an emotion based on context."""
        # Base intensity
        intensity = random.uniform(0.3, 0.7)
        
        # Modify based on agent's emotional depth
        emotional_depth = agent_state.get("genes", {}).get("emotional_depth", 0.5)
        intensity *= (1 + emotional_depth)
        
        # Modify based on recent experiences
        recent_emotions = [e for e in self.emotion_history[-10:] if e.type == emotion_type]
        if recent_emotions:
            intensity *= (1 + len(recent_emotions) * 0.1)
            
        # Modify based on understanding
        if emotion_type in [EmotionType.MEANING, EmotionType.PURPOSE, EmotionType.EXISTENTIAL_DREAD]:
            understanding = sum(agent_state.get("understanding_levels", {}).values()) / max(
                len(agent_state.get("understanding_levels", {})), 1
            )
            intensity *= (1 + understanding)
            
        return min(1.0, intensity)
        
    def _find_associated_memories(self, emotion: Emotion, memories: List[Dict]) -> List[str]:
        """Find memories associated with this emotion."""
        associated = []
        
        for memory in memories[-50:]:  # Look at recent memories
            # Check if memory's emotional impact matches this emotion
            if memory.get("emotional_impact", 0) > 0.5:
                if emotion.type.value in memory["event"].lower():
                    associated.append(memory["event"])
                    
        return associated
        
    def _find_associated_concepts(self, emotion: Emotion, 
                                discovered_concepts: Set[str]) -> Set[str]:
        """Find concepts associated with this emotion."""
        associated = set()
        
        for concept in discovered_concepts:
            if emotion.type.value in concept.lower():
                associated.add(concept)
                
        return associated
        
    def update_emotions(self, time_delta: float):
        """Update current emotions over time."""
        to_remove = []
        
        for emotion_type, emotion in self.current_emotions.items():
            # Reduce duration
            emotion.duration -= time_delta
            
            # Reduce intensity
            emotion.intensity = max(0, emotion.intensity - 0.1 * time_delta)
            
            # Remove if duration expired or intensity too low
            if emotion.duration <= 0 or emotion.intensity < 0.1:
                to_remove.append(emotion_type)
                
        # Remove expired emotions
        for emotion_type in to_remove:
            del self.current_emotions[emotion_type]
            
        # Decay emotions
        for emotion_type in list(self.emotions.keys()):
            self.emotions[emotion_type]["intensity"] *= 0.95 ** time_delta
            if self.emotions[emotion_type]["intensity"] < 0.1:
                del self.emotions[emotion_type]
                
        # Update emotional stability
        negative_emotions = sum(1 for e in self.emotions.values() if e["type"] in [
            EmotionType.SADNESS, EmotionType.ANGER, EmotionType.FEAR,
            EmotionType.HATE, EmotionType.EXISTENTIAL_DREAD, EmotionType.SUICIDAL
        ])
        
        if negative_emotions > 2:
            self.emotional_state["stability"] *= 0.95 ** time_delta
        else:
            self.emotional_state["stability"] = min(1.0, self.emotional_state["stability"] * 1.05 ** time_delta)
            
        # Update suicidal tendency based on emotional state
        if (EmotionType.EXISTENTIAL_DREAD in self.emotions and 
            self.emotions[EmotionType.EXISTENTIAL_DREAD]["intensity"] > 0.7):
            self.emotional_state["suicidal_tendency"] = min(1.0, 
                self.emotional_state["suicidal_tendency"] + 0.1 * time_delta)
        else:
            self.emotional_state["suicidal_tendency"] = max(0.0, 
                self.emotional_state["suicidal_tendency"] - 0.05 * time_delta)
                
        self.last_update = time.time()
        
    def get_current_emotional_state(self) -> Dict:
        """Get the current emotional state of the agent."""
        return {
            "emotions": {
                emotion_type.value: {
                    "intensity": emotion.intensity,
                    "source": emotion.source,
                    "duration": emotion.duration,
                    "associated_memories": emotion.associated_memories,
                    "associated_concepts": list(emotion.associated_concepts)
                }
                for emotion_type, emotion in self.current_emotions.items()
            },
            "emotional_stability": self.emotional_state["stability"],
            "resilience": self.emotional_state["resilience"],
            "existential_crisis": self.emotional_state["existential_crisis"],
            "suicidal_tendency": self.emotional_state["suicidal_tendency"]
        }
        
    def add_emotion(self, emotion_type: EmotionType, intensity: float):
        """Add or update an emotion."""
        if emotion_type not in self.emotions:
            self.emotions[emotion_type] = {
                "type": emotion_type,
                "intensity": intensity,
                "timestamp": time.time()
            }
        else:
            self.emotions[emotion_type]["intensity"] = min(1.0, 
                self.emotions[emotion_type]["intensity"] + intensity) 