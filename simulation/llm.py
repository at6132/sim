import os
import openai
from typing import Dict, List, Optional
import json
import logging
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

# Load environment variables from .env file in root directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class AgentCognition:
    def __init__(self, agent_id: str):
        """Initialize the cognition system for an agent."""
        self.agent_id = agent_id
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("No OpenAI API key found in .env file. Cognition system will operate in limited mode.")
            self.openai_available = False
        else:
            openai.api_key = api_key
            self.openai_available = True
            logger.info(f"OpenAI API key loaded successfully for agent {agent_id}")
        self.memories: List[Dict] = []
        self.knowledge: Dict[str, float] = {}
        self.goals: List[str] = []
        self.current_thoughts: str = ""
        self.last_action: Optional[Dict] = None
        
    def get_state(self) -> Dict:
        """Get the current state of the cognition system."""
        return {
            "memories": self.memories,
            "knowledge": self.knowledge,
            "goals": self.goals,
            "current_thoughts": self.current_thoughts,
            "last_action": self.last_action
        }
        
    def think(self, agent_state: Dict) -> Dict:
        """Process the agent's current state and determine next action."""
        try:
            # Prepare the prompt with agent's current state
            prompt = self._create_thought_prompt(agent_state)
            
            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI simulating an agent's thoughts and decision-making process."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response
            thoughts = response.choices[0].message.content
            
            # Update cognition state
            self.current_thoughts = thoughts
            self._update_memories(agent_state, thoughts)
            
            # Determine next action based on thoughts
            action = self._determine_action(thoughts, agent_state)
            self.last_action = action
            
            return {
                "thoughts": thoughts,
                "action": action,
                "learning": self._extract_learning(thoughts)
            }
            
        except Exception as e:
            logger.error(f"Error in agent {self.agent_id} cognition: {str(e)}")
            return {
                "thoughts": "Error in cognition system",
                "action": {"type": "wait"},
                "learning": {"concepts": []}
            }
            
    def _create_thought_prompt(self, agent_state: Dict) -> str:
        """Create a prompt for the agent's thoughts."""
        return f"""
        Agent State:
        {json.dumps(agent_state, indent=2)}
        
        Previous Thoughts:
        {self.current_thoughts}
        
        Previous Action:
        {json.dumps(self.last_action) if self.last_action else "None"}
        
        Based on this information, what are your thoughts and what should you do next?
        Consider your needs, environment, and goals.
        """
        
    def _update_memories(self, agent_state: Dict, thoughts: str):
        """Update the agent's memories with new information."""
        memory = {
            "state": agent_state,
            "thoughts": thoughts,
            "timestamp": agent_state.get("time", 0)
        }
        self.memories.append(memory)
        # Keep only last 10 memories
        if len(self.memories) > 10:
            self.memories = self.memories[-10:]
            
    def _determine_action(self, thoughts: str, agent_state: Dict) -> Dict:
        """Determine the next action based on thoughts and state."""
        # Basic action determination logic
        needs = agent_state.get("needs", {})
        
        # Check most urgent needs
        if needs.get("hunger", 0) > 0.7:
            return {"type": "gather", "resource": "food"}
        elif needs.get("thirst", 0) > 0.7:
            return {"type": "gather", "resource": "water"}
        elif needs.get("rest", 0) > 0.7:
            return {"type": "rest"}
            
        # Default to exploring
        return {"type": "move"}
        
    def _extract_learning(self, thoughts: str) -> Dict:
        """Extract learning concepts from thoughts."""
        return {
            "concepts": []  # To be implemented with more sophisticated learning extraction
        } 