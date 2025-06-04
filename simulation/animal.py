from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
import random
import time
import logging

logger = logging.getLogger(__name__)

class AnimalType(Enum):
    HORSE = "horse"
    WOLF = "wolf"
    DEER = "deer"
    BEAR = "bear"
    RABBIT = "rabbit"
    SHEEP = "sheep"
    COW = "cow"
    GOAT = "goat"

class AnimalTemperament(Enum):
    DOCILE = "docile"
    NEUTRAL = "neutral"
    AGGRESSIVE = "aggressive"
    WILD = "wild"

@dataclass
class AnimalNeeds:
    hunger: float = 100.0  # 0-100, 0 means starving
    thirst: float = 100.0  # 0-100, 0 means dehydrated
    energy: float = 100.0  # 0-100, 0 means exhausted
    health: float = 100.0  # 0-100, 0 means dead
    reproduction_urge: float = 0.0  # 0-100, increases with age and health
    social_need: float = 50.0  # 0-100, varies by species
    comfort: float = 100.0  # 0-100, affected by environment

@dataclass
class AnimalState:
    is_sick: bool = False
    disease_resistance: float = 100.0  # 0-100, affected by health and age
    pregnancy_progress: float = 0.0  # 0-100, for pregnant animals
    age: float = 0.0  # in years
    lifespan: float = 0.0  # in years, varies by species
    maturity_age: float = 0.0  # age at which animal can reproduce
    last_meal_time: float = 0.0
    last_water_time: float = 0.0
    last_rest_time: float = 0.0
    last_social_time: float = 0.0
    reproduction_cooldown: float = 0.0
    territory: Optional[Tuple[float, float, float, float]] = None
    social_group: Optional[str] = None

@dataclass
class Animal:
    id: str
    type: AnimalType
    name: str
    position: Tuple[float, float]
    age: float = 0.0
    health: float = 1.0
    domesticated: bool = False
    owner_id: Optional[str] = None
    training_progress: float = 0.0
    temperament: AnimalTemperament = AnimalTemperament.NEUTRAL
    needs: AnimalNeeds = field(default_factory=AnimalNeeds)
    state: AnimalState = field(default_factory=AnimalState)
    
    # Physical attributes
    size: float = 1.0
    speed: float = 1.0
    strength: float = 1.0
    intelligence: float = 1.0
    diet: List[str] = field(default_factory=list)
    last_action: str = "idle"

