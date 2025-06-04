from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
import random
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    FOOD = "food"
    WATER = "water"
    WOOD = "wood"
    STONE = "stone"
    METAL = "metal"
    CLOTH = "cloth"
    TOOLS = "tools"
    WEAPONS = "weapons"
    SHELTER = "shelter"
    MEDICINE = "medicine"
    KNOWLEDGE = "knowledge"
    SERVICE = "service"
    CURRENCY = "currency"

class TradeType(Enum):
    BARTER = "barter"
    CURRENCY = "currency"
    GIFT = "gift"
    TRIBUTE = "tribute"

class MarketType(Enum):
    EXCHANGE = "exchange"  # General trading platform
    FUTURES = "futures"    # Future contracts
    DERIVATIVES = "derivatives"  # Complex financial instruments
    COMMODITY = "commodity"  # Raw materials trading
    LABOR = "labor"       # Labor market
    REAL_ESTATE = "real_estate"  # Property market
    INNOVATION = "innovation"  # Technology and ideas market

class FinancialInstrument(Enum):
    SHARE = "share"           # Ownership stake
    BOND = "bond"            # Debt instrument
    FUTURE = "future"        # Future contract
    OPTION = "option"        # Option contract
    SWAP = "swap"           # Swap contract
    FORWARD = "forward"      # Forward contract
    WARRANT = "warrant"      # Warrant
    CERTIFICATE = "certificate"  # Certificate

@dataclass
class Resource:
    type: ResourceType
    amount: float
    quality: float  # 0.0 to 1.0
    source: str
    production_time: float  # in hours
    value: float  # base value
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent resource types

@dataclass
class Exchange:
    name: str
    description: str
    type: str  # Emergent exchange type
    rules: Dict[str, Any] = field(default_factory=dict)  # Custom rules for this exchange
    participants: Set[str] = field(default_factory=set)
    volume: float = 0.0
    efficiency: float = 1.0
    created_at: float = field(default_factory=time.time)
    last_trade_time: Optional[float] = None
    history: List[Dict[str, Any]] = field(default_factory=list)  # Custom history format

@dataclass
class Trade:
    exchange: str
    goods_given: Dict[str, float]  # Can be any resource or service
    goods_received: Dict[str, float]
    participants: List[str]
    timestamp: float
    success: bool
    value_ratio: float
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent trade types

@dataclass
class Market:
    name: str
    type: MarketType
    description: str
    instruments: Dict[str, FinancialInstrument] = field(default_factory=dict)
    participants: Set[str] = field(default_factory=set)
    volume: float = 0.0
    liquidity: float = 1.0
    volatility: float = 0.1
    created_at: float = field(default_factory=time.time)
    last_trade_time: Optional[float] = None
    price_history: List[Tuple[float, float]] = field(default_factory=list)  # (timestamp, price)

@dataclass
class FinancialInstrument:
    name: str
    type: FinancialInstrument
    issuer: str
    value: float
    risk: float
    maturity: Optional[float] = None
    dividend: float = 0.0
    volume: float = 0.0
    last_price: float = 0.0
    price_history: List[Tuple[float, float]] = field(default_factory=list)

@dataclass
class Portfolio:
    owner: str
    resources: Dict[str, float] = field(default_factory=dict)  # Can hold any resource type
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    properties: Dict[str, Any] = field(default_factory=dict)  # Custom properties for emergent portfolio types

