from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import random
from datetime import datetime
import logging
import numpy as np
from .utils.logging_config import get_logger
import time

logger = get_logger(__name__)

class ResourceType(Enum):
    # Basic Resources
    FOOD = "food"
    WATER = "water"
    WOOD = "wood"
    STONE = "stone"
    ORE = "ore"
    FIBER = "fiber"
    
    # Marine Resources
    FISH = "fish"
    SHELLFISH = "shellfish"
    SEAWEED = "seaweed"
    SALT = "salt"
    PEARL = "pearl"
    CORAL = "coral"
    
    # Advanced Resources
    TOOLS = "tools"
    WEAPONS = "weapons"
    CLOTHING = "clothing"
    SHELTER = "shelter"
    MEDICINE = "medicine"
    
    # Luxury Resources
    JEWELRY = "jewelry"
    ART = "art"
    SPICES = "spices"
    WINE = "wine"
    
    # Special Resources
    KNOWLEDGE = "knowledge"
    TECHNOLOGY = "technology"
    CULTURE = "culture"
    
    # Processed Resources
    DRIED_FISH = "dried_fish"
    FISH_OIL = "fish_oil"
    FISH_MEAL = "fish_meal"
    SHELL_CRAFT = "shell_craft"
    SEAWEED_FERTILIZER = "seaweed_fertilizer"

@dataclass
class Resource:
    type: ResourceType
    amount: float
    quality: float  # 0-1 scale
    longitude: float
    latitude: float
    renewable: bool
    regrowth_rate: float
    max_amount: float

