"""Integration tests for StreetRace Manager modules."""

import sys
import os
import pytest

# Add the code directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

from modules.registration import Registration
from modules.crew import Crew
from modules.inventory import Inventory
from modules.race import Race
from modules.results import Results
from modules.mission import Mission
from modules.garage import Garage
from modules.leaderboard import Leaderboard

# helper functions

def make_all():
    """Helper function to create instances of all modules."""

    registration = Registration()
    crew = Crew(registration)
    inventory = Inventory()
    garage = Garage(inventory)
    race = Race(crew, inventory)
    results = Results(race, inventory)
    leaderboard = Leaderboard(results)
    mission = Mission(crew)

    m = {
        "registration": registration,
        "crew": crew,
        "inventory": inventory,
        "garage": garage,
        "race": race,
        "results": results,
        "leaderboard": leaderboard,
        "mission": mission
    }

    return m

# test 1

def test_register_then_assign_to_crew():
    """Test registering a driver and assigning them to the crew."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    
    reg.register("Alice", "driver")
    crew.assign_role("Alice", 8)
    assert crew.get_role("Alice") == "driver"

# test 2

def test_crew_assign_unregistered_raises():
    """Test that assigning an unregistered member to the crew raises an error."""

    m = make_all()
    crew = m["crew"]

    with pytest.raises(ValueError):
        crew.assign_role("Bob", 5)

# test 3

def test_re_registration_does_not_update_crew():
    """Test that re-registering a member updates their crew role as well."""
    
    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    
    reg.register("Charlie", "mechanic")
    crew.assign_role("Charlie", 7)
    assert crew.get_role("Charlie") == "mechanic"
    
    # re-register
    reg.register("Charlie", "driver")
    assert crew.get_role("Charlie") == "driver"

# test 4

def test_only_drivers_can_enter_race():
    """Test that only crew members with the driver role can enter a race."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    race = m["race"]
    inventory = m["inventory"]

    reg.register("Dave", "mechanic")
    crew.assign_role("Dave", 6)
    inventory.add_car("Car-A")
    race_id = race.create_race("City")

    with pytest.raises(ValueError):
        race.add_entry(race_id, "Dave", "Car-A")

# test 5

def test_car_damaged_by_driver_a_blocks_driver_b():
    """Test that if one driver damages a car, it becomes unavailable for another driver."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    race = m["race"]
    inventory = m["inventory"]
    result = m["results"]
    
    reg.register("Eve", "driver")
    reg.register("Frank", "driver")
    crew.assign_role("Eve", 9)
    crew.assign_role("Frank", 8)
    inventory.add_car("Car-B")
    inventory.add_cash(2000)
    race_id = race.create_race("Highway")
    
    # Eve enters and damages the car
    race.add_entry(race_id, "Eve", "Car-B")
    result.record_result(race_id, "Eve", 1, 1000, car_damaged=True)
    assert inventory.get_car("Car-B") == "damaged"
    
    # new race which Frank tries to enter
    race_id = race.create_race("City") 
    with pytest.raises(ValueError):
        race.add_entry(race_id, "Frank", "Car-B")

# test 6

def test_two_drivers_same_car_same_race():
    """Test that two drivers cannot enter the same car in the same race."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    race = m["race"]
    inventory = m["inventory"]
    
    reg.register("Alice", "driver")
    reg.register("Bob", "driver")
    crew.assign_role("Alice", 8)
    crew.assign_role("Bob", 7)
    inventory.add_car("Car-C")
    race_id = race.create_race("Downtown")

    race.add_entry(race_id, "Alice", "Car-C")
    with pytest.raises(ValueError):
        race.add_entry(race_id, "Bob", "Car-C")

# test 7

