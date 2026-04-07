"""Simple action-like structures for mission orchestration.

This module provides Python dataclasses that simulate ROS 2 action interfaces
without requiring interface generation. Useful for pure Python simulation
where the formal ROS 2 IDL infrastructure isn't necessary.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExcavateGoal:
    """Goal for excavation action."""
    dig_duration_sec: float


@dataclass  
class ExcavateResult:
    """Result from excavation action."""
    material_collected_kg: float
    success: bool


@dataclass
class ExcavateFeedback:
    """Feedback from excavation action during execution."""
    bucket_fill_percentage: float
    estimated_time_remaining: int


@dataclass
class DepositGoal:
    """Goal for deposit action."""
    material_to_deposit_kg: float


@dataclass
class DepositResult:
    """Result from deposit action."""
    material_deposited_kg: float
    success: bool


@dataclass
class DepositFeedback:
    """Feedback from deposit action during execution."""
    deposit_progress_percentage: float
    estimated_time_remaining: int
