from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class Word:
    word: str
    meaning: str
    origin: str  # Which agent/tribe created it
    created_at: float = field(default_factory=time.time)
    usage_count: int = 0
    complexity: float = 0.0  # 0-1 scale
    emotional_weight: float = 0.0  # 0-1 scale
    cultural_significance: float = 0.0  # 0-1 scale

@dataclass
class Grammar:
    rules: Dict[str, Any] = field(default_factory=dict)
    complexity: float = 0.0  # 0-1 scale
    flexibility: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Language:
    name: str
    creator: str  # Agent ID
    words: Dict[str, Word] = field(default_factory=dict)
    grammar: Grammar = field(default_factory=Grammar)
    speakers: Set[str] = field(default_factory=set)  # Set of agent IDs
    dialects: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    complexity: float = 0.0  # 0-1 scale
    cultural_significance: float = 0.0  # 0-1 scale

@dataclass
class Translation:
    source_language: str
    target_language: str
    word_mappings: Dict[str, str] = field(default_factory=dict)
    accuracy: float = 0.0  # 0-1 scale
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

class LanguageSystem:
    def __init__(self, world):
        """Initialize the language system."""
        self.world = world
        self.languages: Dict[str, Language] = {}
        self.translations: Dict[Tuple[str, str], Translation] = {}
        
    def create_language(self, name: str, creator: str) -> Language:
        """Create a new language."""
        if name in self.languages:
            logger.warning(f"Language {name} already exists")
            return self.languages[name]
            
        language = Language(
            name=name,
            creator=creator
        )
        
        self.languages[name] = language
        logger.info(f"Created new language: {name}")
        return language
        
    def create_word(self, language: str, word: str, meaning: str, creator: str) -> Word:
        """Create a new word in a language."""
        if language not in self.languages:
            logger.error(f"Language {language} does not exist")
            return None
            
        word_obj = Word(
            word=word,
            meaning=meaning,
            origin=creator
        )
        
        self.languages[language].words[word] = word_obj
        logger.info(f"Created new word {word} in language {language}")
        return word_obj
        
    def add_speaker(self, language: str, agent_id: str):
        """Add a speaker to a language."""
        if language in self.languages:
            self.languages[language].speakers.add(agent_id)
            logger.info(f"Added speaker {agent_id} to language {language}")
            
    def remove_speaker(self, language: str, agent_id: str):
        """Remove a speaker from a language."""
        if language in self.languages:
            self.languages[language].speakers.discard(agent_id)
            logger.info(f"Removed speaker {agent_id} from language {language}")
            
    def create_translation(self, source: str, target: str) -> Translation:
        """Create a translation between two languages."""
        if source not in self.languages or target not in self.languages:
            logger.error(f"One or both languages do not exist: {source}, {target}")
            return None
            
        translation = Translation(
            source_language=source,
            target_language=target
        )
        
        # Create word mappings
        for word, word_obj in self.languages[source].words.items():
            if word in self.languages[target].words:
                translation.word_mappings[word] = word
            else:
                # Find closest matching word
                closest = self._find_closest_word(word, target)
                if closest:
                    translation.word_mappings[word] = closest
                    
        self.translations[(source, target)] = translation
        logger.info(f"Created translation between {source} and {target}")
        return translation
        
    def _find_closest_word(self, word: str, target_language: str) -> Optional[str]:
        """Find the closest matching word in the target language."""
        # Simple implementation: find word with same meaning
        source_meaning = self.languages[word].words[word].meaning
        for target_word, target_obj in self.languages[target_language].words.items():
            if target_obj.meaning == source_meaning:
                return target_word
        return None
        
    def translate(self, text: str, source: str, target: str) -> str:
        """Translate text between languages."""
        if (source, target) not in self.translations:
            self.create_translation(source, target)
            
        translation = self.translations[(source, target)]
        translated_words = []
        
        for word in text.split():
            if word in translation.word_mappings:
                translated_words.append(translation.word_mappings[word])
            else:
                translated_words.append(word)  # Keep original if no translation
                
        return " ".join(translated_words)
        
    def evolve_language(self, language: str, time_delta: float):
        """Evolve a language over time."""
        if language not in self.languages:
            return
            
        lang = self.languages[language]
        
        # Evolve words
        for word, word_obj in list(lang.words.items()):
            if random.random() < 0.1 * time_delta:  # 10% chance per hour
                new_word = self._evolve_word(word)
                if new_word != word:
                    lang.words[new_word] = Word(
                        word=new_word,
                        meaning=word_obj.meaning,
                        origin=word_obj.origin
                    )
                    del lang.words[word]
                    
        # Evolve grammar
        if random.random() < 0.05 * time_delta:  # 5% chance per hour
            self._evolve_grammar(lang)
            
        # Update language complexity
        self._update_language_complexity(lang)
        
    def _evolve_word(self, word: str) -> str:
        """Evolve a word through random changes."""
        # Simple evolution: randomly change one letter
        if len(word) > 1:
            pos = random.randint(0, len(word) - 1)
            new_char = random.choice("abcdefghijklmnopqrstuvwxyz")
            return word[:pos] + new_char + word[pos + 1:]
        return word
        
    def _evolve_grammar(self, language: Language):
        """Evolve a language's grammar."""
        # Simple grammar evolution: add or modify a rule
        if not language.grammar.rules:
            language.grammar.rules = {
                "word_order": random.choice(["SVO", "SOV", "VSO"]),
                "tense": random.choice(["present", "past", "future"]),
                "number": random.choice(["singular", "plural"])
            }
        else:
            # Modify existing rules
            rule = random.choice(list(language.grammar.rules.keys()))
            if rule == "word_order":
                language.grammar.rules[rule] = random.choice(["SVO", "SOV", "VSO"])
            elif rule == "tense":
                language.grammar.rules[rule] = random.choice(["present", "past", "future"])
            elif rule == "number":
                language.grammar.rules[rule] = random.choice(["singular", "plural"])
                
    def _update_language_complexity(self, language: Language):
        """Update a language's complexity score."""
        # Factors affecting complexity:
        # 1. Number of words
        # 2. Grammar complexity
        # 3. Number of speakers
        # 4. Number of dialects
        
        word_factor = min(1.0, len(language.words) / 1000.0)
        grammar_factor = language.grammar.complexity
        speaker_factor = min(1.0, len(language.speakers) / 1000.0)
        dialect_factor = min(1.0, len(language.dialects) / 10.0)
        
        language.complexity = (
            word_factor * 0.4 +
            grammar_factor * 0.3 +
            speaker_factor * 0.2 +
            dialect_factor * 0.1
        )
        
    def update(self, time_delta: float):
        """Update language system state."""
        # Evolve languages
        for language in self.languages.values():
            self.evolve_language(language.name, time_delta)
            
        # Update translations
        self._update_translations(time_delta)
        
    def _update_translations(self, time_delta: float):
        """Update translation accuracy and mappings."""
        for translation in self.translations.values():
            # Improve accuracy over time
            if translation.accuracy < 1.0:
                translation.accuracy = min(1.0, 
                    translation.accuracy + 0.01 * time_delta)
                    
            # Update word mappings
            for word, mapping in list(translation.word_mappings.items()):
                if random.random() < 0.05 * time_delta:  # 5% chance per hour
                    new_mapping = self._find_closest_word(word, translation.target_language)
                    if new_mapping:
                        translation.word_mappings[word] = new_mapping
                        
    def to_dict(self) -> Dict:
        """Convert language system state to dictionary for serialization."""
        return {
            "languages": {
                name: {
                    "name": lang.name,
                    "creator": lang.creator,
                    "words": {
                        word: {
                            "word": word_obj.word,
                            "meaning": word_obj.meaning,
                            "origin": word_obj.origin,
                            "created_at": word_obj.created_at,
                            "usage_count": word_obj.usage_count,
                            "complexity": word_obj.complexity,
                            "emotional_weight": word_obj.emotional_weight,
                            "cultural_significance": word_obj.cultural_significance
                        }
                        for word, word_obj in lang.words.items()
                    },
                    "grammar": {
                        "rules": lang.grammar.rules,
                        "complexity": lang.grammar.complexity,
                        "flexibility": lang.grammar.flexibility,
                        "created_at": lang.grammar.created_at,
                        "last_update": lang.grammar.last_update
                    },
                    "speakers": list(lang.speakers),
                    "dialects": lang.dialects,
                    "created_at": lang.created_at,
                    "last_update": lang.last_update,
                    "complexity": lang.complexity,
                    "cultural_significance": lang.cultural_significance
                }
                for name, lang in self.languages.items()
            },
            "translations": {
                f"{source}-{target}": {
                    "source_language": trans.source_language,
                    "target_language": trans.target_language,
                    "word_mappings": trans.word_mappings,
                    "accuracy": trans.accuracy,
                    "created_at": trans.created_at,
                    "last_used": trans.last_used
                }
                for (source, target), trans in self.translations.items()
            }
        } 