def test_full_race_lifecycle():
    """Test the full lifecycle of creating a race and registering drivers."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    inventory = m["inventory"]
    race = m["race"]
    results = m["results"]
    
    reg.register("Alice", "driver")
    reg.register("Bob", "driver")
    crew.assign_role("Alice", 8)
    crew.assign_role("Bob", 7)
    inventory.add_car("Car-D")
    inventory.add_car("Car-E")
    inventory.add_cash(2000)
    race_id = race.create_race("City")
    
    race.add_entry(race_id, "Alice", "Car-D")
    race.add_entry(race_id, "Bob", "Car-E")

    results.record_result(race_id, "Alice", 1, 1000)
    results.record_result(race_id, "Bob", 2, 800)

    assert inventory.cash == 200
    assert results.list_results() == [
        {"race_id": race_id, "driver": "Alice", "position": 1, 
         "prize": 1000, "car": "Car-D"}, 
        {"race_id": race_id, "driver": "Bob", "position": 2, 
         "prize": 800, "car": "Car-E"}
    ]

# test 8

def test_multiple_drivers_leaderboard_order_and_rank():
    """Test that the leaderboard correctly ranks multiple drivers based on points."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    inventory = m["inventory"]
    race = m["race"]
    results = m["results"]
    leaderboard = m["leaderboard"]

    reg.register("Alice", "driver")
    reg.register("Bob", "driver")
    crew.assign_role("Alice", 8)
    crew.assign_role("Bob", 7)
    inventory.add_car("Car-D")
    inventory.add_car("Car-E")
    inventory.add_cash(3000)

    race_id = race.create_race("City")
    race.add_entry(race_id, "Alice", "Car-D")
    race.add_entry(race_id, "Bob", "Car-E")
    results.record_result(race_id, "Alice", 1, 1000)
    results.record_result(race_id, "Bob", 2, 500)

    assert leaderboard.show_leaderboard() == [("Alice", 1000), ("Bob", 500)]
    assert leaderboard.get_rank("Alice") == 1
    assert leaderboard.get_rank("Bob") == 2

# test 9

def test_leaderboard_accumulates_across_races():
    """Test that the leaderboard accumulates prize totals across multiple races for one driver."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    inventory = m["inventory"]
    race = m["race"]
    results = m["results"]
    leaderboard = m["leaderboard"]

    reg.register("Alice", "driver")
    crew.assign_role("Alice", 8)
    inventory.add_car("Car-F")
    inventory.add_cash(3000)

    race_id1 = race.create_race("Race 1")
    race.add_entry(race_id1, "Alice", "Car-F")
    results.record_result(race_id1, "Alice", 1, 1000)

    race_id2 = race.create_race("Race 2")
    race.add_entry(race_id2, "Alice", "Car-F")
    results.record_result(race_id2, "Alice", 1, 800)

    assert leaderboard.show_leaderboard() == [("Alice", 1800)]

# test 10

def test_repair_consumes_parts_from_shared_inventory():
    """Test that repairing a car consumes the required parts from inventory."""

    m = make_all()
    inventory = m["inventory"]
    garage = m["garage"]

    inventory.add_car("Car-H")
    inventory.cars["Car-H"] = "damaged"
    inventory.add_parts("engine")
    inventory.add_parts("tire")

    garage.repair_car("Car-H", ["engine", "tire"])

    assert inventory.parts == []
    assert inventory.get_car("Car-H") == "ok"

# test 11

def test_mission_starts_after_crew_assigned():
    """Test that a mission starts successfully when the required role is in the crew."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    mission = m["mission"]

    reg.register("Alice", "driver")
    crew.assign_role("Alice", 8)

    mission_id = mission.create_mission("delivery", ["driver"])
    mission.start_mission(mission_id)

    assert mission.list_missions()[mission_id]["status"] == "active"

# test 12

