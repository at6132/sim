from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import uuid
import time
import random

@dataclass
class BuildingState:
    construction_progress: float = 0.0  # 0-100
    durability: float = 100.0  # 0-100
    last_maintenance: float = 0.0
    maintenance_needed: bool = False
    construction_materials: Dict[str, float] = field(default_factory=dict)
    construction_workers: List[str] = field(default_factory=list)

class BuildingSystem:
    def __init__(self):
        self.buildings: Dict[str, Building] = {}
        self.building_states: Dict[str, BuildingState] = {}
        self.construction_queue: List[Tuple[str, str, Dict[str, float]]] = []  # (building_type, location, materials)
        
    def update(self, time_delta: float, world_state: Dict):
        """Update building states and handle construction."""
        # Update existing buildings
        for building_id, building in list(self.buildings.items()):
            state = self.building_states[building_id]
            
            # Handle construction
            if state.construction_progress < 100.0:
                self._update_construction(building, state, time_delta, world_state)
                continue
                
            # Update durability
            self._update_durability(building, state, time_delta)
            
            # Check for maintenance
            if state.maintenance_needed:
                self._handle_maintenance(building, state, time_delta)
                
    def _update_construction(self, building: Building, state: BuildingState, time_delta: float, world_state: Dict):
        """Update construction progress."""
        if not state.construction_workers:
            return
            
        # Calculate construction speed based on workers
        worker_count = len(state.construction_workers)
        construction_speed = 0.1 * worker_count  # Base speed per worker
        
        # Apply worker skills
        for worker_id in state.construction_workers:
            worker = world_state["agents"].get(worker_id)
            if worker:
                construction_speed *= (1.0 + worker.skills.get("construction", 0.0))
                
        # Update progress
        state.construction_progress += construction_speed * time_delta
        
        # Check if construction is complete
        if state.construction_progress >= 100.0:
            state.construction_progress = 100.0
            state.durability = 100.0
            state.last_maintenance = time.time()
            state.construction_materials.clear()
            state.construction_workers.clear()
            
            # Log completion
            self.world.log_event("building_completed", {
                "building_id": building.id,
                "building_type": building.type,
                "location": building.position
            })
            
    def _update_durability(self, building: Building, state: BuildingState, time_delta: float):
        """Update building durability."""
        # Natural decay
        decay_rate = 0.01 * time_delta  # Base decay rate
        
        # Environmental factors
        if self.world.weather.is_raining:
            decay_rate *= 1.5
        if self.world.weather.is_storming:
            decay_rate *= 2.0
            
        # Apply decay
        state.durability -= decay_rate
        
        # Check for maintenance needed
        if state.durability < 70.0 and not state.maintenance_needed:
            state.maintenance_needed = True
            self.world.log_event("building_maintenance_needed", {
                "building_id": building.id,
                "building_type": building.type,
                "durability": state.durability
            })
            
        # Check for critical damage
        if state.durability < 30.0:
            self.world.log_event("building_critical_damage", {
                "building_id": building.id,
                "building_type": building.type,
                "durability": state.durability
            })
            
        # Check for collapse
        if state.durability <= 0.0:
            self._handle_building_collapse(building)
            
    def _handle_maintenance(self, building: Building, state: BuildingState, time_delta: float):
        """Handle building maintenance."""
        # Find available workers
        available_workers = [
            agent for agent in self.world.agents.get_all()
            if agent.skills.get("construction", 0.0) > 0.0
            and agent.needs.energy > 0.5
        ]
        
        if not available_workers:
            return
            
        # Calculate maintenance speed
        maintenance_speed = 0.0
        for worker in available_workers:
            maintenance_speed += 0.05 * worker.skills["construction"]
            
        # Apply maintenance
        repair_amount = maintenance_speed * time_delta
        state.durability = min(100.0, state.durability + repair_amount)
        
        # Check if maintenance is complete
        if state.durability >= 90.0:
            state.maintenance_needed = False
            state.last_maintenance = time.time()
            self.world.log_event("building_maintenance_completed", {
                "building_id": building.id,
                "building_type": building.type,
                "durability": state.durability
            })
            
    def _handle_building_collapse(self, building: Building):
        """Handle building collapse."""
        # Log collapse
        self.world.log_event("building_collapsed", {
            "building_id": building.id,
            "building_type": building.type,
            "location": building.position
        })
        
        # Remove building
        del self.buildings[building.id]
        del self.building_states[building.id]
        
        # Create debris
        self._create_debris(building)
        
    def _create_debris(self, building: Building):
        """Create debris from collapsed building."""
        debris_type = random.choice(["wood", "stone", "metal"])
        debris_amount = random.uniform(0.5, 1.0) * building.size
        
        # Create resource
        resource = Resource(
            type=debris_type,
            amount=debris_amount,
            position=building.position,
            quality=0.5  # Damaged materials
        )
        
        self.world.resources.add(resource)
        
    def start_construction(self, building_type: str, position: Tuple[float, float], materials: Dict[str, float]) -> Optional[str]:
        """Start construction of a new building."""
        # Validate materials
        if not self._validate_materials(building_type, materials):
            return None
            
        # Create building
        building = Building(
            id=str(uuid.uuid4()),
            type=building_type,
            position=position,
            size=1.0,  # Default size
            capacity=10  # Default capacity
        )
        
        # Create building state
        state = BuildingState(
            construction_progress=0.0,
            durability=100.0,
            last_maintenance=time.time(),
            construction_materials=materials.copy()
        )
        
        # Add to system
        self.buildings[building.id] = building
        self.building_states[building.id] = state
        
        # Log construction start
        self.world.log_event("building_construction_started", {
            "building_id": building.id,
            "building_type": building_type,
            "location": position,
            "materials": materials
        })
        
        return building.id
        
    def _validate_materials(self, building_type: str, materials: Dict[str, float]) -> bool:
        """Validate if provided materials are sufficient for construction."""
        required_materials = self._get_required_materials(building_type)
        
        for material, amount in required_materials.items():
            if material not in materials or materials[material] < amount:
                return False
                
        return True
        
    def _get_required_materials(self, building_type: str) -> Dict[str, float]:
        """Get required materials for a building type."""
        # Define material requirements for different building types
        requirements = {
            "hut": {
                "wood": 10.0,
                "stone": 5.0
            },
            "house": {
                "wood": 20.0,
                "stone": 15.0,
                "metal": 5.0
            },
            "storage": {
                "wood": 15.0,
                "stone": 10.0
            },
            "workshop": {
                "wood": 25.0,
                "stone": 20.0,
                "metal": 10.0
            }
        }
        
        return requirements.get(building_type, {})
        
    def assign_worker(self, building_id: str, worker_id: str) -> bool:
        """Assign a worker to construction."""
        if building_id not in self.buildings:
            return False
            
        state = self.building_states[building_id]
        if state.construction_progress >= 100.0:
            return False
            
        if worker_id not in state.construction_workers:
            state.construction_workers.append(worker_id)
            return True
            
        return False
        
    def remove_worker(self, building_id: str, worker_id: str) -> bool:
        """Remove a worker from construction."""
        if building_id not in self.buildings:
            return False
            
        state = self.building_states[building_id]
        if worker_id in state.construction_workers:
            state.construction_workers.remove(worker_id)
            return True
            
        return False
        
    def to_dict(self) -> Dict:
        """Convert system state to dictionary."""
        return {
            'buildings': {
                building_id: {
                    'type': building.type,
                    'position': building.position,
                    'size': building.size,
                    'capacity': building.capacity,
                    'state': {
                        'construction_progress': state.construction_progress,
                        'durability': state.durability,
                        'last_maintenance': state.last_maintenance,
                        'maintenance_needed': state.maintenance_needed,
                        'construction_materials': state.construction_materials,
                        'construction_workers': state.construction_workers
                    }
                }
                for building_id, building in self.buildings.items()
                for state in [self.building_states[building_id]]
            }
        } 