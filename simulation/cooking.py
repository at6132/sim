from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

class FoodType(Enum):
    # Raw Foods
    RAW_MEAT = "raw_meat"
    RAW_FISH = "raw_fish"
    RAW_CHICKEN = "raw_chicken"
    RAW_EGGS = "raw_eggs"
    RAW_VEGETABLES = "raw_vegetables"
    RAW_FRUITS = "raw_fruits"
    RAW_GRAINS = "raw_grains"
    
    # Cooked Foods
    COOKED_MEAT = "cooked_meat"
    COOKED_FISH = "cooked_fish"
    COOKED_CHICKEN = "cooked_chicken"
    COOKED_EGGS = "cooked_eggs"
    COOKED_VEGETABLES = "cooked_vegetables"
    COOKED_GRAINS = "cooked_grains"
    
    # Processed Foods
    BREAD = "bread"
    SOUP = "soup"
    STEW = "stew"
    DRIED_FRUITS = "dried_fruits"
    DRIED_MEAT = "dried_meat"
    DRIED_FISH = "dried_fish"

@dataclass
class FoodProperties:
    nutritional_value: float  # 0-100, how much hunger it satisfies
    health_effect: float  # -100 to 100, negative for raw foods, positive for cooked
    cooking_time: float  # in seconds
    cooking_temperature: float  # in Celsius
    spoilage_time: float  # in seconds
    requires_cooking: bool
    can_be_eaten_raw: bool
    food_safety_risk: float  # 0-100, higher means more likely to cause illness

@dataclass
class CookingSkill:
    level: float = 0.0  # 0-100
    experience: float = 0.0
    specialties: List[str] = field(default_factory=list)
    last_cooked: float = 0.0
    success_rate: float = 0.0

@dataclass
class Recipe:
    name: str
    ingredients: Dict[str, float]
    cooking_time: float
    difficulty: float  # 0-100
    effects: Dict[str, float]
    required_tools: List[str]
    temperature_range: Tuple[float, float]
    skill_bonus: Dict[str, float]  # Skill bonuses for different cooking methods

