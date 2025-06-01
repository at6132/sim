from enum import Enum
from typing import Dict, List
import random

class MoralAlignment(Enum):
    LAWFUL_GOOD = "lawful_good"
    NEUTRAL_GOOD = "neutral_good"
    CHAOTIC_GOOD = "chaotic_good"
    LAWFUL_NEUTRAL = "lawful_neutral"
    NEUTRAL = "neutral"
    CHAOTIC_NEUTRAL = "chaotic_neutral"
    LAWFUL_EVIL = "lawful_evil"
    NEUTRAL_EVIL = "neutral_evil"
    CHAOTIC_EVIL = "chaotic_evil"
    
    @classmethod
    def from_values(cls, law_chaos: float, good_evil: float) -> 'MoralAlignment':
        """Convert law-chaos and good-evil values to alignment."""
        # Normalize values to 0-1 range
        law_chaos = max(0.0, min(1.0, law_chaos))
        good_evil = max(0.0, min(1.0, good_evil))
        
        # Determine law-chaos axis
        if law_chaos < 0.33:
            law_axis = "lawful"
        elif law_chaos < 0.66:
            law_axis = "neutral"
        else:
            law_axis = "chaotic"
            
        # Determine good-evil axis
        if good_evil < 0.33:
            good_axis = "good"
        elif good_evil < 0.66:
            good_axis = "neutral"
        else:
            good_axis = "evil"
            
        # Combine axes
        if law_axis == "neutral" and good_axis == "neutral":
            return cls.NEUTRAL
        elif law_axis == "neutral":
            return cls[f"NEUTRAL_{good_axis.upper()}"]
        elif good_axis == "neutral":
            return cls[f"{law_axis.upper()}_NEUTRAL"]
        else:
            return cls[f"{law_axis.upper()}_{good_axis.upper()}"]
            
    def to_values(self) -> Dict[str, float]:
        """Convert alignment to law-chaos and good-evil values."""
        values = {
            "law_chaos": 0.5,  # 0.0 = lawful, 1.0 = chaotic
            "good_evil": 0.5   # 0.0 = good, 1.0 = evil
        }
        
        # Set law-chaos value
        if "LAWFUL" in self.value:
            values["law_chaos"] = 0.2
        elif "CHAOTIC" in self.value:
            values["law_chaos"] = 0.8
            
        # Set good-evil value
        if "GOOD" in self.value:
            values["good_evil"] = 0.2
        elif "EVIL" in self.value:
            values["good_evil"] = 0.8
            
        return values
        
    def shift(self, law_chaos_delta: float, good_evil_delta: float) -> 'MoralAlignment':
        """Shift alignment based on changes in law-chaos and good-evil values."""
        current_values = self.to_values()
        new_law_chaos = max(0.0, min(1.0, current_values["law_chaos"] + law_chaos_delta))
        new_good_evil = max(0.0, min(1.0, current_values["good_evil"] + good_evil_delta))
        return self.from_values(new_law_chaos, new_good_evil)
        
    def get_description(self) -> str:
        """Get a description of the alignment."""
        descriptions = {
            "lawful_good": "Believes in order and goodness",
            "neutral_good": "Believes in goodness without strict order",
            "chaotic_good": "Believes in freedom and goodness",
            "lawful_neutral": "Believes in order above all",
            "neutral": "Balances all aspects",
            "chaotic_neutral": "Believes in freedom above all",
            "lawful_evil": "Believes in order through evil",
            "neutral_evil": "Believes in evil without strict order",
            "chaotic_evil": "Believes in freedom through evil"
        }
        return descriptions[self.value] 