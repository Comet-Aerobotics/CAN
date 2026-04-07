#!/usr/bin/env python3
"""
Simple test of mission orchestration logic without ROS 2 action interfaces.
This demonstrates the mission flow for testing and debugging the state machine logic.

Run with:
    python3 simple_mission_test.py
"""

import time
from enum import Enum, auto
from dataclasses import dataclass, field


class MissionState(Enum):
    STARTUP = auto()
    NAV_TO_MINE = auto()
    EXCAVATE = auto()
    NAV_TO_DEPOSIT = auto()
    DEPOSIT = auto()
    NAV_HOME = auto()
    IDLE = auto()


@dataclass
class SimulatedLoader:
    """Simulates load sensor."""
    current_weight: float = 0.0
    capacity: float = 5.0
    dig_rate: float = 1.0  # kg/s
    
    def is_full(self) -> bool:
        return self.current_weight >= self.capacity * 0.95
    
    def excavate(self, duration_sec: float) -> float:
        """Simulate excavation."""
        weight_gained = min(self.capacity - self.current_weight, self.dig_rate * duration_sec)
        self.current_weight += weight_gained
        return weight_gained
    
    def deposit(self) -> float:
        """Empty bucket."""
        amount = self.current_weight
        self.current_weight = 0.0
        return amount
    
    def update(self, elapsed: float):
        """Simulate continuous collection during dig."""
        if elapsed < 5.0:  # simulate 5 second dig
            rate = self.dig_rate * (1.0 - (self.current_weight / self.capacity))
            self.current_weight = min(self.capacity, self.current_weight + rate * 0.1)


class SimpleMissionOrchestrator:
    """Simplified mission orchestrator for testing."""
    
    def __init__(self, target_material_kg: float = 10.0, dig_rate: float = 1.0):
        self.state = MissionState.STARTUP
        self.total_material = 0.0
        self.target_material = target_material_kg
        self.loader = SimulatedLoader(dig_rate=dig_rate)
        
        self.state_start_time = time.monotonic()
        self._log_once_messages = set()
    
    def log_once(self, msg: str):
        """Log message only once per unique message."""
        if msg not in self._log_once_messages:
            print(f"[{self.state.name}] {msg}")
            self._log_once_messages.add(msg)
    
    def log(self, msg: str):
        """Log message with current time."""
        print(f"[{self.state.name}] {msg}")
    
    def set_state(self, new_state: MissionState):
        """Transition to new state."""
        if self.state != new_state:
            elapsed = time.monotonic() - self.state_start_time
            self.log(f"Duration: {elapsed:.1f}s")
            self.log(f"Transition: {self.state.name} -> {new_state.name}")
            self.state = new_state
            self.state_start_time = time.monotonic()
            self._log_once_messages.clear()
    
    def update(self):
        """Update mission state machine."""
        elapsed = time.monotonic() - self.state_start_time
        
        if self.state == MissionState.STARTUP:
            self.log_once("Initializing mission...")
            self.set_state(MissionState.NAV_TO_MINE)
        
        elif self.state == MissionState.NAV_TO_MINE:
            self.log_once(f"Navigating to mine (simulated {elapsed:.1f}s)")
            if elapsed > 2.0:
                self.set_state(MissionState.EXCAVATE)
        
        elif self.state == MissionState.EXCAVATE:
            self.log_once(f"Excavating (bucket: {self.loader.current_weight:.1f}/{self.loader.capacity}kg)")
            
            # Simulate excavation
            self.loader.update(elapsed)
            
            if elapsed > 5.0 or self.loader.is_full():
                collected = self.loader.current_weight
                self.total_material += collected
                self.log(f"Excavation complete: {collected:.2f}kg collected (total: {self.total_material:.2f}kg)")
                self.set_state(MissionState.NAV_TO_DEPOSIT)
        
        elif self.state == MissionState.NAV_TO_DEPOSIT:
            self.log_once(f"Navigating to dump site (simulated {elapsed:.1f}s)")
            if elapsed > 2.0:
                self.set_state(MissionState.DEPOSIT)
        
        elif self.state == MissionState.DEPOSIT:
            self.log_once(f"Depositing (bucket will be empty in {max(0, 3.0 - elapsed):.1f}s)")
            if elapsed > 3.0:
                deposited = self.loader.deposit()
                self.log(f"Deposit complete: {deposited:.2f}kg deposited")
                
                # Check if mission complete
                if self.total_material >= self.target_material:
                    self.set_state(MissionState.NAV_HOME)
                else:
                    self.set_state(MissionState.NAV_TO_MINE)
        
        elif self.state == MissionState.NAV_HOME:
            self.log_once(f"Returning to base (simulated {elapsed:.1f}s)")
            if elapsed > 2.0:
                self.set_state(MissionState.IDLE)
        
        elif self.state == MissionState.IDLE:
            self.log_once(f"🎉 Mission complete! Collected {self.total_material:.2f}kg")
    
    def run(self, duration_sec: float = 60, update_rate_hz: float = 2):
        """Run the mission simulation for specified duration."""
        update_interval = 1.0 / update_rate_hz
        start_time = time.monotonic()
        
        print("\n" + "=" * 60)
        print("MISSION ORCHESTRATOR TEST")
        print(f"Target: {self.target_material}kg")
        print(f"Dig rate: {self.loader.dig_rate}kg/s")
        print("=" * 60 + "\n")
        
        while time.monotonic() - start_time < duration_sec and self.state != MissionState.IDLE:
            self.update()
            time.sleep(update_interval)
        
        final_elapsed = time.monotonic() - start_time
        print("\n" + "=" * 60)
        print(f"TEST COMPLETE ({final_elapsed:.1f}s)")
        print(f"Final state: {self.state.name}")
        print(f"Total material: {self.total_material:.2f}kg / {self.target_material}kg")
        print("=" * 60 + "\n")


def main():
    """Run mission orchestration test."""
    
    # Test with normal speed
    print("\n>>> NORMAL SPEED TEST (2 minute timeout)")
    print("    Expected: ~1 minute to collect 10kg\n")
    orchestrator = SimpleMissionOrchestrator(target_material_kg=10.0, dig_rate=1.0)
    orchestrator.run(duration_sec=120, update_rate_hz=2)
    
    # Test with fast speed
    print("\n>>> FAST SPEED TEST (30 second timeout)")
    print("    Expected: ~15 seconds to collect 2kg\n")
    orchestrator_fast = SimpleMissionOrchestrator(target_material_kg=2.0, dig_rate=10.0)
    orchestrator_fast.run(duration_sec=30, update_rate_hz=5)


if __name__ == '__main__':
    main()