def test_mission_fails_without_required_role():
    """Test that a mission cannot start if the required role is missing from the crew."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    mission = m["mission"]

    reg.register("Alice", "driver")
    crew.assign_role("Alice", 8)

    mission_id = mission.create_mission("rescue", ["mechanic"])

    with pytest.raises(ValueError):
        mission.start_mission(mission_id)

# test 13

def test_leaderboard_reflects_live_results():
    """Test that the leaderboard recomputes live as new results are recorded."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    inventory = m["inventory"]
    race = m["race"]
    results = m["results"]
    leaderboard = m["leaderboard"]

    reg.register("Alice", "driver")
    crew.assign_role("Alice", 8)
    inventory.add_car("Car-I")
    inventory.add_cash(2000)

    race_id1 = race.create_race("Race 1")
    race.add_entry(race_id1, "Alice", "Car-I")
    results.record_result(race_id1, "Alice", 1, 600)
    assert leaderboard.show_leaderboard() == [("Alice", 600)]

    race_id2 = race.create_race("Race 2")
    race.add_entry(race_id2, "Alice", "Car-I")
    results.record_result(race_id2, "Alice", 1, 400)
    assert leaderboard.show_leaderboard() == [("Alice", 1000)]

# test 14

def test_leaderboard_zero_prize_result():
    """Test that a driver with a zero prize result still appears on the leaderboard."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    inventory = m["inventory"]
    race = m["race"]
    results = m["results"]
    leaderboard = m["leaderboard"]

    reg.register("Alice", "driver")
    crew.assign_role("Alice", 8)
    inventory.add_car("Car-J")
    inventory.add_cash(500)

    race_id = race.create_race("City")
    race.add_entry(race_id, "Alice", "Car-J")
    results.record_result(race_id, "Alice", 1, 0)

    assert leaderboard.show_leaderboard() == [("Alice", 0)]

# test 15

def test_leaderboard_empty_before_any_results():
    """Test that the leaderboard returns an empty list when no results have been recorded."""

    m = make_all()
    leaderboard = m["leaderboard"]

    assert leaderboard.show_leaderboard() == []

# test 16

def test_garage_lists_car_as_damaged_after_result():
    """Test that garage.list_damaged reflects a car damaged during a race result."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    inventory = m["inventory"]
    garage = m["garage"]
    race = m["race"]
    results = m["results"]

    reg.register("Alice", "driver")
    crew.assign_role("Alice", 8)
    inventory.add_car("Car-K")
    inventory.add_cash(1000)

    race_id = race.create_race("City")
    race.add_entry(race_id, "Alice", "Car-K")
    results.record_result(race_id, "Alice", 1, 500, car_damaged=True)

    assert "Car-K" in garage.list_damaged()

# test 17

def test_insufficient_cash_blocks_result():
    """Test that recording a result raises when there is not enough cash, and cash is unchanged."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    inventory = m["inventory"]
    race = m["race"]
    results = m["results"]

    reg.register("Alice", "driver")
    crew.assign_role("Alice", 8)
    inventory.add_car("Car-L")
    inventory.add_cash(50)

    race_id = race.create_race("City")
    race.add_entry(race_id, "Alice", "Car-L")

    with pytest.raises(ValueError):
        results.record_result(race_id, "Alice", 1, 100)

    assert inventory.cash == 50

# test 18

def test_damage_repair_rerace_cycle():
    """Test the full damage → repair → re-race cycle across all modules."""

    m = make_all()
    reg = m["registration"]
    crew = m["crew"]
    inventory = m["inventory"]
    garage = m["garage"]
    race = m["race"]
    results = m["results"]
    leaderboard = m["leaderboard"]

    reg.register("Alice", "driver")
    crew.assign_role("Alice", 8)
    inventory.add_car("Car-O")
    inventory.add_cash(3000)
    inventory.add_parts("engine")

    # first race — car gets damaged
    race_id1 = race.create_race("Race 1")
    race.add_entry(race_id1, "Alice", "Car-O")
    results.record_result(race_id1, "Alice", 1, 1000, car_damaged=True)
    assert inventory.get_car("Car-O") == "damaged"

    # repair the car
    garage.repair_car("Car-O", ["engine"])
    assert inventory.get_car("Car-O") == "ok"

    # second race with same car
    race_id2 = race.create_race("Race 2")
    race.add_entry(race_id2, "Alice", "Car-O")
    results.record_result(race_id2, "Alice", 1, 800)

    assert leaderboard.show_leaderboard() == [("Alice", 1800)]