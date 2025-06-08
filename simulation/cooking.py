from dataclasses import dataclass
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

class CookingSystem:
    def __init__(self):
        self.food_properties = self._initialize_food_properties()
        self.cooking_recipes = self._initialize_cooking_recipes()
        
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