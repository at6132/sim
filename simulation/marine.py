import logging
import traceback
from typing import Dict, List, Optional, Tuple
from simulation.utils.logging_config import get_logger

logger = get_logger(__name__)

class MarineSystem:
    def __init__(self, world):
        self.world = world
        self.logger = get_logger('MarineSystem')
        self.logger.info("Initializing MarineSystem...")
        
        # Initialize system components
        self.ocean_currents = {}
        self.marine_life = {}
        self.marine_resources = {}

    # Backwards compatibility for world code
    @property
    def creatures(self) -> Dict:
        return self.marine_life

    def initialize_marine_system(self):
        """Public entry point to initialize the system."""
        self.initialize()
        
    def initialize(self):
        """Initialize the marine system."""
        self.logger.info("Starting marine system initialization...")
        
        try:
            # Initialize ocean currents
            self.logger.info("Initializing ocean currents...")
            self._initialize_ocean_currents()
            
            # Initialize marine life
            self.logger.info("Initializing marine life...")
            self._initialize_marine_life()
            
            # Initialize marine resources
            self.logger.info("Initializing marine resources...")
            self._initialize_marine_resources()
            
            # Verify initialization
            if not self.verify_initialization():
                self.logger.error("Marine system initialization verification failed")
                raise RuntimeError("Marine system initialization verification failed")
            
            self.logger.info("Marine system initialization complete")
            
        except Exception as e:
            self.logger.error(f"Error during marine system initialization: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def verify_initialization(self):
        """Verify that the marine system is properly initialized."""
        self.logger.info("Verifying marine system initialization...")
        
        try:
            # Check ocean currents
            if not hasattr(self, 'ocean_currents') or not self.ocean_currents:
                self.logger.error("Ocean currents not properly initialized")
                return False
                
            # Check marine life
            if not hasattr(self, 'marine_life') or not self.marine_life:
                self.logger.error("Marine life not properly initialized")
                return False
                
            # Check marine resources
            if not hasattr(self, 'marine_resources') or not self.marine_resources:
                self.logger.error("Marine resources not properly initialized")
                return False
                
            self.logger.info("Marine system initialization verification successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during marine system verification: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
            
    def _initialize_ocean_currents(self):
        """Initialize ocean currents."""
        self.logger.info("Setting up ocean currents...")
        # Very simplified ocean current model
        self.ocean_currents = {
            "equatorial_current": {
                "direction": (1.0, 0.0),
                "speed": 1.0,
                "temperature": 25.0,
            },
            "gulf_stream": {
                "direction": (0.5, 0.5),
                "speed": 2.0,
                "temperature": 18.0,
            },
            "antarctic_circumpolar": {
                "direction": (1.0, 0.0),
                "speed": 1.5,
                "temperature": 2.0,
            },
        }
        
    def _initialize_marine_life(self):
        """Initialize marine life populations."""
        self.logger.info("Setting up marine life...")
        self.marine_life = {
            "fish": {"population": 1_000_000, "growth_rate": 0.01},
            "whale": {"population": 500, "growth_rate": 0.005},
            "shark": {"population": 5_000, "growth_rate": 0.002},
        }
        
    def _initialize_marine_resources(self):
        """Initialize marine resources."""
        self.logger.info("Setting up marine resources...")
        self.marine_resources = {
            "fish": 1_000_000,
            "seaweed": 500_000,
            "pearls": 1000,
        }
        
    def update(self, time_delta: float):
        """Update the marine system state."""
        self.logger.debug(
            f"Updating marine system with time delta: {time_delta}")

        # Simple population growth/decline model
        for info in self.marine_life.values():
            growth = info.get("growth_rate", 0.0)
            info["population"] = max(
                0,
                info["population"] + info["population"] * growth * (time_delta / 24.0),
            )

    def get_state(self) -> Dict:
        """Return current state of the marine system."""
        return {
            "ocean_currents": self.ocean_currents,
            "marine_life": self.marine_life,
            "marine_resources": self.marine_resources,
        }