class AnimalSystem:
    def __init__(self, world):
        """Initialize the animal system with a reference to the world."""
        self.world = world
        self.animals: Dict[str, Animal] = {}
        self.animal_types = self._initialize_animal_types()
        self.social_groups = {}
        self.territories = {}
        
    def _initialize_animal_types(self):
        """Initialize the types of animals and their attributes."""
        return {
            AnimalType.HORSE: {
                "type": AnimalType.HORSE,
                "size": 2.0,
                "speed": 1.5,
                "strength": 1.2,
                "intelligence": 0.8,
                "temperament": AnimalTemperament.DOCILE,
                "diet": ["grass", "hay", "grain"],
                "lifespan": 25.0,
                "maturity_age": 3.0,
                "social": True,
                "territory_size": 1.0
            },
            AnimalType.WOLF: {
                "type": AnimalType.WOLF,
                "size": 1.5,
                "speed": 1.8,
                "strength": 1.5,
                "intelligence": 1.2,
                "temperament": AnimalTemperament.AGGRESSIVE,
                "diet": ["meat"],
                "lifespan": 12.0,
                "maturity_age": 2.0,
                "social": True,
                "territory_size": 2.0
            },
            AnimalType.DEER: {
                "type": AnimalType.DEER,
                "size": 1.8,
                "speed": 1.6,
                "strength": 1.0,
                "intelligence": 0.7,
                "temperament": AnimalTemperament.NEUTRAL,
                "diet": ["grass", "leaves", "bark"],
                "lifespan": 15.0,
                "maturity_age": 2.0,
                "social": True,
                "territory_size": 1.5
            },
            AnimalType.BEAR: {
                "type": AnimalType.BEAR,
                "size": 2.5,
                "speed": 1.2,
                "strength": 2.0,
                "intelligence": 1.0,
                "temperament": AnimalTemperament.AGGRESSIVE,
                "diet": ["meat", "fish", "berries", "honey"],
                "lifespan": 20.0,
                "maturity_age": 4.0,
                "social": False,
                "territory_size": 3.0
            },
            AnimalType.RABBIT: {
                "type": AnimalType.RABBIT,
                "size": 0.5,
                "speed": 1.4,
                "strength": 0.3,
                "intelligence": 0.6,
                "temperament": AnimalTemperament.NEUTRAL,
                "diet": ["grass", "vegetables"],
                "lifespan": 8.0,
                "maturity_age": 0.5,
                "social": True,
                "territory_size": 0.5
            },
            AnimalType.SHEEP: {
                "type": AnimalType.SHEEP,
                "size": 1.2,
                "speed": 1.0,
                "strength": 0.8,
                "intelligence": 0.5,
                "temperament": AnimalTemperament.DOCILE,
                "diet": ["grass", "hay"],
                "lifespan": 12.0,
                "maturity_age": 1.0,
                "social": True,
                "territory_size": 0.8
            },
            AnimalType.COW: {
                "type": AnimalType.COW,
                "size": 2.2,
                "speed": 0.8,
                "strength": 1.5,
                "intelligence": 0.6,
                "temperament": AnimalTemperament.DOCILE,
                "diet": ["grass", "hay", "grain"],
                "lifespan": 20.0,
                "maturity_age": 2.0,
                "social": True,
                "territory_size": 1.0
            },
            AnimalType.GOAT: {
                "type": AnimalType.GOAT,
                "size": 1.0,
                "speed": 1.2,
                "strength": 0.9,
                "intelligence": 0.7,
                "temperament": AnimalTemperament.NEUTRAL,
                "diet": ["grass", "leaves", "bark"],
                "lifespan": 15.0,
                "maturity_age": 1.5,
                "social": True,
                "territory_size": 0.8
            }
        }
        
    def initialize_animals(self):
        """Initialize the animal system with initial populations."""
        logger.info("Initializing animal system...")
        
        # Get all regions
        regions = self.world.get_regions()
        
        # Spawn animals in each region based on terrain type
        for region in regions:
            terrain_type = region.get("terrain_type", "grassland")
            position = region["center"]
            
            # Spawn animals based on terrain type
            if terrain_type == "forest":
                self._spawn_animals(position, "forest")
            elif terrain_type == "grassland":
                self._spawn_animals(position, "grassland")
            elif terrain_type == "desert":
                self._spawn_animals(position, "desert")
            elif terrain_type == "tundra":
                self._spawn_animals(position, "tundra")
            elif terrain_type == "swamp":
                self._spawn_animals(position, "swamp")
        
        # Initialize social groups and territories
        self._initialize_social_groups()
        self._initialize_territories()
        
        logger.info(f"Initialized {len(self.animals)} animals")
        
    def _spawn_animals(self, position: Tuple[float, float], terrain_type: str):
        """Spawn animals in a given location based on terrain type."""
        # Define animal types for each terrain
        terrain_animals = {
            "forest": [
                (AnimalType.DEER, 5),  # (type, count)
                (AnimalType.WOLF, 3),
                (AnimalType.BEAR, 2),
                (AnimalType.RABBIT, 8)
            ],
            "grassland": [
                (AnimalType.HORSE, 4),
                (AnimalType.SHEEP, 6),
                (AnimalType.COW, 3),
                (AnimalType.GOAT, 5)
            ],
            "desert": [
                (AnimalType.GOAT, 4),
                (AnimalType.COW, 2)
            ],
            "tundra": [
                (AnimalType.DEER, 3),
                (AnimalType.WOLF, 2)
            ],
            "swamp": [
                (AnimalType.DEER, 2),
                (AnimalType.RABBIT, 4)
            ]
        }
        
        # Spawn animals for this terrain type
        for animal_type, count in terrain_animals.get(terrain_type, []):
            for _ in range(count):
                # Calculate random offset from center position
                offset_lon = random.uniform(-0.1, 0.1)
                offset_lat = random.uniform(-0.1, 0.1)
                spawn_pos = (position[0] + offset_lon, position[1] + offset_lat)
                
                # Create the animal
                animal = Animal(
                    id=f"{animal_type.value}_{len(self.animals)}",
                    type=animal_type,
                    name=f"{animal_type.value.capitalize()} {len(self.animals)}",
                    position=spawn_pos,
                    age=random.uniform(0.1, 5.0),
                    health=random.uniform(0.8, 1.0),
                    domesticated=False,
                    temperament=self.animal_types[animal_type]["temperament"],
                    needs=AnimalNeeds(),
                    state=AnimalState(
                        lifespan=self.animal_types[animal_type]["lifespan"],
                        maturity_age=self.animal_types[animal_type]["maturity_age"]
                    ),
                    size=self.animal_types[animal_type]["size"],
                    speed=self.animal_types[animal_type]["speed"],
                    strength=self.animal_types[animal_type]["strength"],
                    intelligence=self.animal_types[animal_type]["intelligence"],
                    diet=self.animal_types[animal_type]["diet"]
                )
                
                self.animals[animal.id] = animal
        
    def _initialize_social_groups(self):
        """Initialize social groups for animals."""
        # Group animals by type and proximity
        type_groups = {}
        for animal_id, animal in self.animals.items():
            if animal.type not in type_groups:
                type_groups[animal.type] = []
            type_groups[animal.type].append(animal)
            
        # Create social groups for each animal type
        for animal_type, animals in type_groups.items():
            if self.animal_types[animal_type]['social']:
                # Group animals that are close to each other
                for animal in animals:
                    nearby = self._find_nearby_animals(animal, animals)
                    if nearby:
                        group_id = f"group_{animal_type.value}_{len(self.social_groups)}"
                        self.social_groups[group_id] = {a.id for a in nearby}
                        
    def _find_nearby_animals(self, animal: Animal, all_animals: List[Animal], max_distance: float = 1.0) -> List[Animal]:
        """Find animals near a given animal."""
        nearby = []
        for other in all_animals:
            if other.id != animal.id:
                distance = self._calculate_distance(animal, other)
                if distance <= max_distance:
                    nearby.append(other)
        return nearby
        
    def _calculate_distance(self, pos1: Union[Animal, Tuple[float, float]], pos2: Union[Animal, Tuple[float, float]]) -> float:
        """Calculate distance between two positions or animals."""
        # Extract positions if Animal objects are passed
        if isinstance(pos1, Animal):
            pos1 = pos1.position
        if isinstance(pos2, Animal):
            pos2 = pos2.position
            
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
        
    def _initialize_territories(self):
        """Initialize territories for territorial animals."""
        for animal_id, animal in self.animals.items():
            if not self.animal_types[animal.type]['social']:
                # Create a territory around the animal's position
                territory_size = self.animal_types[animal.type]['territory_size']
                self.territories[animal_id] = (
                    animal.position[0],
                    animal.position[1],
                    territory_size
                )
        
    def update(self, current_time: float, world_state: Dict) -> None:
        """Update all animals' states"""
        # Update existing animals
        for animal in list(self.animals.values()):
            # Update age
            animal.state.age += 0.01  # Age increases with each update
            
            # Update needs
            self._update_needs(animal, current_time, world_state)
            
            # Update health
            self._update_health(animal)
            
            # Update reproduction
            self._update_reproduction(animal, current_time)
            
            # Update behavior
            self._update_behavior(animal, current_time, world_state)
            
            # Handle death
            self._handle_death(animal)
            
        # Spawn new animals if population is too low
        self._maintain_population(world_state)
        
    def _maintain_population(self, world_state: Dict) -> None:
        """Maintain minimum population levels for each species"""
        # Count current population by type
        population_counts = {}
        for animal in self.animals.values():
            if animal.type not in population_counts:
                population_counts[animal.type] = 0
            population_counts[animal.type] += 1
            
        # Check each species
        for animal_type, traits in self.animal_types.items():
            current_count = population_counts.get(animal_type, 0)
            min_population = int(self.world.world_size * 0.01)  # 1% of world size
            
            # If population is too low, spawn new animals
            if current_count < min_population:
                num_to_spawn = min_population - current_count
                for _ in range(num_to_spawn):
                    self.spawn_animal(animal_type)
                    
    def _handle_death(self, animal: Animal) -> None:
        """Handle animal death"""
        death_causes = []
        
        # Check various death conditions
        if animal.state.age >= animal.state.lifespan:
            death_causes.append("old_age")
        if animal.needs.health <= 0:
            death_causes.append("health")
        if animal.needs.hunger <= 0:
            death_causes.append("starvation")
        if animal.needs.thirst <= 0:
            death_causes.append("dehydration")
            
        # If any death condition is met
        if death_causes:
            # Log death
            logger.info(f"Animal {animal.id} ({animal.name}) died of {', '.join(death_causes)}")
            
            # Remove from social group if applicable
            if animal.social_group:
                # Update social group members
                for other in self.animals.values():
                    if other.social_group == animal.social_group:
                        other.needs.social_need = max(0, other.needs.social_need - 20)
                        
            # Remove animal
            del self.animals[animal.id]
            
    def _update_health(self, animal: Animal) -> None:
        """Update animal's health status"""
        # Health affected by needs
        if animal.needs.hunger < 20 or animal.needs.thirst < 20:
            animal.needs.health = max(0, animal.needs.health - 0.5)
            
        # Age affects health
        age_factor = min(1.0, animal.state.age / animal.state.lifespan)
        if age_factor > 0.7:  # Elderly animals
            animal.needs.health = max(0, animal.needs.health - 0.1)
            
        # Disease resistance affected by health and age
        animal.state.disease_resistance = max(0, animal.state.disease_resistance - (age_factor * 0.1))
        
        # Random chance of getting sick
        if not animal.state.is_sick and random.random() < 0.01:
            if random.random() > (animal.state.disease_resistance / 100):
                animal.state.is_sick = True
                animal.needs.health = max(0, animal.needs.health - 10)
                
        # Recovery from sickness
        if animal.state.is_sick:
            if random.random() < 0.1:  # 10% chance to recover each update
                animal.state.is_sick = False
            else:
                animal.needs.health = max(0, animal.needs.health - 0.2)
                
    def _update_reproduction(self, animal: Animal, current_time: float) -> None:
        """Handle animal reproduction"""
        if animal.state.reproduction_cooldown > 0:
            animal.state.reproduction_cooldown -= 0.1
            
        # Check if animal can reproduce
        if (animal.state.age >= animal.state.maturity_age and 
            animal.state.reproduction_cooldown <= 0 and
            animal.needs.health > 70 and
            animal.needs.hunger > 50 and
            animal.needs.thirst > 50):
            
            # Find potential mate
            nearby_animals = self.get_nearby_animals(animal.position, 50.0)
            potential_mates = [a for a in nearby_animals 
                             if (a.type == animal.type and 
                                 a.state.age >= a.state.maturity_age and
                                 a.state.reproduction_cooldown <= 0 and
                                 a.needs.health > 70)]
                             
            if potential_mates:
                mate = random.choice(potential_mates)
                self._handle_reproduction(animal, mate)
                
    def _handle_reproduction(self, parent1: Animal, parent2: Animal) -> None:
        """Handle the reproduction process between two animals"""
        # Set reproduction cooldown
        parent1.state.reproduction_cooldown = 100.0
        parent2.state.reproduction_cooldown = 100.0
        
        # Create offspring
        offspring_type = parent1.type
        offspring_traits = self.animal_types[offspring_type]
        
        # Inherit traits from parents with some variation
        size = (parent1.size + parent2.size) / 2 * random.uniform(0.9, 1.1)
        speed = (parent1.speed + parent2.speed) / 2 * random.uniform(0.9, 1.1)
        strength = (parent1.strength + parent2.strength) / 2 * random.uniform(0.9, 1.1)
        intelligence = (parent1.intelligence + parent2.intelligence) / 2 * random.uniform(0.9, 1.1)
        
        # Create new animal
        offspring = Animal(
            id=f"{offspring_type.value}_{len(self.animals)}",
            type=offspring_type,
            name=f"Baby {offspring_type.value.capitalize()}",
            temperament=random.choice([parent1.temperament, parent2.temperament]),
            size=size,
            speed=speed,
            strength=strength,
            intelligence=intelligence,
            position=parent1.position,
            diet=offspring_traits["diet"].copy(),
            state=AnimalState(
                lifespan=offspring_traits["lifespan"],
                maturity_age=offspring_traits["maturity_age"]
            )
        )
        
        self.animals[offspring.id] = offspring
        logger.info(f"New {offspring_type.value} born to parents {parent1.id} and {parent2.id}")
        
    def spawn_animal(self, animal_type: AnimalType, position: Optional[Tuple[float, float]] = None) -> Animal:
        """Spawn a new animal of specified type"""
        animal_id = f"{animal_type.value}_{len(self.animals)}"
        attributes = self.animal_types[animal_type]
        
        # Generate random position if none provided
        if position is None:
            position = (
                random.uniform(0, self.world.world_size),
                random.uniform(0, self.world.world_size)
            )
            
        animal = Animal(
            id=animal_id,
            type=animal_type,
            name=f"{animal_type.value.capitalize()} {len(self.animals)}",
            position=position,
            size=attributes["size"],
            speed=attributes["speed"],
            strength=attributes["strength"],
            intelligence=attributes["intelligence"],
            temperament=attributes["temperament"],
            diet=attributes["diet"].copy(),
            state=AnimalState(
                lifespan=attributes["lifespan"],
                maturity_age=attributes["maturity_age"]
            )
        )
        
        self.animals[animal_id] = animal
        logger.info(f"Spawned new {animal_type.value} at position {position}")
        return animal
        
    def get_nearby_animals(self, position: Tuple[float, float], radius: float) -> List[Animal]:
        """Get animals within radius of position"""
        return [
            animal for animal in self.animals.values()
            if self._calculate_distance(position, animal.position) <= radius
        ]
        
    def _update_needs(self, animal: Animal, current_time: float, world_state: Dict) -> None:
        """Update animal needs over time"""
        # Decrease needs based on time
        animal.needs.hunger = max(0.0, animal.needs.hunger - 0.01)
        animal.needs.thirst = max(0.0, animal.needs.thirst - 0.02)
        animal.needs.energy = max(0.0, animal.needs.energy - 0.005)
        
        # Increase reproduction urge over time
        animal.needs.reproduction_urge = min(100.0, animal.needs.reproduction_urge + 0.001)
        
    def _update_behavior(self, animal: Animal, current_time: float, world_state: Dict) -> None:
        """Update animal behavior based on needs and environment"""
        if animal.domesticated:
            self._update_domesticated_behavior(animal, current_time, world_state)
        else:
            self._update_wild_behavior(animal, current_time, world_state)
            
    def _update_domesticated_behavior(self, animal: Animal, current_time: float, world_state: Dict) -> None:
        """Update behavior for domesticated animals"""
        if animal.owner_id:
            owner = world_state.get("agents", {}).get(animal.owner_id)
            if owner:
                # Follow owner if too far
                distance = self._calculate_distance(animal.position, owner["position"])
                if distance > 50:  # Max follow distance
                    self._move_towards(animal.position, owner["position"])
                    
                # Train if owner is nearby
                if distance < 10:
                    animal.training_progress = min(1.0, animal.training_progress + 0.01)
                    
    def _update_wild_behavior(self, animal: Animal, current_time: float, world_state: Dict) -> None:
        """Update behavior for wild animals"""
        # Prioritize needs
        if animal.needs.thirst < 30:
            self._seek_water(animal, world_state)
        elif animal.needs.hunger < 30:
            self._seek_food(animal, world_state)
        elif animal.needs.energy < 30:
            self._rest(animal)
        elif animal.needs.social_need < 30 and self.animal_types[animal.type]["social"]:
            self._seek_social_interaction(animal)
        else:
            self._explore_territory(animal)
            
    def _seek_water(self, animal: Animal, world_state: Dict) -> None:
        """Seek water source"""
        water_sources = world_state.get("water_sources", [])
        if water_sources:
            nearest_water = min(water_sources, 
                              key=lambda w: self._calculate_distance(animal.position, w))
            direction = self._get_direction(animal.position, nearest_water)
            new_x = animal.position[0] + direction[0] * animal.speed * 10
            new_y = animal.position[1] + direction[1] * animal.speed * 10
            animal.position = (new_x, new_y)
            animal.last_action = "seeking_water"
            
            # Drink if close enough
            if self._calculate_distance(animal.position, nearest_water) < 10:
                animal.needs.thirst = min(100, animal.needs.thirst + 50)
                animal.state.last_water_time = time.time()
                animal.last_action = "drinking"
                
    def _seek_food(self, animal: Animal, world_state: Dict) -> None:
        """Seek food source based on diet"""
        # Get nearby food sources and animals
        nearby_animals = self.get_nearby_animals(animal.position, 50.0)
        food_sources = world_state.get("food_sources", [])
        
        # Filter potential prey based on diet
        if "meat" in animal.diet:
            potential_prey = [a for a in nearby_animals 
                            if a.type != animal.type and 
                            a.size < animal.size * 1.5 and
                            not a.domesticated]
            
            if potential_prey:
                # Choose weakest prey
                prey = min(potential_prey, key=lambda a: a.needs.health)
                self._hunt_prey(animal, prey)
                return
                
        # If not hunting or hunt failed, seek plants
        if food_sources:
            nearest_food = min(food_sources, 
                             key=lambda f: self._calculate_distance(animal.position, f))
            direction = self._get_direction(animal.position, nearest_food)
            new_x = animal.position[0] + direction[0] * animal.speed * 10
            new_y = animal.position[1] + direction[1] * animal.speed * 10
            animal.position = (new_x, new_y)
            animal.last_action = "seeking_food"
            
            # Eat if close enough
            if self._calculate_distance(animal.position, nearest_food) < 10:
                animal.needs.hunger = min(100, animal.needs.hunger + 50)
                animal.state.last_meal_time = time.time()
                animal.last_action = "eating"
                
    def _hunt_prey(self, predator: Animal, prey: Animal) -> None:
        """Hunt and attempt to kill prey"""
        # Calculate success chance based on relative strength and health
        predator_power = predator.strength * predator.needs.health / 100.0
        prey_power = prey.strength * prey.needs.health / 100.0
        
        success_chance = predator_power / (predator_power + prey_power)
        
        # Move towards prey
        direction = self._get_direction(predator.position, prey.position)
        new_x = predator.position[0] + direction[0] * predator.speed * 10
        new_y = predator.position[1] + direction[1] * predator.speed * 10
        predator.position = (new_x, new_y)
        predator.last_action = "hunting"
        
        # If close enough, attempt to kill
        if self._calculate_distance(predator.position, prey.position) < 10:
            if random.random() < success_chance:
                # Kill prey
                prey.needs.health = 0
                predator.needs.hunger = min(100, predator.needs.hunger + 70)
                predator.state.last_meal_time = time.time()
                predator.last_action = "eating_prey"
                
                # Remove prey from system
                del self.animals[prey.id]
            else:
                # Prey escapes
                prey.last_action = "fleeing"
                prey.needs.energy = max(0, prey.needs.energy - 20)
                predator.needs.energy = max(0, predator.needs.energy - 30)
                
    def _rest(self, animal: Animal) -> None:
        """Rest to regain energy"""
        animal.needs.energy = min(100, animal.needs.energy + 10)
        animal.state.last_rest_time = time.time()
        animal.last_action = "resting"
        
    def _seek_social_interaction(self, animal: Animal) -> None:
        """Seek social interaction with other animals"""
        nearby_animals = self.get_nearby_animals(animal.position, 50.0)
        social_animals = [a for a in nearby_animals 
                         if a.type == animal.type and a.social_group]
        
        if social_animals:
            # Join existing social group
            animal.social_group = social_animals[0].social_group
            animal.needs.social_need = min(100, animal.needs.social_need + 30)
            animal.state.last_social_time = time.time()
            animal.last_action = "socializing"
        else:
            # Create new social group
            animal.social_group = f"group_{len(self.animals)}"
            animal.last_action = "forming_group"
            
    def _explore_territory(self, animal: Animal) -> None:
        """Explore territory"""
        if animal.state.territory:
            x1, y1, x2, y2 = animal.state.territory
            new_x = random.uniform(x1, x2)
            new_y = random.uniform(y1, y2)
            animal.position = (new_x, new_y)
        else:
            # Move randomly if no territory
            dx = random.uniform(-1, 1) * animal.speed
            dy = random.uniform(-1, 1) * animal.speed
            animal.position = (animal.position[0] + dx, animal.position[1] + dy)
            
    def _get_direction(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> Tuple[float, float]:
        """Get normalized direction vector from pos1 to pos2"""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance > 0:
            return (dx / distance, dy / distance)
        return (0, 0)
        
    def _move_towards(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> None:
        """Move position 1 towards position 2"""
        direction = self._get_direction(pos1, pos2)
        return (pos1[0] + direction[0], pos1[1] + direction[1])

    def to_dict(self) -> Dict:
        """Convert animal system state to dictionary for serialization."""
        return {
            "animals": {
                animal_id: {
                    "id": animal.id,
                    "type": animal.type.value,
                    "name": animal.name,
                    "position": animal.position,
                    "needs": {
                        "hunger": animal.needs.hunger,
                        "thirst": animal.needs.thirst,
                        "energy": animal.needs.energy,
                        "health": animal.needs.health,
                        "social_need": animal.needs.social_need,
                        "comfort": animal.needs.comfort,
                        "reproduction_urge": animal.needs.reproduction_urge
                    },
                    "state": {
                        "is_sick": animal.state.is_sick,
                        "disease_resistance": animal.state.disease_resistance,
                        "pregnancy_progress": animal.state.pregnancy_progress,
                        "age": animal.state.age,
                        "lifespan": animal.state.lifespan,
                        "maturity_age": animal.state.maturity_age,
                        "reproduction_cooldown": animal.state.reproduction_cooldown,
                        "territory": animal.state.territory,
                        "social_group": animal.state.social_group
                    },
                    "domesticated": animal.domesticated,
                    "owner_id": animal.owner_id,
                    "training_progress": animal.training_progress,
                    "temperament": animal.temperament.value,
                    "size": animal.size,
                    "speed": animal.speed,
                    "strength": animal.strength,
                    "intelligence": animal.intelligence,
                    "diet": animal.diet,
                    "last_action": animal.last_action
                }
                for animal_id, animal in self.animals.items()
            }
        } 