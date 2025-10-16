"""
Unit tests for market impact models.
"""

import pytest
import numpy as np
from src.impact.impact_models import (
    AlmgrenChrissImpact,
    SquareRootImpact,
    LinearImpact,
    AlmgrenChrissParameters,
    SquareRootParameters,
    ImpactTracker
)


class TestAlmgrenChrissImpact:
    """Test Almgren-Chriss impact model."""
    
    @pytest.fixture
    def model(self):
        params = AlmgrenChrissParameters(
            gamma=0.0001,
            eta=0.001,
            epsilon=0.0,
            sigma=0.02
        )
        return AlmgrenChrissImpact(params)
    
    def test_temporary_impact_positive_volume(self, model):
        """Test temporary impact for buy order."""
        impact = model.temporary_impact(volume=100, midprice=100.0, execution_time=1.0)
        assert impact > 0  # Buy order increases price
    
    def test_temporary_impact_negative_volume(self, model):
        """Test temporary impact for sell order."""
        impact = model.temporary_impact(volume=-100, midprice=100.0, execution_time=1.0)
        assert impact < 0  # Sell order decreases price
    
    def test_temporary_impact_urgency(self, model):
        """Test that faster execution has higher temporary impact."""
        impact_fast = model.temporary_impact(volume=100, midprice=100.0, execution_time=0.1)
        impact_slow = model.temporary_impact(volume=100, midprice=100.0, execution_time=10.0)
        assert impact_fast > impact_slow
    
    def test_permanent_impact(self, model):
        """Test permanent impact calculation."""
        impact = model.permanent_impact(volume=100, midprice=100.0)
        assert impact > 0
        
        # Should be linear in volume
        impact_2x = model.permanent_impact(volume=200, midprice=100.0)
        assert np.isclose(impact_2x, 2 * impact)
    
    def test_zero_volume(self, model):
        """Test that zero volume produces zero impact."""
        temp = model.temporary_impact(volume=0, midprice=100.0)
        perm = model.permanent_impact(volume=0, midprice=100.0)
        assert temp == 0
        assert perm == 0
    
    def test_total_impact(self, model):
        """Test total impact calculation."""
        temp, perm = model.total_impact(volume=100, midprice=100.0)
        assert temp > 0
        assert perm > 0
    
    def test_decay_temporary_impact(self, model):
        """Test temporary impact decay."""
        initial_impact = 0.1
        decayed = model.decay_temporary_impact(initial_impact, time_elapsed=1.0, decay_rate=0.5)
        assert 0 < decayed < initial_impact


class TestSquareRootImpact:
    """Test square-root impact model."""
    
    @pytest.fixture
    def model(self):
        params = SquareRootParameters(
            beta=0.5,
            daily_volume=1000000.0,
            sigma=0.02
        )
        return SquareRootImpact(params)
    
    def test_temporary_impact_scales_with_sqrt(self, model):
        """Test that impact scales with square root of volume."""
        impact_1 = model.temporary_impact(volume=100, midprice=100.0)
        impact_4 = model.temporary_impact(volume=400, midprice=100.0)
        
        # Should be approximately 2x (sqrt(4) = 2)
        ratio = impact_4 / impact_1
        assert 1.9 < ratio < 2.1
    
    def test_permanent_impact_fraction(self, model):
        """Test permanent impact is fraction of temporary."""
        temp = model.temporary_impact(volume=100, midprice=100.0)
        perm = model.permanent_impact(volume=100, midprice=100.0)
        
        assert perm < temp
        assert np.isclose(perm, 0.3 * temp, rtol=0.01)


class TestLinearImpact:
    """Test linear impact model."""
    
    @pytest.fixture
    def model(self):
        return LinearImpact(alpha=0.0001, permanent_fraction=0.5)
    
    def test_linear_scaling(self, model):
        """Test impact scales linearly with volume."""
        impact_1 = model.temporary_impact(volume=100, midprice=100.0)
        impact_2 = model.temporary_impact(volume=200, midprice=100.0)
        
        assert np.isclose(impact_2, 2 * impact_1)
    
    def test_permanent_fraction(self, model):
        """Test permanent fraction is correct."""
        temp = model.temporary_impact(volume=100, midprice=100.0)
        perm = model.permanent_impact(volume=100, midprice=100.0)
        
        assert np.isclose(perm, temp)  # With 50% fraction


class TestImpactTracker:
    """Test impact tracking over time."""
    
    @pytest.fixture
    def tracker(self):
        model = LinearImpact(alpha=0.0001, permanent_fraction=0.5)
        return ImpactTracker(model, decay_rate=0.5)
    
    def test_add_trade(self, tracker):
        """Test adding a trade."""
        temp, perm = tracker.add_trade(
            timestamp=1.0,
            volume=100,
            midprice=100.0
        )
        
        assert temp > 0
        assert perm > 0
        assert len(tracker.trade_history) == 1
    
    def test_cumulative_impact(self, tracker):
        """Test cumulative impact accumulation."""
        tracker.add_trade(1.0, 100, 100.0)
        tracker.add_trade(2.0, 100, 100.0)
        
        total_impact = tracker.get_total_impact(2.0)
        assert total_impact > 0
    
    def test_temporary_impact_decay(self, tracker):
        """Test temporary impact decays over time."""
        tracker.add_trade(1.0, 100, 100.0)
        
        temp_immediate = tracker.get_temporary_impact(1.0)
        temp_later = tracker.get_temporary_impact(3.0)
        
        assert temp_later < temp_immediate
    
    def test_permanent_impact_persists(self, tracker):
        """Test permanent impact doesn't decay."""
        tracker.add_trade(1.0, 100, 100.0)
        
        perm_immediate = tracker.get_permanent_impact()
        tracker.get_total_impact(10.0)  # Let time pass
        perm_later = tracker.get_permanent_impact()
        
        assert perm_immediate == perm_later
    
    def test_reset(self, tracker):
        """Test tracker reset."""
        tracker.add_trade(1.0, 100, 100.0)
        tracker.reset()
        
        assert len(tracker.trade_history) == 0
        assert tracker.current_permanent_impact == 0
        assert tracker.current_temporary_impact == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