class ResourceSystem:
    def __init__(self, world):
        self.world = world
        self.logger = get_logger(__name__)
        
        # Initialize resource maps
        self.mineral_map = {}
        self.water_map = {}
        self.vegetation_map = {}
        
        # Resource types and their properties
        self.mineral_types = {
            'iron': {'abundance': 0.1, 'value': 1.0},
            'copper': {'abundance': 0.05, 'value': 1.5},
            'gold': {'abundance': 0.01, 'value': 5.0},
            'coal': {'abundance': 0.15, 'value': 0.8},
            'oil': {'abundance': 0.08, 'value': 2.0}
        }
        
        self.vegetation_types = {
            'forest': {'density': 0.8, 'growth_rate': 0.1},
            'grassland': {'density': 0.5, 'growth_rate': 0.2},
            'desert': {'density': 0.1, 'growth_rate': 0.05},
            'tundra': {'density': 0.3, 'growth_rate': 0.08}
        }
        
        self.resources = {}  # (longitude, latitude) -> Dict[str, float]
        self.resource_regeneration_rate = 0.1  # Resources regenerate at 10% per tick
        self.resource_capacity = 1000  # Maximum amount of each resource
        self.discovered_resources: Set[ResourceType] = set()  # Track discovered resource types
        self.fishing_zones: Dict[Tuple[float, float], Dict] = {}  # (longitude, latitude) -> fishing data
        
        # Technology-based resource modifiers
        self.tech_efficiency_modifiers = {
            'mining': 1.0,
            'farming': 1.0,
            'fishing': 1.0,
            'processing': 1.0,
            'storage': 1.0
        }
        
        # Technology-based resource discovery requirements
        self.tech_discovery_requirements = {
            ResourceType.ORE: 'mining',
            ResourceType.TOOLS: 'toolmaking',
            ResourceType.WEAPONS: 'weaponmaking',
            ResourceType.MEDICINE: 'medicine',
            ResourceType.JEWELRY: 'metallurgy',
            ResourceType.ART: 'art',
            ResourceType.SPICES: 'cooking',
            ResourceType.WINE: 'fermentation',
            ResourceType.DRIED_FISH: 'preservation',
            ResourceType.FISH_OIL: 'processing',
            ResourceType.FISH_MEAL: 'processing',
            ResourceType.SHELL_CRAFT: 'crafting',
            ResourceType.SEAWEED_FERTILIZER: 'agriculture'
        }
        
        # Initialize resource requirements
        logger.info("Setting up resource requirements...")
        self.resource_requirements: Dict[ResourceType, List[Tuple[ResourceType, float]]] = {
            ResourceType.TOOLS: [(ResourceType.WOOD, 2), (ResourceType.STONE, 1)],
            ResourceType.WEAPONS: [(ResourceType.WOOD, 1), (ResourceType.STONE, 2)],
            ResourceType.CLOTHING: [(ResourceType.FIBER, 3)],
            ResourceType.SHELTER: [(ResourceType.WOOD, 5), (ResourceType.STONE, 2)],
            ResourceType.MEDICINE: [(ResourceType.FIBER, 2), (ResourceType.WATER, 1)],
            ResourceType.JEWELRY: [(ResourceType.ORE, 2)],
            ResourceType.ART: [(ResourceType.WOOD, 1), (ResourceType.STONE, 1)],
            ResourceType.SPICES: [(ResourceType.FIBER, 1)],
            ResourceType.WINE: [(ResourceType.WATER, 2), (ResourceType.FIBER, 1)],
            ResourceType.DRIED_FISH: [(ResourceType.FISH, 2)],
            ResourceType.FISH_OIL: [(ResourceType.FISH, 3)],
            ResourceType.FISH_MEAL: [(ResourceType.FISH, 1)],
            ResourceType.SHELL_CRAFT: [(ResourceType.SHELLFISH, 2)],
            ResourceType.SEAWEED_FERTILIZER: [(ResourceType.SEAWEED, 3)]
        }
        logger.info("Resource requirements initialized")
        
        # Initialize processing recipes
        logger.info("Setting up processing recipes...")
        self.processing_recipes = {}
        self._initialize_processing_recipes()
        logger.info("Processing recipes initialized")
        
        # Initialize basic resources as discovered
        logger.info("Setting up basic resources...")
        self.discovered_resources.update([
            ResourceType.FOOD,
            ResourceType.WATER,
            ResourceType.WOOD,
            ResourceType.STONE,
            ResourceType.FIBER,
            ResourceType.FISH,
            ResourceType.SHELLFISH,
            ResourceType.SEAWEED
        ])
        logger.info("Basic resources initialized")
        
        # Initialize resources after terrain is ready
        logger.info("Initializing resource distribution...")
        self.initialize_resources()
        logger.info("Resource distribution initialized")
        
        logger.info("Resource system initialized")
        
    def add_resource(self, resource: Resource) -> None:
        """Add a resource to the manager"""
        location = (resource.longitude, resource.latitude)
        if location not in self.resources:
            self.resources[location] = {}
        self.resources[location][resource.type] = resource
        
    def get_resource(self, longitude: float, latitude: float, resource_type: ResourceType) -> Optional[Resource]:
        """Get a resource at a specific location"""
        location = (longitude, latitude)
        return self.resources.get(location, {}).get(resource_type)
        
    def get_resources_at(self, lon: float, lat: float) -> Dict[str, float]:
        """Get resources at a specific location."""
        # Round coordinates to nearest degree
        lon_rounded = round(lon)
        lat_rounded = round(lat)
        return self.resources.get((lon_rounded, lat_rounded), {
            'water': 0.0,
            'food': 0.0,
            'wood': 0.0,
            'stone': 0.0,
            'metal': 0.0,
            'fertility': 0.0
        })
        
    def get_nearby_resources(self, longitude: float, latitude: float, radius: float) -> Dict[str, Dict[ResourceType, float]]:
        """Get resources within radius of location"""
        nearby = {}
        for dlon in np.arange(-radius, radius + self.world.longitude_resolution, self.world.longitude_resolution):
            for dlat in np.arange(-radius, radius + self.world.latitude_resolution, self.world.latitude_resolution):
                check_lon = longitude + dlon
                check_lat = latitude + dlat
                pos = (check_lon, check_lat)
                if pos in self.resources:
                    nearby[f"{check_lon},{check_lat}"] = {
                        str(resource_type): amount 
                        for resource_type, amount in self.resources[pos].items()
                    }
        return nearby
        
    def update_resources(self, lon: float, lat: float, resource_type: str, amount: float):
        """Update resource amount at a location."""
        lon_rounded = round(lon)
        lat_rounded = round(lat)
        if (lon_rounded, lat_rounded) in self.resources:
            self.resources[(lon_rounded, lat_rounded)][resource_type] = max(0.0, amount)
        
    def consume_resource(self, longitude: float, latitude: float, resource_type: ResourceType, amount: float) -> bool:
        """Consume a resource amount"""
        location = (longitude, latitude)
        resource = self.get_resource(longitude, latitude, resource_type)
        if not resource or resource.amount < amount:
            return False
            
        resource.amount -= amount
        if resource.amount <= 0:
            del self.resources[location][resource_type]
            if not self.resources[location]:
                del self.resources[location]
        return True
        
    def can_craft(self, resource_type: ResourceType, available_resources: Dict[ResourceType, float]) -> bool:
        """Check if a resource can be crafted with available resources"""
        if resource_type not in self.resource_requirements:
            return False
            
        for required_type, required_amount in self.resource_requirements[resource_type]:
            if available_resources.get(required_type, 0) < required_amount:
                return False
        return True
        
    def craft_resource(self, resource_type: ResourceType, longitude: float, latitude: float, quality: float = 0.5) -> bool:
        """Craft a new resource"""
        if resource_type not in self.resource_requirements:
            return False
            
        # Check if we have all required resources
        available_resources = self.get_resources_at(longitude, latitude)
        if not self.can_craft(resource_type, {r.type: r.amount for r in available_resources.values()}):
            return False
            
        # Consume required resources
        for required_type, required_amount in self.resource_requirements[resource_type]:
            if not self.consume_resource(longitude, latitude, required_type, required_amount):
                return False
                
        # Create new resource
        new_resource = Resource(
            type=resource_type,
            amount=1.0,
            quality=quality,
            longitude=longitude,
            latitude=latitude,
            renewable=False,
            regrowth_rate=0.0,
            max_amount=1.0
        )
        self.add_resource(new_resource)
        return True
        
    def get_resource_quality(self, longitude: float, latitude: float, resource_type: ResourceType) -> float:
        """Get the quality of a resource at a location"""
        resource = self.get_resource(longitude, latitude, resource_type)
        return resource.quality if resource else 0.0
        
    def improve_resource_quality(self, longitude: float, latitude: float, resource_type: ResourceType, amount: float) -> None:
        """Improve the quality of a resource"""
        resource = self.get_resource(longitude, latitude, resource_type)
        if resource:
            resource.quality = min(1.0, resource.quality + amount)
            
    def get_resource_stats(self) -> Dict[ResourceType, Dict[str, float]]:
        """Get statistics about all resources"""
        stats = {}
        for resource_type in ResourceType:
            total_amount = 0.0
            total_quality = 0.0
            count = 0
            
            for location_resources in self.resources.values():
                if resource_type in location_resources:
                    resource = location_resources[resource_type]
                    total_amount += resource.amount
                    total_quality += resource.quality
                    count += 1
                    
            if count > 0:
                stats[resource_type] = {
                    "total_amount": total_amount,
                    "average_quality": total_quality / count,
                    "locations": count
                }
            else:
                stats[resource_type] = {
                    "total_amount": 0.0,
                    "average_quality": 0.0,
                    "locations": 0
                }
                
        return stats

    def generate_resources(self, longitude: float, latitude: float, terrain_type: str):
        """Generate resources at a specific location based on terrain type."""
        # Round coordinates to nearest grid point
        lon_rounded = round(longitude / self.world.longitude_resolution) * self.world.longitude_resolution
        lat_rounded = round(latitude / self.world.latitude_resolution) * self.world.latitude_resolution
        
        # Initialize resource amounts based on terrain type
        resources = {
            'water': 0.0,
            'food': 0.0,
            'wood': 0.0,
            'stone': 0.0,
            'metal': 0.0
        }
        
        # Set resource amounts based on terrain type
        if terrain_type == 'water':
            resources['water'] = 1.0
            resources['food'] = random.uniform(0.3, 0.7)
        elif terrain_type == 'forest':
            resources['wood'] = random.uniform(0.6, 1.0)
            resources['food'] = random.uniform(0.4, 0.8)
        elif terrain_type == 'mountain':
            resources['stone'] = random.uniform(0.7, 1.0)
            resources['metal'] = random.uniform(0.5, 0.9)
        elif terrain_type == 'grassland':
            resources['food'] = random.uniform(0.5, 0.9)
            resources['water'] = random.uniform(0.3, 0.7)
        elif terrain_type == 'desert':
            resources['stone'] = random.uniform(0.3, 0.7)
            resources['metal'] = random.uniform(0.2, 0.6)
        
        # Store resources
        self.resources[(lon_rounded, lat_rounded)] = resources
        
    def discover_resource(self, resource_type: ResourceType, tech_name: Optional[str] = None) -> bool:
        """Discover a new resource type, requiring appropriate technology."""
        if resource_type in self.discovered_resources:
            return False
            
        # Check technology requirements
        required_tech = self.tech_discovery_requirements.get(resource_type)
        if required_tech and not self._has_required_tech(required_tech):
            return False
            
        self.discovered_resources.add(resource_type)
        self.logger.info(f"Discovered new resource type: {resource_type.value}")
        return True
        
    def _has_required_tech(self, tech_name: str) -> bool:
        """Check if required technology is available."""
        if not self.world.technology:
            return False
        return self.world.technology.get_tech_level(tech_name) > 0
        
    def gather_resource(self, longitude: float, latitude: float, resource_type: ResourceType, amount: float) -> float:
        """Gather a resource with technology-based efficiency."""
        # Get base gathering amount
        base_amount = super().gather_resource(longitude, latitude, resource_type, amount)
        
        # Apply technology modifier
        if resource_type in [ResourceType.ORE, ResourceType.STONE]:
            tech_modifier = self.tech_efficiency_modifiers['mining']
        elif resource_type in [ResourceType.FOOD, ResourceType.FIBER]:
            tech_modifier = self.tech_efficiency_modifiers['farming']
        elif resource_type in [ResourceType.FISH, ResourceType.SHELLFISH]:
            tech_modifier = self.tech_efficiency_modifiers['fishing']
        else:
            tech_modifier = 1.0
            
        return base_amount * tech_modifier
        
    def process_resource(self, resource_type: ResourceType, amount: float) -> Dict[ResourceType, float]:
        """Process a resource with technology-based efficiency."""
        # Get base processing results
        base_results = super().process_resource(resource_type, amount)
        
        # Apply technology modifier
        tech_modifier = self.tech_efficiency_modifiers['processing']
        
        # Scale results by technology level
        return {rtype: amount * tech_modifier for rtype, amount in base_results.items()}
        
    def check_fire_discovery(self, agent_intelligence: float, has_wood: bool, has_stone: bool) -> bool:
        """Check if an agent can discover fire"""
        if not has_wood or not has_stone:
            return False
            
        # Base chance of 1% plus intelligence bonus
        chance = 0.01 + (agent_intelligence * 0.05)
        return random.random() < chance
        
    def to_dict(self):
        """Convert resource system state to dictionary."""
        return {
            "resources": {
                str(loc): {
                    str(resource_type): {
                        "amount": resource.amount if hasattr(resource, 'amount') else resource.get('amount', 0.0),
                        "type": resource_type
                    }
                    for resource_type, resource in resources.items()
                }
                for loc, resources in self.resources.items()
            }
        }
        
    def update(self, time_delta: float) -> None:
        """Update resource states based on time delta"""
        # Update resource regeneration
        for location, resources in self.resources.items():
            for resource_type, resource in resources.items():
                # Skip non-renewable resources
                if not isinstance(resource, dict) or not resource.get('renewable', False):
                    continue
                    
                # Calculate regeneration
                regen_rate = self._get_regeneration_rate(resource_type)
                max_amount = self._get_max_amount(resource_type)
                current_amount = resource.get('amount', 0)
                
                # Regenerate resource
                new_amount = min(
                    current_amount + (regen_rate * time_delta),
                    max_amount
                )
                resource['amount'] = new_amount
        
        # Update fishing zones
        for zone in self.fishing_zones.values():
            if zone['active']:
                # Apply fishing technology modifier
                tech_modifier = self.tech_efficiency_modifiers.get('fishing', 1.0)
                zone['efficiency'] *= tech_modifier
                zone['last_update'] = time.time()
        
    def _update_tech_modifiers(self) -> None:
        """Update technology-based efficiency modifiers."""
        if not self.world.technology:
            return
            
        # Update mining efficiency
        mining_tech = self.world.technology.get_tech_level('mining')
        self.tech_efficiency_modifiers['mining'] = 1.0 + (mining_tech * 0.2)
        
        # Update farming efficiency
        farming_tech = self.world.technology.get_tech_level('agriculture')
        self.tech_efficiency_modifiers['farming'] = 1.0 + (farming_tech * 0.2)
        
        # Update fishing efficiency
        fishing_tech = self.world.technology.get_tech_level('fishing')
        self.tech_efficiency_modifiers['fishing'] = 1.0 + (fishing_tech * 0.2)
        
        # Update processing efficiency
        processing_tech = self.world.technology.get_tech_level('processing')
        self.tech_efficiency_modifiers['processing'] = 1.0 + (processing_tech * 0.2)
        
        # Update storage efficiency
        storage_tech = self.world.technology.get_tech_level('storage')
        self.tech_efficiency_modifiers['storage'] = 1.0 + (storage_tech * 0.2)

    def _get_regeneration_rate(self, resource_type: str) -> float:
        """Get the regeneration rate for a resource type"""
        rates = {
            "food": 0.2,
            "water": 0.1,
            "wood": 0.05,
            "stone": 0.0,
            "ore": 0.0,
            "fiber": 0.15,
            "fish": 0.2,
            "shellfish": 0.1,
            "seaweed": 0.15
        }
        return rates.get(resource_type, 0.0)
        
    def _get_max_amount(self, resource_type: str) -> float:
        """Get the maximum amount for a resource type"""
        max_amounts = {
            "food": 10.0,
            "water": 5.0,
            "wood": 20.0,
            "stone": 30.0,
            "ore": 10.0,
            "fiber": 8.0,
            "fish": 15.0,
            "shellfish": 8.0,
            "seaweed": 5.0
        }
        return max_amounts.get(resource_type, 1.0)
        
    def _initialize_processing_recipes(self) -> None:
        """Initialize resource processing recipes"""
        self.processing_recipes = {
            ResourceType.FISH: {
                ResourceType.DRIED_FISH: 0.5,
                ResourceType.FISH_OIL: 0.3,
                ResourceType.FISH_MEAL: 0.2
            },
            ResourceType.SHELLFISH: {
                ResourceType.SHELL_CRAFT: 0.7
            },
            ResourceType.SEAWEED: {
                ResourceType.SEAWEED_FERTILIZER: 0.8
            }
        }
        
    def get_state(self) -> Dict:
        """Get current resource system state."""
        return {
            'resources': self.resources
        }
        
    def initialize_resources(self):
        """Initialize all resource maps."""
        self.logger.info("Initializing resource system...")
        
        # Calculate total steps for progress tracking
        total_steps = (self.world.max_longitude - self.world.min_longitude) * \
                     (self.world.max_latitude - self.world.min_latitude)
        current_step = 0
        
        # Initialize resources for each coordinate
        for lon in range(int(self.world.min_longitude), int(self.world.max_longitude)):
            for lat in range(int(self.world.min_latitude), int(self.world.max_latitude)):
                coord = (lon, lat)
                
                # Initialize mineral resources
                self.mineral_map[coord] = self._generate_mineral_resources(coord)

                # Initialize water resources
                self.water_map[coord] = self._generate_water_resources(coord)

                # Initialize vegetation
                self.vegetation_map[coord] = self._generate_vegetation(coord)

                # Combine into unified resource mapping
                self.resources[coord] = {
                    'minerals': self.mineral_map[coord],
                    'water': self.water_map[coord],
                    'vegetation': self.vegetation_map[coord],
                }
                
                # Update progress
                current_step += 1
                if current_step % 100 == 0:
                    progress = (current_step / total_steps) * 100
                    self.logger.info(f"Resource initialization progress: {progress:.1f}%")
        
        self.logger.info("Resource system initialization complete")
    
    def _generate_mineral_resources(self, coord: Tuple[int, int]) -> Dict:
        """Generate mineral resources for a coordinate."""
        resources = {}
        for mineral, properties in self.mineral_types.items():
            # Use coordinate-based noise for resource distribution
            noise = np.random.normal(0, 1)
            abundance = properties['abundance'] * (1 + 0.2 * noise)
            if abundance > 0.5:  # Threshold for resource presence
                resources[mineral] = {
                    'amount': abundance,
                    'value': properties['value']
                }
        return resources
    
    def _generate_water_resources(self, coord: Tuple[int, int]) -> Dict:
        """Generate water resources for a coordinate."""
        # Base water availability on terrain and climate
        lon, lat = coord
        terrain = self.world.terrain.get_terrain_info_at(lon, lat)
        climate = self.world.climate.get_climate_at(lon, lat)
        
        water_amount = 0.0
        if terrain['type'] == 'ocean':
            water_amount = 1.0
        elif terrain['type'] == 'lake':
            water_amount = 0.8
        elif terrain['type'] == 'river':
            water_amount = 0.6
        else:
            # Adjust based on precipitation
            water_amount = climate['precipitation'] * 0.5
        
        return {
            'amount': water_amount,
            'type': terrain['type'] if water_amount > 0 else 'none'
        }
    
    def _generate_vegetation(self, coord: Tuple[int, int]) -> Dict:
        """Generate vegetation for a coordinate."""
        # Base vegetation on climate and terrain
        lon, lat = coord
        climate = self.world.climate.get_climate_at(lon, lat)
        terrain = self.world.terrain.get_terrain_info_at(lon, lat)
        
        if terrain['type'] in ['ocean', 'lake', 'river']:
            return {'type': 'none', 'density': 0.0}
        
        # Determine vegetation type based on temperature and precipitation
        temp = climate['temperature']
        precip = climate['precipitation']
        
        if temp < 0:
            veg_type = 'tundra'
        elif temp > 30 and precip < 0.2:
            veg_type = 'desert'
        elif precip > 0.6:
            veg_type = 'forest'
        else:
            veg_type = 'grassland'
        
        properties = self.vegetation_types[veg_type]
        return {
            'type': veg_type,
            'density': properties['density'],
            'growth_rate': properties['growth_rate']
        }

    def verify_initialization(self) -> bool:
        """Verify that the resource system is properly initialized."""
        logger.info("Verifying resource system initialization...")
        
        # Check resources dictionary
        if not hasattr(self, 'resources') or not self.resources:
            logger.error("Resources not initialized")
            return False
            
        # Check resource distribution
        if not hasattr(self, 'resource_distribution') or not self.resource_distribution:
            logger.error("Resource distribution not initialized")
            return False
            
        # Check resource regeneration
        if not hasattr(self, 'regeneration_rates') or not self.regeneration_rates:
            logger.error("Resource regeneration not initialized")
            return False
            
        # Check resource types
        required_types = {'water', 'food', 'wood', 'stone', 'metal'}
        if not all(resource_type in self.resources for resource_type in required_types):
            logger.error("Not all required resource types initialized")
            return False
            
        logger.info("Resource system initialization verified successfully")
        return True

    def _initialize_basic_resources(self):
        """Initialize basic resources across the world."""
        logger.info("Initializing basic resources...")
        for lon in np.arange(-180, 180, self.world.longitude_resolution):
            for lat in np.arange(-90, 90, self.world.latitude_resolution):
                terrain_type = self.world.terrain.get_terrain_type(lon, lat)
                self.generate_resources(lon, lat, terrain_type)
        logger.info("Basic resources initialized")

    def _initialize_resource_distribution(self):
        """Initialize resource distribution patterns."""
        logger.info("Initializing resource distribution patterns...")
        # Create resource clusters
        for _ in range(100):  # Create 100 resource clusters
            center_lon = random.uniform(-180, 180)
            center_lat = random.uniform(-90, 90)
            radius = random.uniform(1, 5)
            
            for dlon in np.arange(-radius, radius, 0.5):
                for dlat in np.arange(-radius, radius, 0.5):
                    lon = center_lon + dlon
                    lat = center_lat + dlat
                    if -180 <= lon <= 180 and -90 <= lat <= 90:
                        terrain_type = self.world.terrain.get_terrain_type(lon, lat)
                        self.generate_resources(lon, lat, terrain_type)
        logger.info("Resource distribution patterns initialized")

    def _initialize_resource_regeneration(self):
        """Initialize resource regeneration settings."""
        logger.info("Initializing resource regeneration settings...")
        self.resource_regeneration_rate = 0.1  # 10% per tick
        self.resource_capacity = 1000  # Maximum amount per resource
        logger.info("Resource regeneration settings initialized")

    def _initialize_fishing_zones(self):
        """Initialize fishing zones in coastal areas."""
        logger.info("Initializing fishing zones...")
        for lon in np.arange(-180, 180, self.world.longitude_resolution):
            for lat in np.arange(-90, 90, self.world.latitude_resolution):
                if self.world.terrain.is_coastal(lon, lat):
                    self.create_fishing_zone(
                        lon, lat,
                        intensity=random.uniform(0.5, 1.0),
                        method="net",
                        efficiency=random.uniform(0.7, 1.0)
                    )
        logger.info("Fishing zones initialized")

    def _initialize_resource_processing(self):
        """Initialize resource processing capabilities."""
        logger.info("Initializing resource processing...")
        # Basic processing
        self.processing_recipes.update({
            ResourceType.DRIED_FISH: {
                "inputs": {ResourceType.FISH: 2},
                "outputs": {ResourceType.DRIED_FISH: 1},
                "time": 1.0
            },
            ResourceType.FISH_OIL: {
                "inputs": {ResourceType.FISH: 3},
                "outputs": {ResourceType.FISH_OIL: 1},
                "time": 2.0
            }
        })
        
        # Advanced processing
        self.processing_recipes.update({
            ResourceType.SHELL_CRAFT: {
                "inputs": {ResourceType.SHELLFISH: 2},
                "outputs": {ResourceType.SHELL_CRAFT: 1},
                "time": 1.5
            },
            ResourceType.SEAWEED_FERTILIZER: {
                "inputs": {ResourceType.SEAWEED: 3},
                "outputs": {ResourceType.SEAWEED_FERTILIZER: 1},
                "time": 2.0
            }
        })
        logger.info("Resource processing initialized")

    def _initialize_marine_processing(self):
        """Initialize marine resource processing capabilities."""
        logger.info("Initializing marine resource processing...")
        self.processing_recipes.update({
            ResourceType.PEARL: {
                "inputs": {ResourceType.SHELLFISH: 5},
                "outputs": {ResourceType.PEARL: 1},
                "time": 3.0
            },
            ResourceType.CORAL: {
                "inputs": {ResourceType.SEAWEED: 4},
                "outputs": {ResourceType.CORAL: 1},
                "time": 2.5
            }
        })
        logger.info("Marine resource processing initialized")

    def _initialize_advanced_processing(self):
        """Initialize advanced resource processing capabilities."""
        logger.info("Initializing advanced resource processing...")
        self.processing_recipes.update({
            ResourceType.TOOLS: {
                "inputs": {ResourceType.WOOD: 2, ResourceType.STONE: 1},
                "outputs": {ResourceType.TOOLS: 1},
                "time": 2.0
            },
            ResourceType.WEAPONS: {
                "inputs": {ResourceType.WOOD: 1, ResourceType.STONE: 2},
                "outputs": {ResourceType.WEAPONS: 1},
                "time": 2.5
            }
        })
        logger.info("Advanced resource processing initialized")

    def _initialize_basic_processing(self):
        """Initialize basic resource processing capabilities."""
        logger.info("Initializing basic resource processing...")
        self.processing_recipes.update({
            ResourceType.CLOTHING: {
                "inputs": {ResourceType.FIBER: 3},
                "outputs": {ResourceType.CLOTHING: 1},
                "time": 1.0
            },
            ResourceType.SHELTER: {
                "inputs": {ResourceType.WOOD: 5, ResourceType.STONE: 2},
                "outputs": {ResourceType.SHELTER: 1},
                "time": 3.0
            }
        })
        logger.info("Basic resource processing initialized")

    def create_fishing_zone(self, longitude: float, latitude: float, intensity: float = 1.0, method: str = "net", efficiency: float = 1.0):
        """Create a new fishing zone"""
        location = (longitude, latitude)
        self.fishing_zones[location] = {
            "intensity": intensity,
            "method": method,
            "efficiency": efficiency,
            "fish_amount": 10.0 * intensity,
            "max_fish": 20.0 * intensity,
            "regeneration_rate": 0.2 * intensity,
            "regeneration_time": 1.0,
            "time_since_last_fish": 0.0
        }
        
    def remove_fishing_zone(self, longitude: float, latitude: float):
        """Remove a fishing zone"""
        location = (longitude, latitude)
        if location in self.fishing_zones:
            del self.fishing_zones[location]
            
    def get_fishing_yield(self, longitude: float, latitude: float, time_delta: float) -> Dict[ResourceType, float]:
        """Get fishing yield from a location"""
        location = (longitude, latitude)
        if location not in self.fishing_zones:
            return {}
            
        zone = self.fishing_zones[location]
        if zone["fish_amount"] <= 0:
            return {}
            
        # Calculate yield based on method and efficiency
        yield_amount = min(
            zone["fish_amount"],
            time_delta * zone["efficiency"] * zone["intensity"]
        )
        
        zone["fish_amount"] -= yield_amount
        
        return {
            ResourceType.FISH: yield_amount
        }
        
    def process_marine_resource(self, resource_type: ResourceType, amount: float) -> Dict[ResourceType, float]:
        """Process a marine resource into other resources"""
        if resource_type not in self.processing_recipes:
            return {}
            
        recipe = self.processing_recipes[resource_type]
        results = {}
        
        for result_type, result_amount in recipe.items():
            results[result_type] = result_amount * amount
            
        return results