import threading
import time
import webbrowser

from simulation.world import World
from simulation.engine import SimulationEngine, engine as engine_global
from simulation.server import app, socketio
from simulation.utils.logging_config import get_logger, setup_logging


def run_server():
    socketio.run(app, host="0.0.0.0", port=5000)


def main():
    setup_logging()
    logger = get_logger(__name__)

    # Initialize the world and engine
    world = World(logger)
    world.spawn_initial_agents()

    engine_global = SimulationEngine(world, logger)

    # Expose engine to other modules
    import simulation.engine as engine_module
    engine_module.engine = engine_global

    engine_global.start()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Open dashboard view
    webbrowser.open("http://localhost:5000/godview")

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