class EconomicSystem:
    def __init__(self, world):
        """Initialize the economic system."""
        self.world = world
        self.resources: Dict[str, Resource] = {}
        self.exchanges: Dict[str, Exchange] = {}
        self.trade_history: List[Trade] = []
        self.portfolios: Dict[str, Portfolio] = {}
        self.initialize_system()
        
    def initialize_system(self):
        """Initialize the economic system with minimal structure."""
        logger.info("Initializing economic system...")
        
        # Create a basic exchange - but don't prescribe its type or rules
        self.exchanges["main_exchange"] = Exchange(
            name="Main Exchange",
            description="Primary trading platform",
            type="emergent"  # Let the simulation determine the type
        )
        
        logger.info("Economic system initialization complete")
        
    def create_exchange(self, name: str, description: str, type: str, rules: Dict[str, Any] = None) -> Exchange:
        """Create a new exchange with custom type and rules."""
        if name in self.exchanges:
            logger.warning(f"Exchange {name} already exists")
            return self.exchanges[name]
            
        exchange = Exchange(
            name=name,
            description=description,
            type=type,
            rules=rules or {}
        )
        
        self.exchanges[name] = exchange
        logger.info(f"Created new exchange: {name} of type {type}")
        return exchange
        
    def create_resource(self, type: ResourceType, amount: float, quality: float,
                       source: str, production_time: float, value: float,
                       properties: Dict[str, Any] = None) -> Resource:
        """Create a new resource with custom properties."""
        resource = Resource(
            type=type,
            amount=amount,
            quality=quality,
            source=source,
            production_time=production_time,
            value=value,
            properties=properties or {}
        )
        
        self.resources[source] = resource
        logger.info(f"Created new resource: {source}")
        return resource
        
    def create_portfolio(self, owner: str, properties: Dict[str, Any] = None) -> Portfolio:
        """Create a new portfolio with custom properties."""
        if owner in self.portfolios:
            logger.warning(f"Portfolio for {owner} already exists")
            return self.portfolios[owner]
            
        portfolio = Portfolio(
            owner=owner,
            properties=properties or {}
        )
        
        self.portfolios[owner] = portfolio
        logger.info(f"Created new portfolio for {owner}")
        return portfolio
        
    def execute_trade(self, exchange: str, goods_given: Dict[str, float],
                     goods_received: Dict[str, float], participants: List[str]) -> bool:
        """Execute a trade with custom goods and participants."""
        if exchange not in self.exchanges:
            logger.error(f"Exchange {exchange} does not exist")
            return False
            
        # Check if participants have the goods
        for participant, goods in zip(participants[:len(goods_given)], goods_given.items()):
            if participant not in self.portfolios:
                logger.error(f"Participant {participant} does not have a portfolio")
                return False
                
            if goods[0] not in self.portfolios[participant].resources or \
               self.portfolios[participant].resources[goods[0]] < goods[1]:
                logger.error(f"Participant {participant} does not have enough {goods[0]}")
                return False
                
        # Execute the trade
        for participant, goods in zip(participants[:len(goods_given)], goods_given.items()):
            self.portfolios[participant].resources[goods[0]] -= goods[1]
            
        for participant, goods in zip(participants[len(goods_given):], goods_received.items()):
            if participant not in self.portfolios:
                self.create_portfolio(participant)
            self.portfolios[participant].resources[goods[0]] = \
                self.portfolios[participant].resources.get(goods[0], 0) + goods[1]
                
        # Record the trade
        trade = Trade(
            exchange=exchange,
            goods_given=goods_given,
            goods_received=goods_received,
            participants=participants,
            timestamp=time.time(),
            success=True,
            value_ratio=sum(goods_received.values()) / sum(goods_given.values())
        )
        
        self.trade_history.append(trade)
        self.exchanges[exchange].history.append({
            "timestamp": trade.timestamp,
            "goods_given": goods_given,
            "goods_received": goods_received,
            "participants": participants
        })
        
        logger.info(f"Executed trade in {exchange}")
        return True
        
    def update(self, time_delta: float):
        """Update economic system state."""
        # Let the simulation determine how exchanges evolve
        self._update_exchanges(time_delta)
        
        # Update portfolios based on emergent rules
        self._update_portfolios(time_delta)
        
        # Check for emergent economic events
        self._check_economic_events(time_delta)
        
    def _update_exchanges(self, time_delta: float):
        """Update exchange states based on emergent rules."""
        for exchange in self.exchanges.values():
            # Let the simulation determine exchange evolution
            pass
            
    def _update_portfolios(self, time_delta: float):
        """Update portfolio states based on emergent rules."""
        for portfolio in self.portfolios.values():
            # Let the simulation determine portfolio evolution
            pass
            
    def _check_economic_events(self, time_delta: float):
        """Check for emergent economic events."""
        # Let the simulation determine what events occur
        pass
        
    def to_dict(self) -> Dict:
        """Convert economic system state to dictionary for serialization."""
        return {
            "resources": {
                source: {
                    "type": resource.type.value,
                    "amount": resource.amount,
                    "quality": resource.quality,
                    "source": resource.source,
                    "production_time": resource.production_time,
                    "value": resource.value,
                    "properties": resource.properties
                }
                for source, resource in self.resources.items()
            },
            "exchanges": {
                name: {
                    "name": exchange.name,
                    "description": exchange.description,
                    "type": exchange.type,
                    "rules": exchange.rules,
                    "participants": list(exchange.participants),
                    "volume": exchange.volume,
                    "efficiency": exchange.efficiency,
                    "created_at": exchange.created_at,
                    "last_trade_time": exchange.last_trade_time,
                    "history": exchange.history
                }
                for name, exchange in self.exchanges.items()
            },
            "trade_history": [
                {
                    "exchange": trade.exchange,
                    "goods_given": trade.goods_given,
                    "goods_received": trade.goods_received,
                    "participants": trade.participants,
                    "timestamp": trade.timestamp,
                    "success": trade.success,
                    "value_ratio": trade.value_ratio,
                    "properties": trade.properties
                }
                for trade in self.trade_history
            ],
            "portfolios": {
                owner: {
                    "owner": portfolio.owner,
                    "resources": portfolio.resources,
                    "created_at": portfolio.created_at,
                    "last_updated": portfolio.last_updated,
                    "properties": portfolio.properties
                }
                for owner, portfolio in self.portfolios.items()
            }
        } 