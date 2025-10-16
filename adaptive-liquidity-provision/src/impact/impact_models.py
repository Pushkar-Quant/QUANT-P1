"""
Market Impact Models

Implements various market impact models used in quantitative finance:
- Almgren-Chriss model (temporary + permanent impact)
- Square-root impact model
- Linear impact model

These models are essential for realistic market making simulation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class ImpactParameters:
    """Base parameters for impact models."""
    pass


@dataclass
class AlmgrenChrissParameters(ImpactParameters):
    """
    Parameters for Almgren-Chriss impact model.
    
    Attributes:
        gamma: Permanent impact coefficient (price drift per unit volume)
        eta: Temporary impact coefficient (execution cost per unit volume)
        epsilon: Fixed cost per trade
        sigma: Volatility of price process
    """
    gamma: float = 0.0001  # Permanent impact
    eta: float = 0.001     # Temporary impact
    epsilon: float = 0.0   # Fixed cost
    sigma: float = 0.02    # Volatility


@dataclass
class SquareRootParameters(ImpactParameters):
    """
    Parameters for square-root impact model.
    
    Attributes:
        beta: Impact coefficient
        daily_volume: Average daily trading volume
        sigma: Volatility
    """
    beta: float = 0.5
    daily_volume: float = 1000000.0
    sigma: float = 0.02


class ImpactModel(ABC):
    """Abstract base class for market impact models."""
    
    @abstractmethod
    def temporary_impact(self, volume: float, midprice: float, **kwargs) -> float:
        """
        Calculate temporary price impact (reverts after trade).
        
        Args:
            volume: Trade volume (signed: positive = buy, negative = sell)
            midprice: Current mid-price
            **kwargs: Additional parameters
        
        Returns:
            Price change due to temporary impact
        """
        pass
    
    @abstractmethod
    def permanent_impact(self, volume: float, midprice: float, **kwargs) -> float:
        """
        Calculate permanent price impact (persists after trade).
        
        Args:
            volume: Trade volume (signed: positive = buy, negative = sell)
            midprice: Current mid-price
            **kwargs: Additional parameters
        
        Returns:
            Price change due to permanent impact
        """
        pass
    
    def total_impact(self, volume: float, midprice: float, **kwargs) -> tuple[float, float]:
        """
        Calculate total impact (temporary + permanent).
        
        Returns:
            (temporary_impact, permanent_impact)
        """
        temp = self.temporary_impact(volume, midprice, **kwargs)
        perm = self.permanent_impact(volume, midprice, **kwargs)
        return temp, perm
    
    def execution_cost(self, volume: float, midprice: float, **kwargs) -> float:
        """
        Calculate total execution cost of a trade.
        
        Returns:
            Dollar cost of impact
        """
        temp, perm = self.total_impact(volume, midprice, **kwargs)
        # Cost is volume * (average of temporary and permanent impact)
        return abs(volume) * (temp + perm / 2)


class AlmgrenChrissImpact(ImpactModel):
    """
    Almgren-Chriss market impact model.
    
    Models both temporary and permanent price impact:
    - Permanent: ΔP_permanent = γ * volume * σ
    - Temporary: ΔP_temporary = η * (volume / √T) * σ + ε * sign(volume)
    
    Reference:
        Almgren, R., & Chriss, N. (2001). Optimal execution of portfolio transactions.
        Journal of Risk, 3, 5-40.
    """
    
    def __init__(self, params: Optional[AlmgrenChrissParameters] = None):
        self.params = params or AlmgrenChrissParameters()
    
    def temporary_impact(
        self, 
        volume: float, 
        midprice: float,
        execution_time: float = 1.0,
        **kwargs
    ) -> float:
        """
        Temporary impact: decays after trade completion.
        
        Formula: η * (|v| / √T) * σ + ε * sign(v)
        
        Args:
            volume: Trade volume (signed)
            midprice: Current mid-price
            execution_time: Time to execute the trade
        """
        if volume == 0:
            return 0.0
        
        # Volume-dependent component (scales with urgency)
        volume_component = (self.params.eta * abs(volume) * self.params.sigma 
                          / np.sqrt(execution_time))
        
        # Fixed component
        fixed_component = self.params.epsilon * np.sign(volume)
        
        return volume_component + fixed_component
    
    def permanent_impact(
        self, 
        volume: float, 
        midprice: float,
        **kwargs
    ) -> float:
        """
        Permanent impact: persists in the price process.
        
        Formula: γ * v * σ
        
        Args:
            volume: Trade volume (signed)
            midprice: Current mid-price
        """
        if volume == 0:
            return 0.0
        
        return self.params.gamma * volume * self.params.sigma
    
    def decay_temporary_impact(
        self, 
        impact: float, 
        time_elapsed: float,
        decay_rate: float = 0.5
    ) -> float:
        """
        Model decay of temporary impact over time.
        
        Args:
            impact: Initial temporary impact
            time_elapsed: Time since trade
            decay_rate: Exponential decay rate
        
        Returns:
            Remaining impact
        """
        return impact * np.exp(-decay_rate * time_elapsed)


class SquareRootImpact(ImpactModel):
    """
    Square-root market impact model.
    
    Popular in empirical studies, models impact as proportional to square root
    of trade size relative to daily volume.
    
    Formula: ΔP = β * σ * √(|v| / V_daily) * sign(v)
    
    Reference:
        Grinold, R. C., & Kahn, R. N. (1999). Active portfolio management.
    """
    
    def __init__(self, params: Optional[SquareRootParameters] = None):
        self.params = params or SquareRootParameters()
    
    def temporary_impact(
        self, 
        volume: float, 
        midprice: float,
        **kwargs
    ) -> float:
        """
        Square-root temporary impact.
        
        Args:
            volume: Trade volume (signed)
            midprice: Current mid-price
        """
        if volume == 0:
            return 0.0
        
        # Participation rate: fraction of daily volume
        participation = abs(volume) / self.params.daily_volume
        
        # Square-root law
        impact = (self.params.beta * self.params.sigma * 
                 np.sqrt(participation) * np.sign(volume))
        
        return impact
    
    def permanent_impact(
        self, 
        volume: float, 
        midprice: float,
        **kwargs
    ) -> float:
        """
        Permanent impact (typically smaller than temporary).
        
        Uses a fraction of temporary impact as permanent.
        """
        temp = self.temporary_impact(volume, midprice, **kwargs)
        # Assume 30% of temporary becomes permanent
        return 0.3 * temp


class LinearImpact(ImpactModel):
    """
    Simple linear impact model.
    
    Impact is directly proportional to trade size.
    Useful as a baseline or for testing.
    
    Formula: ΔP = α * v
    """
    
    def __init__(self, alpha: float = 0.0001, permanent_fraction: float = 0.5):
        """
        Args:
            alpha: Impact coefficient
            permanent_fraction: Fraction of impact that is permanent
        """
        self.alpha = alpha
        self.permanent_fraction = permanent_fraction
    
    def temporary_impact(
        self, 
        volume: float, 
        midprice: float,
        **kwargs
    ) -> float:
        """Linear temporary impact."""
        return self.alpha * volume * (1 - self.permanent_fraction)
    
    def permanent_impact(
        self, 
        volume: float, 
        midprice: float,
        **kwargs
    ) -> float:
        """Linear permanent impact."""
        return self.alpha * volume * self.permanent_fraction


class ImpactTracker:
    """
    Tracks and accumulates market impact over time.
    
    Maintains history of:
    - Trades and their impacts
    - Decay of temporary impacts
    - Net permanent impact
    """
    
    def __init__(self, impact_model: ImpactModel, decay_rate: float = 0.5):
        self.impact_model = impact_model
        self.decay_rate = decay_rate
        
        # History tracking
        self.trade_history = []  # (timestamp, volume, temp_impact, perm_impact)
        self.current_permanent_impact = 0.0
        self.current_temporary_impact = 0.0
        self.last_update_time = 0.0
    
    def add_trade(
        self, 
        timestamp: float, 
        volume: float, 
        midprice: float,
        **kwargs
    ) -> tuple[float, float]:
        """
        Record a trade and compute its impact.
        
        Returns:
            (temporary_impact, permanent_impact)
        """
        # Decay previous temporary impacts
        self._decay_temporary(timestamp)
        
        # Calculate new impact
        temp, perm = self.impact_model.total_impact(volume, midprice, **kwargs)
        
        # Update cumulative impacts
        self.current_temporary_impact += temp
        self.current_permanent_impact += perm
        
        # Record trade
        self.trade_history.append((timestamp, volume, temp, perm))
        self.last_update_time = timestamp
        
        return temp, perm
    
    def _decay_temporary(self, current_time: float):
        """Decay temporary impact based on time elapsed."""
        time_elapsed = current_time - self.last_update_time
        if time_elapsed > 0:
            decay_factor = np.exp(-self.decay_rate * time_elapsed)
            self.current_temporary_impact *= decay_factor
    
    def get_total_impact(self, current_time: float) -> float:
        """Get total current impact (temporary + permanent)."""
        self._decay_temporary(current_time)
        return self.current_temporary_impact + self.current_permanent_impact
    
    def get_permanent_impact(self) -> float:
        """Get cumulative permanent impact."""
        return self.current_permanent_impact
    
    def get_temporary_impact(self, current_time: float) -> float:
        """Get current temporary impact (decayed)."""
        self._decay_temporary(current_time)
        return self.current_temporary_impact
    
    def reset(self):
        """Reset the tracker."""
        self.trade_history = []
        self.current_permanent_impact = 0.0
        self.current_temporary_impact = 0.0
        self.last_update_time = 0.0
