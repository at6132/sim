from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import random
import logging
import time
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    SICK = "sick"
    INJURED = "injured"
    CRITICAL = "critical"
    DEAD = "dead"

class DiseaseType(Enum):
    VIRAL = "viral"
    BACTERIAL = "bacterial"
    FUNGAL = "fungal"
    PARASITIC = "parasitic"
    GENETIC = "genetic"
    ENVIRONMENTAL = "environmental"
    NUTRITIONAL = "nutritional"
    MENTAL = "mental"

class TreatmentType(Enum):
    MEDICATION = "medication"
    SURGERY = "surgery"
    THERAPY = "therapy"
    PREVENTION = "prevention"
    VACCINATION = "vaccination"
    LIFESTYLE = "lifestyle"
    ALTERNATIVE = "alternative"

@dataclass
class Disease:
    name: str
    type: DiseaseType
    description: str
    symptoms: List[str]
    transmission_rate: float
    mortality_rate: float
    recovery_rate: float
    incubation_period: float
    duration: float
    immunity_duration: float
    affected_systems: Set[str] = field(default_factory=set)
    treatments: Dict[str, float] = field(default_factory=dict)  # treatment: effectiveness
    mutations: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

@dataclass
class HealthCondition:
    type: str  # Emergent condition type
    name: str
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent conditions
    symptoms: Dict[str, Any] = field(default_factory=dict)  # Condition symptoms
    effects: Dict[str, Any] = field(default_factory=dict)  # Condition effects
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

@dataclass
class Treatment:
    type: str  # Emergent treatment type
    name: str
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent treatments
    requirements: Dict[str, Any] = field(default_factory=dict)  # Treatment requirements
    effects: Dict[str, Any] = field(default_factory=dict)  # Treatment effects
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

@dataclass
class MedicalEvolution:
    type: str  # Emergent evolution type
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent evolution
    conditions: Dict[str, Any] = field(default_factory=dict)  # Evolution conditions
    effects: Dict[str, Any] = field(default_factory=dict)  # Evolution effects
    created_at: float = field(default_factory=time.time)

@dataclass
class HealthcareFacility:
    name: str
    type: str
    capacity: int
    staff: Set[str] = field(default_factory=set)
    patients: Set[str] = field(default_factory=set)
    treatments: Dict[str, Treatment] = field(default_factory=dict)
    resources: Dict[str, float] = field(default_factory=dict)
    efficiency: float = 1.0
    created_at: float = field(default_factory=time.time)

