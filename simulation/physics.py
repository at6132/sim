from dataclasses import dataclass
from typing import Dict, Tuple
from .utils.logging_config import get_logger

logger = get_logger(__name__)

GRAVITY = 9.80665  # m/s^2

@dataclass
class Body:
    id: str
    position: Tuple[float, float]
    velocity: Tuple[float, float] = (0.0, 0.0)
    mass: float = 70.0

class PhysicsSystem:
    """Simple 2D physics system for agents and objects."""
    def __init__(self, world):
        self.world = world
        self.bodies: Dict[str, Body] = {}
        logger.info("Physics system initialized")

    def register_agent(self, agent):
        """Register an agent as a physics body."""
        if not agent:
            return
        self.bodies[agent.id] = Body(
            id=agent.id,
            position=agent.position,
            velocity=getattr(agent, "velocity", (0.0, 0.0)),
            mass=getattr(agent, "mass", 70.0),
        )
        logger.info(f"Registered body for agent {agent.id}")

    def update(self, time_delta: float):
        """Update all physics bodies."""
        dt = time_delta
        for body in self.bodies.values():
            vx, vy = body.velocity
            lon, lat = body.position
            slope = self.world.terrain.get_slope_at(lon, lat)
            friction = 0.1 + (slope / 90.0)
            vx *= max(0.0, 1 - friction * dt)
            vy *= max(0.0, 1 - friction * dt)

            new_lon = body.position[0] + vx * dt
            new_lat = body.position[1] + vy * dt
            if self.world.is_valid_position(new_lon, new_lat):
                body.position = (new_lon, new_lat)
                agent = self.world.agents.get_agent(body.id)
                if agent:
                    agent.position = body.position
                    agent.velocity = (vx, vy)
            body.velocity = (vx, vy)

