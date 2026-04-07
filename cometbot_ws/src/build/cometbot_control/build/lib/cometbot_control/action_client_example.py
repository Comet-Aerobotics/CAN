#!/usr/bin/env python3
"""
Example showing how to use the action types and orchestration logic.

This demonstrates:
1. How to create action goals using dataclasses
2. How the mission state machine works
3. How to manually test the logic

For full testing with ROS 2 nodes, use:
  python3 simple_mission_test.py (in parent directory)
"""

from cometbot_control.action_types import (
    ExcavateGoal, ExcavateResult, ExcavateFeedback,
    DepositGoal, DepositResult, DepositFeedback
)


def example_action_creation():
    """Show how to create action goals and results."""
    print("\n=== Action Types Example ===\n")
    
    # Create an excavate goal
    dig_goal = ExcavateGoal(dig_duration_sec=30.0)
    print(f"Excavate Goal: {dig_goal}")
    
    # Create feedback
    dig_feedback = ExcavateFeedback(
        bucket_fill_percentage=75.5,
        estimated_time_remaining=15
    )
    print(f"Excavate Feedback: {dig_feedback}")
    
    # Create result
    dig_result = ExcavateResult(
        material_collected_kg=5.0,
        success=True
    )
    print(f"Excavate Result: {dig_result}")
    
    print()
    
    # Create a deposit goal
    deposit_goal = DepositGoal(material_to_deposit_kg=5.0)
    print(f"Deposit Goal: {deposit_goal}")
    
    # Create feedback
    deposit_feedback = DepositFeedback(
        deposit_progress_percentage=50.0,
        estimated_time_remaining=3
    )
    print(f"Deposit Feedback: {deposit_feedback}")
    
    # Create result
    deposit_result = DepositResult(
        material_deposited_kg=5.0,
        success=True
    )
    print(f"Deposit Result: {deposit_result}")


def example_mission_flow():
    """Show the expected mission flow with these action types."""
    print("\n=== Expected Mission Flow ===\n")
    
    flow = [
        ("1. FSM creates excavate goal", ExcavateGoal(dig_duration_sec=30)),
        ("2. Excavator receives goal", "→ starts digging"),
        ("3. Excavator publishes feedback", ExcavateFeedback(75.0, 5)),
        ("4. FSM receives feedback", "→ updates bucket fill display"),
        ("5. Excavation completes", ExcavateResult(5.0, True)),
        ("6. FSM receives result", "→ updates total material"),
        ("7. FSM creates deposit goal", DepositGoal(5.0)),
        ("8. Depositor receives goal", "→ starts dumping"),
        ("9. Depositor publishes feedback", DepositFeedback(50.0, 3)),
        ("10. Deposition completes", DepositResult(5.0, True)),
        ("11. FSM checks mission complete", "→ repeat or finish"),
    ]
    
    for step, data in flow:
        print(f"{step}")
        if hasattr(data, '__dataclass_fields__'):
            print(f"     {data}")
        else:
            print(f"     {data}")
        print()


if __name__ == '__main__':
    print("=" * 70)
    print("ACTION ORCHESTRATION EXAMPLE")
    print("=" * 70)
    
    example_action_creation()
    example_mission_flow()
    
    print("\n" + "=" * 70)
    print("\nFor full mission orchestration test, run: python3 simple_mission_test.py")
    print("=" * 70 + "\n")