class HealthSystem:
    def __init__(self, world):
        """Initialize the health system."""
        self.world = world
        self.diseases: Dict[str, Disease] = {}
        self.conditions: Dict[str, HealthCondition] = {}
        self.treatments: Dict[str, Treatment] = {}
        self.evolutions: Dict[str, MedicalEvolution] = {}
        self.facilities: Dict[str, HealthcareFacility] = {}
        self.medical_knowledge: Dict[DiseaseType, float] = {dtype: 0.0 for dtype in DiseaseType}
        self.logger = get_logger(__name__)
        self.initialize_system()
        
    def initialize_system(self):
        """Initialize the health system with basic capabilities."""
        self.logger.info("Initializing health system...")
        
        # Create basic healthcare facilities
        self.facilities["main_hospital"] = HealthcareFacility(
            name="Main Hospital",
            type="hospital",
            capacity=100
        )
        
        # Initialize basic diseases
        self._initialize_basic_diseases()
        
        # Initialize basic health conditions
        self._initialize_basic_conditions()
        
        # Initialize basic treatments
        self._initialize_basic_treatments()
        
        # Initialize medical knowledge
        self._initialize_medical_knowledge()
        
        self.logger.info("Health system initialization complete")
        
    def _initialize_basic_diseases(self):
        """Initialize basic diseases."""
        # Common cold
        self.diseases["common_cold"] = Disease(
            name="Common Cold",
            type=DiseaseType.VIRAL,
            description="A mild viral infection of the upper respiratory tract",
            symptoms=["runny nose", "sore throat", "cough", "sneezing"],
            transmission_rate=0.3,
            mortality_rate=0.001,
            recovery_rate=0.1,
            incubation_period=2.0,
            duration=7.0,
            immunity_duration=30.0
        )
        
        # Influenza
        self.diseases["influenza"] = Disease(
            name="Influenza",
            type=DiseaseType.VIRAL,
            description="A contagious respiratory illness caused by influenza viruses",
            symptoms=["fever", "cough", "sore throat", "muscle aches", "fatigue"],
            transmission_rate=0.4,
            mortality_rate=0.01,
            recovery_rate=0.05,
            incubation_period=2.0,
            duration=14.0,
            immunity_duration=180.0
        )
        
        # Bacterial infection
        self.diseases["bacterial_infection"] = Disease(
            name="Bacterial Infection",
            type=DiseaseType.BACTERIAL,
            description="An infection caused by harmful bacteria",
            symptoms=["fever", "inflammation", "pain", "fatigue"],
            transmission_rate=0.2,
            mortality_rate=0.05,
            recovery_rate=0.08,
            incubation_period=3.0,
            duration=10.0,
            immunity_duration=90.0
        )
        
    def _initialize_basic_conditions(self):
        """Initialize basic health conditions."""
        # Create a basic health condition - but don't prescribe its type
        self.conditions["initial_condition"] = HealthCondition(
            type="emergent",  # Let the simulation determine the type
            name="Initial Condition",
            description="Primary health condition"
        )
        
    def _initialize_basic_treatments(self):
        """Initialize basic treatments."""
        # Basic medication
        self.treatments["basic_medication"] = Treatment(
            type="medication",
            name="Basic Medication",
            description="Simple medicinal compounds for treating common ailments",
            properties={"herbs": 1.0},
            requirements={},
            effects={"effectiveness": 0.3, "side_effects": ["nausea", "drowsiness"]},
            created_at=time.time(),
            last_used=time.time()
        )
        
        # Basic surgery
        self.treatments["basic_surgery"] = Treatment(
            type="surgery",
            name="Basic Surgery",
            description="Simple surgical procedures for treating injuries and conditions",
            properties={"tools": 1.0, "bandages": 1.0},
            requirements={},
            effects={"effectiveness": 0.5, "side_effects": ["pain", "infection risk"]},
            created_at=time.time(),
            last_used=time.time()
        )
        
    def _initialize_medical_knowledge(self):
        """Initialize basic medical knowledge."""
        self.logger.info("Initializing medical knowledge...")
        
        # Define basic medical knowledge
        basic_knowledge = {
            "wound_care": {
                "name": "Wound Care",
                "level": 0.3,
                "treatments": ["basic_medication"],
                "conditions": ["initial_condition"]
            },
            "herbal_remedies": {
                "name": "Herbal Remedies",
                "level": 0.4,
                "treatments": ["basic_medication"],
                "conditions": ["common_cold", "influenza"]
            },
            "bone_setting": {
                "name": "Bone Setting",
                "level": 0.2,
                "treatments": ["basic_surgery"],
                "conditions": ["bacterial_infection"]
            }
        }
        
        # Add medical knowledge to system
        for knowledge_id, knowledge_data in basic_knowledge.items():
            self.medical_knowledge[knowledge_id] = knowledge_data
            self.logger.info(f"Added medical knowledge: {knowledge_data['name']}")
        
    def create_disease(self, name: str, type: DiseaseType, description: str,
                      symptoms: List[str], transmission_rate: float, mortality_rate: float,
                      recovery_rate: float, incubation_period: float, duration: float,
                      immunity_duration: float) -> Disease:
        """Create a new disease."""
        if name in self.diseases:
            logger.warning(f"Disease {name} already exists")
            return self.diseases[name]
            
        disease = Disease(
            name=name,
            type=type,
            description=description,
            symptoms=symptoms,
            transmission_rate=transmission_rate,
            mortality_rate=mortality_rate,
            recovery_rate=recovery_rate,
            incubation_period=incubation_period,
            duration=duration,
            immunity_duration=immunity_duration
        )
        
        self.diseases[name] = disease
        logger.info(f"Created new disease: {name}")
        return disease
        
    def create_condition(self, type: str, name: str, description: str,
                        properties: Dict[str, Any] = None) -> HealthCondition:
        """Create new health condition with custom properties."""
        condition = HealthCondition(
            type=type,
            name=name,
            description=description,
            properties=properties or {}
        )
        
        condition_id = f"condition_{len(self.conditions)}"
        self.conditions[condition_id] = condition
        logger.info(f"Created new health condition: {name} of type {type}")
        return condition
        
    def create_treatment(self, type: str, name: str, description: str,
                        properties: Dict[str, Any] = None) -> Treatment:
        """Create new treatment with custom properties."""
        treatment = Treatment(
            type=type,
            name=name,
            description=description,
            properties=properties or {}
        )
        
        treatment_id = f"treatment_{len(self.treatments)}"
        self.treatments[treatment_id] = treatment
        logger.info(f"Created new treatment: {name} of type {type}")
        return treatment
        
    def create_evolution(self, type: str, description: str,
                        properties: Dict[str, Any] = None,
                        conditions: Dict[str, Any] = None,
                        effects: Dict[str, Any] = None) -> MedicalEvolution:
        """Create new medical evolution with custom properties."""
        evolution = MedicalEvolution(
            type=type,
            description=description,
            properties=properties or {},
            conditions=conditions or {},
            effects=effects or {}
        )
        
        evolution_id = f"evolution_{len(self.evolutions)}"
        self.evolutions[evolution_id] = evolution
        logger.info(f"Created new medical evolution of type {type}")
        return evolution
        
    def create_healthcare_facility(self, name: str, type: str, capacity: int) -> HealthcareFacility:
        """Create a new healthcare facility."""
        if name in self.facilities:
            logger.warning(f"Facility {name} already exists")
            return self.facilities[name]
            
        facility = HealthcareFacility(
            name=name,
            type=type,
            capacity=capacity
        )
        
        self.facilities[name] = facility
        logger.info(f"Created new healthcare facility: {name}")
        return facility
        
    def apply_treatment(self, facility: str, patient: str, treatment: str) -> bool:
        """Apply a treatment to a patient."""
        if facility not in self.facilities:
            logger.error(f"Facility {facility} does not exist")
            return False
            
        if treatment not in self.treatments:
            logger.error(f"Treatment {treatment} does not exist")
            return False
            
        if patient not in self.facilities[facility].patients:
            logger.error(f"Patient {patient} is not in facility {facility}")
            return False
            
        # Check if facility has required resources
        treatment_obj = self.treatments[treatment]
        for resource, amount in treatment_obj.requirements.items():
            if resource not in self.facilities[facility].resources or \
               self.facilities[facility].resources[resource] < amount:
                logger.error(f"Facility {facility} lacks required resources for {treatment}")
                return False
                
        # Apply treatment
        for resource, amount in treatment_obj.requirements.items():
            self.facilities[facility].resources[resource] -= amount
            
        # Update patient health
        self.world.agents[patient].apply_treatment(treatment_obj)
        
        logger.info(f"Applied treatment {treatment} to patient {patient} at {facility}")
        return True
        
    def update_health(self, time_delta: float):
        """Update health state."""
        # Let the simulation determine how health evolves
        self._update_health_conditions(time_delta)
        
        # Update treatments based on emergent rules
        self._update_treatments(time_delta)
        
        # Check for emergent health events
        self._check_health_events(time_delta)
        
    def _update_health_conditions(self, time_delta: float):
        """Update health conditions over time."""
        for condition_id, condition in self.conditions.items():
            # Update condition properties based on time
            for prop, value in condition.properties.items():
                if isinstance(value, (int, float)):
                    # Apply natural progression
                    condition.properties[prop] = value * (1 + random.uniform(-0.1, 0.1) * time_delta)
            
            # Update symptoms
            for symptom, severity in condition.symptoms.items():
                if isinstance(severity, (int, float)):
                    # Apply symptom progression
                    condition.symptoms[symptom] = severity * (1 + random.uniform(-0.2, 0.2) * time_delta)
            
            # Update effects
            for effect, magnitude in condition.effects.items():
                if isinstance(magnitude, (int, float)):
                    # Apply effect progression
                    condition.effects[effect] = magnitude * (1 + random.uniform(-0.15, 0.15) * time_delta)
            
            # Update timestamp
            condition.last_update = time.time()

    def _update_treatments(self, time_delta: float):
        """Update treatments over time."""
        for treatment_id, treatment in self.treatments.items():
            # Update treatment properties
            for prop, value in treatment.properties.items():
                if isinstance(value, (int, float)):
                    # Apply treatment evolution
                    treatment.properties[prop] = value * (1 + random.uniform(-0.05, 0.1) * time_delta)
            
            # Update requirements
            for req, value in treatment.requirements.items():
                if isinstance(value, (int, float)):
                    # Apply requirement changes
                    treatment.requirements[req] = value * (1 + random.uniform(-0.1, 0.05) * time_delta)
            
            # Update effects
            for effect, magnitude in treatment.effects.items():
                if isinstance(magnitude, (int, float)):
                    # Apply effect changes
                    treatment.effects[effect] = magnitude * (1 + random.uniform(-0.1, 0.1) * time_delta)
            
            # Update timestamp
            treatment.last_used = time.time()

    def _check_health_events(self, time_delta: float):
        """Check for health-related events."""
        # Check for disease outbreaks
        for disease_id, disease in self.diseases.items():
            if random.random() < disease.transmission_rate * time_delta:
                # Simulate disease spread
                self._simulate_disease_spread(disease)
        
        # Check for treatment effectiveness
        for treatment_id, treatment in self.treatments.items():
            if random.random() < 0.1 * time_delta:  # 10% chance per time unit
                # Simulate treatment evolution
                self._simulate_treatment_evolution(treatment)
        
        # Check for medical breakthroughs
        if random.random() < 0.05 * time_delta:  # 5% chance per time unit
            # Simulate medical discovery
            self._simulate_medical_discovery()

    def _simulate_disease_spread(self, disease: Disease):
        """Simulate the spread of a disease."""
        # Calculate spread probability based on disease properties
        spread_chance = disease.transmission_rate * (1 + random.uniform(-0.2, 0.2))
        
        # Simulate spread to nearby agents
        for agent in self.world.agents:
            if random.random() < spread_chance:
                # Check immunity
                if disease.name not in agent.health.immunity:
                    # Apply disease
                    agent.health.diseases.append(disease)
                    self.logger.info(f"Disease {disease.name} spread to agent {agent.id}")

    def _simulate_treatment_evolution(self, treatment: Treatment):
        """Simulate the evolution of a treatment."""
        # Randomly improve or modify treatment properties
        for prop, value in treatment.properties.items():
            if isinstance(value, (int, float)):
                # Apply random improvement
                treatment.properties[prop] = value * (1 + random.uniform(0, 0.2))
        
        # Update treatment effects
        for effect, magnitude in treatment.effects.items():
            if isinstance(magnitude, (int, float)):
                # Apply random improvement
                treatment.effects[effect] = magnitude * (1 + random.uniform(0, 0.15))
        
        self.logger.info(f"Treatment {treatment.name} evolved")

    def _simulate_medical_discovery(self):
        """Simulate a medical discovery."""
        # Randomly select a disease type to improve knowledge of
        disease_type = random.choice(list(DiseaseType))
        
        # Improve medical knowledge
        self.medical_knowledge[disease_type] = min(
            1.0,
            self.medical_knowledge[disease_type] + random.uniform(0.1, 0.3)
        )
        
        self.logger.info(f"Medical discovery in {disease_type.value} field")
        
    def update(self, time_delta: float):
        """Update health system state."""
        # Update conditions
        self._update_health_conditions(time_delta)
        
        # Update treatments
        self._update_treatments(time_delta)
        
        # Check for events
        self._check_health_events(time_delta)
        
        # Update healthcare facilities
        self._update_healthcare_facilities(time_delta)
        
        # Update medical knowledge
        self._update_medical_knowledge(time_delta)
        
    def _update_healthcare_facilities(self, time_delta: float):
        """Update healthcare facility states."""
        for facility in self.facilities.values():
            # Update patient care
            for patient_id in facility.patients:
                self._update_patient_care(facility, patient_id, time_delta)
                
            # Update resource consumption
            self._update_facility_resources(facility, time_delta)
            
            # Update efficiency
            self._update_facility_efficiency(facility, time_delta)
            
    def _update_patient_care(self, facility: HealthcareFacility, patient_id: str, time_delta: float):
        """Update care for a patient in a facility."""
        agent = self.world.agents[patient_id]
        
        # Apply treatments
        for treatment in facility.treatments.values():
            if random.random() < treatment.effects["effectiveness"] * time_delta:
                agent.apply_treatment(treatment)
                
        # Check for discharge
        if agent.health >= 0.8:  # Healthy enough to leave
            facility.patients.remove(patient_id)
            
    def _update_facility_resources(self, facility: HealthcareFacility, time_delta: float):
        """Update resource consumption in a facility."""
        for resource, amount in facility.resources.items():
            # Consume resources based on patient load
            consumption = amount * len(facility.patients) * time_delta
            facility.resources[resource] = max(0.0, amount - consumption)
            
    def _update_facility_efficiency(self, facility: HealthcareFacility, time_delta: float):
        """Update facility efficiency."""
        # Factors affecting efficiency:
        # 1. Staff-to-patient ratio
        # 2. Resource availability
        # 3. Facility age
        # 4. Technology level
        
        staff_ratio = len(facility.staff) / max(1, len(facility.patients))
        resource_factor = min(1.0, sum(facility.resources.values()) / 100.0)
        age_factor = 1.0 / (1.0 + (time.time() - facility.created_at) / 31536000.0)  # Decay over years
        
        efficiency = (staff_ratio * 0.4 + resource_factor * 0.3 + age_factor * 0.3)
        facility.efficiency = max(0.1, min(1.0, efficiency))
        
    def _update_medical_knowledge(self, time_delta: float):
        """Update medical knowledge based on research and experience."""
        for disease_type in DiseaseType:
            # Increase knowledge based on:
            # 1. Research progress
            # 2. Treatment effectiveness
            # 3. Disease observations
            # 4. Medical facilities
            
            research_factor = self.world.science.get_field_knowledge(disease_type.value)
            treatment_factor = self._get_treatment_effectiveness(disease_type)
            observation_factor = self._get_disease_observations(disease_type)
            facility_factor = self._get_medical_facility_contribution()
            
            knowledge_gain = (research_factor * 0.4 + treatment_factor * 0.3 +
                            observation_factor * 0.2 + facility_factor * 0.1) * time_delta
            
            self.medical_knowledge[disease_type] = min(1.0, 
                self.medical_knowledge[disease_type] + knowledge_gain)
            
    def _get_treatment_effectiveness(self, disease_type: DiseaseType) -> float:
        """Calculate treatment effectiveness for a disease type."""
        effectiveness = 0.0
        count = 0
        
        for disease in self.diseases.values():
            if disease.type == disease_type:
                for treatment in disease.treatments.values():
                    effectiveness += treatment
                    count += 1
                    
        return effectiveness / max(1, count)
        
    def _get_disease_observations(self, disease_type: DiseaseType) -> float:
        """Calculate disease observation factor."""
        observations = 0
        total_cases = 0
        
        for disease in self.diseases.values():
            if disease.type == disease_type:
                cases = len(self._get_affected_population(disease))
                observations += cases
                total_cases += cases
                
        return observations / max(1, total_cases)
        
    def _get_medical_facility_contribution(self) -> float:
        """Calculate contribution of medical facilities to knowledge."""
        return sum(facility.efficiency for facility in self.facilities.values()) / max(1, len(self.facilities))
        
    def to_dict(self) -> Dict:
        """Convert health system state to dictionary for serialization."""
        return {
            "diseases": {
                name: {
                    "name": disease.name,
                    "type": disease.type.value,
                    "description": disease.description,
                    "symptoms": disease.symptoms,
                    "transmission_rate": disease.transmission_rate,
                    "mortality_rate": disease.mortality_rate,
                    "recovery_rate": disease.recovery_rate,
                    "incubation_period": disease.incubation_period,
                    "duration": disease.duration,
                    "immunity_duration": disease.immunity_duration,
                    "affected_systems": list(disease.affected_systems),
                    "treatments": disease.treatments,
                    "mutations": disease.mutations,
                    "created_at": disease.created_at
                }
                for name, disease in self.diseases.items()
            },
            "conditions": {
                condition_id: {
                    "type": condition.type,
                    "name": condition.name,
                    "description": condition.description,
                    "properties": condition.properties,
                    "symptoms": condition.symptoms,
                    "effects": condition.effects,
                    "created_at": condition.created_at,
                    "last_update": condition.last_update
                }
                for condition_id, condition in self.conditions.items()
            },
            "treatments": {
                treatment_id: {
                    "type": treatment.type,
                    "name": treatment.name,
                    "description": treatment.description,
                    "properties": treatment.properties,
                    "requirements": treatment.requirements,
                    "effects": treatment.effects,
                    "created_at": treatment.created_at,
                    "last_used": treatment.last_used
                }
                for treatment_id, treatment in self.treatments.items()
            },
            "evolutions": {
                evolution_id: {
                    "type": evolution.type,
                    "description": evolution.description,
                    "properties": evolution.properties,
                    "conditions": evolution.conditions,
                    "effects": evolution.effects,
                    "created_at": evolution.created_at
                }
                for evolution_id, evolution in self.evolutions.items()
            },
            "facilities": {
                name: {
                    "name": facility.name,
                    "type": facility.type,
                    "capacity": facility.capacity,
                    "staff": list(facility.staff),
                    "patients": list(facility.patients),
                    "treatments": {
                        tname: {
                            "type": treatment.type,
                            "name": treatment.name,
                            "description": treatment.description,
                            "properties": treatment.properties,
                            "requirements": treatment.requirements,
                            "effects": treatment.effects
                        }
                        for tname, treatment in facility.treatments.items()
                    },
                    "resources": facility.resources,
                    "efficiency": facility.efficiency,
                    "created_at": facility.created_at
                }
                for name, facility in self.facilities.items()
            },
            "medical_knowledge": {
                dtype.value: level
                for dtype, level in self.medical_knowledge.items()
            }
        } 

@dataclass
class Health:
    """Represents the health state of an agent."""
    status: HealthStatus = HealthStatus.HEALTHY
    diseases: List[Disease] = field(default_factory=list)
    conditions: List[HealthCondition] = field(default_factory=list)
    treatments: List[Treatment] = field(default_factory=list)
    immunity: Dict[str, float] = field(default_factory=dict)  # disease: immunity_duration
    last_checkup: float = field(default_factory=time.time)
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
        
    def to_dict(self) -> Dict:
        """Convert health state to dictionary for serialization."""
        return {
            "status": self.status.value,
            "diseases": [disease.name for disease in self.diseases],
            "conditions": [condition.name for condition in self.conditions],
            "treatments": [treatment.name for treatment in self.treatments],
            "immunity": self.immunity,
            "last_checkup": self.last_checkup,
            "created_at": self.created_at,
            "last_update": self.last_update
        } 