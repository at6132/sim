from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

class FoodType(Enum):
    """Types of food available in the simulation."""
    RAW_MEAT = "raw_meat"
    COOKED_MEAT = "cooked_meat"
    RAW_FISH = "raw_fish"
    COOKED_FISH = "cooked_fish"
    RAW_VEGETABLES = "raw_vegetables"
    COOKED_VEGETABLES = "cooked_vegetables"
    RAW_GRAINS = "raw_grains"
    BREAD = "bread"
    FRUIT = "fruit"
    NUTS = "nuts"
    BERRIES = "berries"
    WATER = "water"
    MILK = "milk"
    CHEESE = "cheese"
    EGGS = "eggs"
    HONEY = "honey"

@dataclass
class Recipe:
    """A cooking recipe."""
    name: str
    ingredients: Dict[str, float]  # ingredient -> amount needed
    result: str  # FoodType value
    cook_time: float  # in seconds
    requires_fire: bool = True

# Basic recipes
RECIPES = {
    "cooked_meat": Recipe(
        name="Cooked Meat",
        ingredients={FoodType.RAW_MEAT.value: 1.0},
        result=FoodType.COOKED_MEAT.value,
        cook_time=60.0,
        requires_fire=True
    ),
    "cooked_fish": Recipe(
        name="Cooked Fish",
        ingredients={FoodType.RAW_FISH.value: 1.0},
        result=FoodType.COOKED_FISH.value,
        cook_time=45.0,
        requires_fire=True
    ),
    "cooked_vegetables": Recipe(
        name="Cooked Vegetables",
        ingredients={FoodType.RAW_VEGETABLES.value: 1.0},
        result=FoodType.COOKED_VEGETABLES.value,
        cook_time=30.0,
        requires_fire=True
    ),
    "bread": Recipe(
        name="Bread",
        ingredients={FoodType.RAW_GRAINS.value: 2.0, FoodType.WATER.value: 1.0},
        result=FoodType.BREAD.value,
        cook_time=120.0,
        requires_fire=True
    ),
}

class CookingSystem:
    """Manages cooking and food preparation."""
    
    def __init__(self):
        self.recipes = RECIPES
        
    def cook(self, recipe_name: str, ingredients: Dict[str, float]) -> Optional[str]:
        """
        Cook a recipe with given ingredients.
        Returns the resulting food type or None if cooking fails.
        """
        if recipe_name not in self.recipes:
            return None
            
        recipe = self.recipes[recipe_name]
        
        # Check if all ingredients are available
        for ingredient, amount_needed in recipe.ingredients.items():
            if ingredients.get(ingredient, 0) < amount_needed:
                return None
                
        # Cooking successful
        return recipe.result
        
    def get_nutrition_value(self, food_type: str) -> float:
        """Get the nutritional value of a food type."""
        nutrition_values = {
            FoodType.RAW_MEAT.value: 0.6,
            FoodType.COOKED_MEAT.value: 0.8,
            FoodType.RAW_FISH.value: 0.5,
            FoodType.COOKED_FISH.value: 0.7,
            FoodType.RAW_VEGETABLES.value: 0.3,
            FoodType.COOKED_VEGETABLES.value: 0.4,
            FoodType.RAW_GRAINS.value: 0.2,
            FoodType.BREAD.value: 0.6,
            FoodType.FRUIT.value: 0.4,
            FoodType.NUTS.value: 0.5,
            FoodType.BERRIES.value: 0.3,
            FoodType.WATER.value: 0.1,
            FoodType.MILK.value: 0.5,
            FoodType.CHEESE.value: 0.7,
            FoodType.EGGS.value: 0.6,
            FoodType.HONEY.value: 0.4,
        }
        return nutrition_values.get(food_type, 0.1)