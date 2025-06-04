import random
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Genes:
    # Core traits
    curiosity: float = 1.0  # Curiosity
    strength: float = 1.0  # Physical strength
    intelligence: float = 1.0  # Cognitive ability
    social_drive: float = 1.0  # Social drive
    creativity: float = 1.0  # Creative thinking
    adaptability: float = 1.0  # Adaptability
    
    # Advanced traits
    philosophical_tendency: float = 1.0  # Philosophical tendency
    emotional_depth: float = 1.0  # Emotional depth
    existential_awareness: float = 1.0  # Existential awareness
    cognitive_complexity: float = 1.0  # Cognitive complexity
    cultural_sensitivity: float = 1.0  # Cultural sensitivity
    
    # Physical traits
    fertility: float = 1.0  # Fertility
    longevity: float = 1.0  # Life expectancy
    disease_resistance: float = 1.0  # Disease resistance
    metabolism: float = 1.0  # Energy efficiency
    
    # Skills
    animal_affinity: float = 1.0  # Animal affinity
    hunting_skill: float = 1.0  # Hunting skill
    taming_skill: float = 1.0  # Taming skill
    
    def __post_init__(self):
        """Initialize genes after dataclass initialization."""
        # Only randomize if all values are still at their defaults
        if all(getattr(self, field) == 1.0 for field in self.__dataclass_fields__):
            self._randomize_genes()
            
    def _randomize_genes(self):
        """Set random values for all genetic traits."""
        for field in self.__dataclass_fields__:
            setattr(self, field, random.uniform(0.3, 0.7))
            
    def _inherit_from_parent(self, parent: 'Genes'):
        """Inherit genes from parent with some random variation."""
        for field in self.__dataclass_fields__:
            parent_value = getattr(parent, field)
            # Inherit with ±20% variation
            variation = random.uniform(-0.2, 0.2)
            new_value = max(0.0, min(1.0, parent_value + variation))
            setattr(self, field, new_value)
            
    def mutate(self, mutation_rate: float = 0.1):
        """Randomly mutate genes with given probability."""
        for field in self.__dataclass_fields__:
            if random.random() < mutation_rate:
                current_value = getattr(self, field)
                # Mutate with ±30% variation
                variation = random.uniform(-0.3, 0.3)
                new_value = max(0.0, min(1.0, current_value + variation))
                setattr(self, field, new_value)
                
    def combine(self, other: 'Genes') -> 'Genes':
        """Combine genes with another set to create offspring genes."""
        child_genes = Genes()
        for field in self.__dataclass_fields__:
            # Randomly inherit from either parent
            if random.random() < 0.5:
                setattr(child_genes, field, getattr(self, field))
            else:
                setattr(child_genes, field, getattr(other, field))
        return child_genes

    def to_dict(self) -> Dict:
        """Convert genes to dictionary"""
        return {
            "curiosity": self.curiosity,
            "strength": self.strength,
            "intelligence": self.intelligence,
            "social_drive": self.social_drive,
            "creativity": self.creativity,
            "adaptability": self.adaptability,
            "philosophical_tendency": self.philosophical_tendency,
            "emotional_depth": self.emotional_depth,
            "existential_awareness": self.existential_awareness,
            "cognitive_complexity": self.cognitive_complexity,
            "cultural_sensitivity": self.cultural_sensitivity,
            "fertility": self.fertility,
            "longevity": self.longevity,
            "disease_resistance": self.disease_resistance,
            "metabolism": self.metabolism,
            "animal_affinity": self.animal_affinity,
            "hunting_skill": self.hunting_skill,
            "taming_skill": self.taming_skill
        }

    @classmethod
    def from_parents(cls, parent1: 'Genes', parent2: 'Genes') -> 'Genes':
        """Create new genes by combining parent genes with mutations"""
        genes = cls()
        
        # Inherit traits from parents with mutation
        for trait in vars(genes):
            if trait.startswith('__'):
                continue
            parent_value = (getattr(parent1, trait) + getattr(parent2, trait)) / 2
            mutation = random.uniform(-0.1, 0.1)  # Small random mutation
            setattr(genes, trait, max(0.0, min(1.0, parent_value + mutation)))
        
        return genes 