class CookingSystem:
    def __init__(self):
        self.food_properties = self._initialize_food_properties()
        self.cooking_recipes = self._initialize_cooking_recipes()
        self.recipes: Dict[str, Recipe] = self._initialize_recipes()
        self.cooking_skills: Dict[str, CookingSkill] = {}
        self.active_cooking: Dict[str, Dict] = {}  # agent_id -> cooking session
        
    def _initialize_food_properties(self) -> Dict[FoodType, FoodProperties]:
        """Initialize properties for different food types."""
        return {
            FoodType.RAW_MEAT: FoodProperties(
                nutritional_value=30.0,
                health_effect=-50.0,
                cooking_time=600.0,  # 10 minutes
                cooking_temperature=70.0,
                spoilage_time=86400.0,  # 24 hours
                requires_cooking=True,
                can_be_eaten_raw=False,
                food_safety_risk=80.0
            ),
            FoodType.RAW_FISH: FoodProperties(
                nutritional_value=25.0,
                health_effect=-40.0,
                cooking_time=300.0,  # 5 minutes
                cooking_temperature=63.0,
                spoilage_time=43200.0,  # 12 hours
                requires_cooking=True,
                can_be_eaten_raw=False,
                food_safety_risk=70.0
            ),
            FoodType.RAW_CHICKEN: FoodProperties(
                nutritional_value=25.0,
                health_effect=-60.0,
                cooking_time=900.0,  # 15 minutes
                cooking_temperature=75.0,
                spoilage_time=43200.0,  # 12 hours
                requires_cooking=True,
                can_be_eaten_raw=False,
                food_safety_risk=90.0
            ),
            FoodType.RAW_EGGS: FoodProperties(
                nutritional_value=15.0,
                health_effect=-30.0,
                cooking_time=300.0,  # 5 minutes
                cooking_temperature=70.0,
                spoilage_time=604800.0,  # 7 days
                requires_cooking=True,
                can_be_eaten_raw=False,
                food_safety_risk=60.0
            ),
            FoodType.RAW_VEGETABLES: FoodProperties(
                nutritional_value=20.0,
                health_effect=10.0,
                cooking_time=300.0,  # 5 minutes
                cooking_temperature=100.0,
                spoilage_time=604800.0,  # 7 days
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=20.0
            ),
            FoodType.RAW_FRUITS: FoodProperties(
                nutritional_value=15.0,
                health_effect=20.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=259200.0,  # 3 days
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=10.0
            ),
            FoodType.RAW_GRAINS: FoodProperties(
                nutritional_value=25.0,
                health_effect=-10.0,
                cooking_time=1200.0,  # 20 minutes
                cooking_temperature=100.0,
                spoilage_time=2592000.0,  # 30 days
                requires_cooking=True,
                can_be_eaten_raw=False,
                food_safety_risk=30.0
            ),
            # Cooked versions have better properties
            FoodType.COOKED_MEAT: FoodProperties(
                nutritional_value=40.0,
                health_effect=30.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=172800.0,  # 48 hours
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=10.0
            ),
            FoodType.COOKED_FISH: FoodProperties(
                nutritional_value=35.0,
                health_effect=25.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=86400.0,  # 24 hours
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=15.0
            ),
            FoodType.COOKED_CHICKEN: FoodProperties(
                nutritional_value=35.0,
                health_effect=30.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=86400.0,  # 24 hours
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=10.0
            ),
            FoodType.COOKED_EGGS: FoodProperties(
                nutritional_value=20.0,
                health_effect=20.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=172800.0,  # 48 hours
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=10.0
            ),
            FoodType.COOKED_VEGETABLES: FoodProperties(
                nutritional_value=25.0,
                health_effect=30.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=259200.0,  # 3 days
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=5.0
            ),
            FoodType.COOKED_GRAINS: FoodProperties(
                nutritional_value=30.0,
                health_effect=25.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=604800.0,  # 7 days
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=5.0
            ),
            # Processed foods
            FoodType.BREAD: FoodProperties(
                nutritional_value=35.0,
                health_effect=20.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=604800.0,  # 7 days
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=5.0
            ),
            FoodType.SOUP: FoodProperties(
                nutritional_value=40.0,
                health_effect=35.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=86400.0,  # 24 hours
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=10.0
            ),
            FoodType.STEW: FoodProperties(
                nutritional_value=45.0,
                health_effect=40.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=172800.0,  # 48 hours
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=10.0
            ),
            FoodType.DRIED_FRUITS: FoodProperties(
                nutritional_value=30.0,
                health_effect=25.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=2592000.0,  # 30 days
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=5.0
            ),
            FoodType.DRIED_MEAT: FoodProperties(
                nutritional_value=35.0,
                health_effect=30.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=2592000.0,  # 30 days
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=5.0
            ),
            FoodType.DRIED_FISH: FoodProperties(
                nutritional_value=30.0,
                health_effect=25.0,
                cooking_time=0.0,
                cooking_temperature=0.0,
                spoilage_time=2592000.0,  # 30 days
                requires_cooking=False,
                can_be_eaten_raw=True,
                food_safety_risk=5.0
            )
        }
        
    def _initialize_cooking_recipes(self) -> Dict[FoodType, Dict[FoodType, float]]:
        """Initialize recipes for cooking different foods."""
        return {
            FoodType.RAW_MEAT: {FoodType.COOKED_MEAT: 1.0},
            FoodType.RAW_FISH: {FoodType.COOKED_FISH: 1.0},
            FoodType.RAW_CHICKEN: {FoodType.COOKED_CHICKEN: 1.0},
            FoodType.RAW_EGGS: {FoodType.COOKED_EGGS: 1.0},
            FoodType.RAW_VEGETABLES: {FoodType.COOKED_VEGETABLES: 1.0},
            FoodType.RAW_GRAINS: {FoodType.COOKED_GRAINS: 1.0},
            # Complex recipes
            FoodType.COOKED_MEAT: {
                FoodType.STEW: 0.8,
                FoodType.DRIED_MEAT: 0.6
            },
            FoodType.COOKED_FISH: {
                FoodType.SOUP: 0.8,
                FoodType.DRIED_FISH: 0.6
            },
            FoodType.RAW_FRUITS: {
                FoodType.DRIED_FRUITS: 0.7
            },
            FoodType.COOKED_GRAINS: {
                FoodType.BREAD: 0.8
            }
        }
        
    def _initialize_recipes(self) -> Dict[str, Recipe]:
        """Initialize available recipes."""
        return {
            "basic_stew": Recipe(
                name="Basic Stew",
                ingredients={"meat": 1.0, "vegetables": 2.0, "water": 1.0},
                cooking_time=1800.0,  # 30 minutes
                difficulty=20.0,
                effects={"hunger": 0.7, "health": 0.1},
                required_tools=["pot", "fire"],
                temperature_range=(80.0, 100.0),
                skill_bonus={"stewing": 0.2}
            ),
            "roasted_meat": Recipe(
                name="Roasted Meat",
                ingredients={"meat": 2.0, "herbs": 0.5},
                cooking_time=1200.0,  # 20 minutes
                difficulty=30.0,
                effects={"hunger": 0.8, "health": 0.15},
                required_tools=["spit", "fire"],
                temperature_range=(150.0, 200.0),
                skill_bonus={"roasting": 0.3}
            ),
            "hearty_soup": Recipe(
                name="Hearty Soup",
                ingredients={"meat": 1.0, "vegetables": 3.0, "herbs": 1.0, "water": 2.0},
                cooking_time=2400.0,  # 40 minutes
                difficulty=40.0,
                effects={"hunger": 0.6, "health": 0.3, "energy": 0.2},
                required_tools=["pot", "fire", "cutting_board"],
                temperature_range=(90.0, 100.0),
                skill_bonus={"soup_making": 0.4}
            ),
            "preserved_food": Recipe(
                name="Preserved Food",
                ingredients={"meat": 3.0, "salt": 1.0, "herbs": 1.0},
                cooking_time=3600.0,  # 1 hour
                difficulty=50.0,
                effects={"hunger": 0.5, "health": 0.1, "preservation": 0.8},
                required_tools=["smoking_rack", "fire"],
                temperature_range=(60.0, 80.0),
                skill_bonus={"preservation": 0.5}
            )
        }
        
    def cook_food(self, food_type: FoodType, cooking_time: float, 
                 temperature: float) -> Optional[FoodType]:
        """Cook food and return the resulting food type."""
        if food_type not in self.food_properties:
            return None
            
        properties = self.food_properties[food_type]
        
        # Check if food can be cooked
        if not properties.requires_cooking:
            return food_type
            
        # Check if cooking conditions are met
        if cooking_time < properties.cooking_time or \
           abs(temperature - properties.cooking_temperature) > 10:
            return None
            
        # Get possible cooked versions
        if food_type in self.cooking_recipes:
            cooked_versions = self.cooking_recipes[food_type]
            # For now, just return the first possible cooked version
            return next(iter(cooked_versions.keys()))
            
        return None
        
    def get_food_properties(self, food_type: FoodType) -> Optional[FoodProperties]:
        """Get properties for a food type."""
        return self.food_properties.get(food_type)
        
    def calculate_health_effect(self, food_type: FoodType, 
                              is_cooked: bool = False) -> float:
        """Calculate health effect of consuming food."""
        properties = self.food_properties.get(food_type)
        if not properties:
            return 0.0
            
        # Base health effect
        health_effect = properties.health_effect
        
        # Adjust for cooking
        if is_cooked:
            health_effect += 20.0
            
        # Random variation based on food safety risk
        risk_factor = random.uniform(0.8, 1.2)
        health_effect *= risk_factor
        
        return health_effect
        
    def calculate_nutritional_value(self, food_type: FoodType, 
                                  is_cooked: bool = False) -> float:
        """Calculate nutritional value of food."""
        properties = self.food_properties.get(food_type)
        if not properties:
            return 0.0
            
        # Base nutritional value
        nutritional_value = properties.nutritional_value
        
        # Adjust for cooking
        if is_cooked:
            nutritional_value *= 1.2
            
        return nutritional_value 

    def start_cooking(self, agent_id: str, recipe_name: str, ingredients: Dict[str, float]) -> bool:
        """Start a cooking session."""
        if agent_id in self.active_cooking:
            return False
            
        recipe = self.recipes.get(recipe_name)
        if not recipe:
            return False
            
        # Validate ingredients
        if not self._validate_ingredients(recipe, ingredients):
            return False
            
        # Get cooking skill
        skill = self.cooking_skills.get(agent_id, CookingSkill())
        
        # Calculate success chance
        success_chance = self._calculate_success_chance(recipe, skill)
        
        # Start cooking session
        self.active_cooking[agent_id] = {
            "recipe": recipe,
            "start_time": time.time(),
            "ingredients": ingredients,
            "success_chance": success_chance,
            "temperature": self._get_optimal_temperature(recipe, skill),
            "progress": 0.0
        }
        
        return True
        
    def update_cooking(self, time_delta: float):
        """Update active cooking sessions."""
        for agent_id, session in list(self.active_cooking.items()):
            recipe = session["recipe"]
            
            # Update progress
            session["progress"] += time_delta / recipe.cooking_time
            
            # Check temperature
            if not self._is_temperature_optimal(session["temperature"], recipe):
                session["success_chance"] *= 0.95
                
            # Check if cooking is complete
            if session["progress"] >= 1.0:
                self._complete_cooking(agent_id, session)
                
    def _validate_ingredients(self, recipe: Recipe, ingredients: Dict[str, float]) -> bool:
        """Validate if provided ingredients match recipe requirements."""
        for ingredient, amount in recipe.ingredients.items():
            if ingredient not in ingredients or ingredients[ingredient] < amount:
                return False
        return True
        
    def _calculate_success_chance(self, recipe: Recipe, skill: CookingSkill) -> float:
        """Calculate cooking success chance based on recipe difficulty and skill."""
        base_chance = 0.5
        
        # Skill level bonus
        skill_bonus = skill.level / 100.0
        
        # Recipe difficulty penalty
        difficulty_penalty = recipe.difficulty / 100.0
        
        # Specialization bonus
        specialization_bonus = 0.0
        for specialty in skill.specialties:
            if specialty in recipe.skill_bonus:
                specialization_bonus += recipe.skill_bonus[specialty]
                
        return min(1.0, base_chance + skill_bonus - difficulty_penalty + specialization_bonus)
        
    def _get_optimal_temperature(self, recipe: Recipe, skill: CookingSkill) -> float:
        """Get optimal cooking temperature based on recipe and skill."""
        min_temp, max_temp = recipe.temperature_range
        optimal_temp = (min_temp + max_temp) / 2.0
        
        # Skill affects temperature control
        temp_variance = (max_temp - min_temp) * (1.0 - skill.level / 100.0)
        
        return optimal_temp + random.uniform(-temp_variance, temp_variance)
        
    def _is_temperature_optimal(self, current_temp: float, recipe: Recipe) -> bool:
        """Check if current temperature is within optimal range."""
        min_temp, max_temp = recipe.temperature_range
        return min_temp <= current_temp <= max_temp
        
    def _complete_cooking(self, agent_id: str, session: Dict):
        """Complete a cooking session and create the cooked food."""
        recipe = session["recipe"]
        skill = self.cooking_skills.get(agent_id, CookingSkill())
        
        # Determine success
        success = random.random() < session["success_chance"]
        
        if success:
            # Create cooked food
            food = Food(
                type=recipe.name,
                amount=1.0,
                quality=self._calculate_food_quality(recipe, skill, session),
                effects=recipe.effects.copy()
            )
            
            # Update skill
            self._update_cooking_skill(agent_id, recipe, success)
            
            # Log success
            self.world.log_event("cooking_success", {
                "agent_id": agent_id,
                "recipe": recipe.name,
                "quality": food.quality
            })
        else:
            # Create failed food
            food = Food(
                type=f"burnt_{recipe.name}",
                amount=0.5,
                quality=0.2,
                effects={"hunger": 0.2, "health": -0.1}
            )
            
            # Update skill
            self._update_cooking_skill(agent_id, recipe, success)
            
            # Log failure
            self.world.log_event("cooking_failure", {
                "agent_id": agent_id,
                "recipe": recipe.name
            })
            
        # Add food to world
        self.world.resources.add(food)
        
        # Remove cooking session
        del self.active_cooking[agent_id]
        
    def _calculate_food_quality(self, recipe: Recipe, skill: CookingSkill, session: Dict) -> float:
        """Calculate the quality of cooked food."""
        base_quality = 0.5
        
        # Skill level bonus
        skill_bonus = skill.level / 100.0
        
        # Temperature control bonus
        temp_bonus = 0.0
        if self._is_temperature_optimal(session["temperature"], recipe):
            temp_bonus = 0.2
            
        # Specialization bonus
        specialization_bonus = 0.0
        for specialty in skill.specialties:
            if specialty in recipe.skill_bonus:
                specialization_bonus += recipe.skill_bonus[specialty]
                
        return min(1.0, base_quality + skill_bonus + temp_bonus + specialization_bonus)
        
    def _update_cooking_skill(self, agent_id: str, recipe: Recipe, success: bool):
        """Update cooking skill based on cooking attempt."""
        if agent_id not in self.cooking_skills:
            self.cooking_skills[agent_id] = CookingSkill()
            
        skill = self.cooking_skills[agent_id]
        
        # Calculate experience gain
        base_exp = recipe.difficulty / 10.0
        if success:
            base_exp *= 1.5
            
        # Apply experience
        skill.experience += base_exp
        
        # Level up if enough experience
        if skill.experience >= 100.0:
            skill.level = min(100.0, skill.level + 1.0)
            skill.experience = 0.0
            
            # Chance to gain specialization
            if random.random() < 0.1:  # 10% chance
                for method, bonus in recipe.skill_bonus.items():
                    if method not in skill.specialties:
                        skill.specialties.append(method)
                        break
                        
        # Update success rate
        skill.success_rate = (skill.success_rate * 0.9) + (1.0 if success else 0.0) * 0.1
        skill.last_cooked = time.time()
        
    def to_dict(self) -> Dict:
        """Convert system state to dictionary."""
        return {
            'recipes': {
                name: {
                    'ingredients': recipe.ingredients,
                    'cooking_time': recipe.cooking_time,
                    'difficulty': recipe.difficulty,
                    'effects': recipe.effects,
                    'required_tools': recipe.required_tools,
                    'temperature_range': recipe.temperature_range,
                    'skill_bonus': recipe.skill_bonus
                }
                for name, recipe in self.recipes.items()
            },
            'cooking_skills': {
                agent_id: {
                    'level': skill.level,
                    'experience': skill.experience,
                    'specialties': skill.specialties,
                    'last_cooked': skill.last_cooked,
                    'success_rate': skill.success_rate
                }
                for agent_id, skill in self.cooking_skills.items()
            },
            'active_cooking': {
                agent_id: {
                    'recipe': session['recipe'].name,
                    'start_time': session['start_time'],
                    'progress': session['progress'],
                    'success_chance': session['success_chance'],
                    'temperature': session['temperature']
                }
                for agent_id, session in self.active_cooking.items()
            }
        } 