from dataclasses import dataclass, field
from typing import Dict, Tuple
import random
from datetime import datetime
from .utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class NaturalDisaster:
    id: str
    type: str
    location: Tuple[float, float]
    severity: float  # 0-1 scale
    duration: float  # seconds
    elapsed: float = 0.0
    start_time: float = field(default_factory=lambda: datetime.now().timestamp())
    active: bool = True

class NaturalDisasterSystem:
    """Manage natural disasters such as earthquakes or hurricanes."""
    def __init__(self, world):
        self.world = world
        self.disasters: Dict[str, NaturalDisaster] = {}
        self.counter = 0

    def initialize_system(self):
        logger.info("Initializing natural disaster system")

    def create_disaster(self, disaster_type: str, longitude: float, latitude: float,
                        severity: float = 0.5, duration: float = 3600) -> NaturalDisaster:
        disaster_id = f"disaster_{self.counter}"
        self.counter += 1
        disaster = NaturalDisaster(
            id=disaster_id,
            type=disaster_type,
            location=(longitude, latitude),
            severity=max(0.0, min(1.0, severity)),
            duration=max(1.0, duration)
        )
        self.disasters[disaster_id] = disaster
        logger.info(
            f"Created {disaster_type} {disaster_id} at ({longitude:.2f},{latitude:.2f})"
        )
        return disaster

    def generate_random_disaster(self):
        """Occasionally spawn a random disaster somewhere on Earth."""
        types = ["earthquake", "volcanic_eruption", "hurricane", "tornado", "flood", "wildfire"]
        disaster_type = random.choice(types)
        lon = random.uniform(self.world.min_longitude, self.world.max_longitude)
        lat = random.uniform(self.world.min_latitude, self.world.max_latitude)
        severity = random.random()
        duration = random.uniform(3600, 7200)
        self.create_disaster(disaster_type, lon, lat, severity, duration)

    def update(self, time_delta: float):
        # Small chance each tick to spawn a new disaster
        if random.random() < 0.0001 * time_delta:
            self.generate_random_disaster()

        ended = []
        for did, disaster in self.disasters.items():
            disaster.elapsed += time_delta
            if disaster.elapsed >= disaster.duration:
                disaster.active = False
                ended.append(did)
        for did in ended:
            logger.info(f"Disaster {did} ended")
            del self.disasters[did]

    def get_state(self) -> Dict:
        return {
            did: {
                "type": d.type,
                "location": d.location,
                "severity": d.severity,
                "duration": d.duration,
                "elapsed": d.elapsed,
                "active": d.active,
            }
            for did, d in self.disasters.items()
        }

