"""CLI entry point for the StreetRace Manager application."""

from modules.registration import Registration
from modules.crew import Crew
from modules.inventory import Inventory
from modules.race import Race
from modules.results import Results
from modules.mission import Mission
from modules.garage import Garage
from modules.leaderboard import Leaderboard


def get_str(prompt):
    """Prompt for a non-empty string or raise ValueError."""
    value = input(prompt).strip()
    if not value:
        raise ValueError(f"{prompt.strip()} cannot be empty")
    return value


def get_int(prompt):
    """Prompt for an integer or raise ValueError."""
    raw = input(prompt).strip()
    if not raw:
        raise ValueError(f"{prompt.strip()} cannot be empty")
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{prompt.strip()} must be a number") from exc


def handle_register(registration):
    """Register a new member with a role."""
    name = get_str("Name: ")
    role = get_str("Role (driver / mechanic / owner): ")
    registration.register(name, role)
    print(f"Registered {name} as {role}.")


def handle_list_members(registration):
    """List all registered members."""
    members = registration.list_members()
    if not members:
        print("No members registered.")
    else:
        for name, role in members.items():
            print(f"  {name}: {role}")


def handle_add_to_crew(crew):
    """Add a registered member to the crew with a skill level."""
    name = get_str("Name: ")
    skill_level = get_int("Skill level (0-10): ")
    if not 0 <= skill_level <= 10:
        raise ValueError("Skill level must be between 0 and 10")
    crew.assign_role(name, skill_level)
    print(f"Assigned {name} to crew (skill {skill_level}).")


def handle_list_crew(crew):
    """List all crew members and their roles."""
    crew_data = crew.list_crew()
    if not crew_data:
        print("No crew assigned.")
    else:
        for name, info in crew_data.items():
            print(f"  {name}: {info['role']} (skill {info['skill_level']})")


def handle_add_car(inventory):
    """Add a car to inventory."""
    car = get_str("Car name: ")
    inventory.add_car(car)
    print(f"Added car '{car}'.")


def handle_add_parts(inventory):
    """Add a part to inventory."""
    part = get_str("Part name: ")
    inventory.add_parts(part)
    print(f"Added part '{part}'.")


def handle_add_tools(inventory):
    """Add a tool to inventory."""
    tool = get_str("Tool name: ")
    inventory.add_tools(tool)
    print(f"Added tool '{tool}'.")


def handle_add_money(inventory):
    """Add cash to inventory."""
    amount = get_int("Amount to add: $")
    if amount <= 0:
        raise ValueError("Amount must be greater than 0")
    inventory.add_cash(amount)
    print(f"Added ${amount}. Balance: ${inventory.cash}")


def handle_view_inventory(inventory):
    """Display current inventory."""
    inv = inventory.list_inventory()
    print(f"  Cars:  {inv['cars']}")
    print(f"  Parts: {inv['parts']}")
    print(f"  Tools: {inv['tools']}")
    print(f"  Cash:  ${inv['cash']}")


def handle_create_race(race):
    """Create a new race event."""
    name = get_str("Race name: ")
    race_id = race.create_race(name)
    print(f"Created race '{name}' with ID {race_id}.")


def handle_add_race_entry(race):
    """Add a driver and car to an existing race."""
    race_id = get_int("Race ID: ")
    driver = get_str("Driver name: ")
    car = get_str("Car name: ")
    race.add_entry(race_id, driver, car)
    print(f"Added {driver} / {car} to race {race_id}.")


def handle_view_race_entries(race):
    """Display all entries for a given race."""
    race_id = get_int("Race ID: ")
    races = race.list_races()
    if race_id not in races:
        raise ValueError(f"Race {race_id} does not exist")
    entries = races[race_id]["entries"]
    if not entries:
        print("No entries yet.")
    else:
        for entry in entries:
            print(f"  {entry['driver']} — {entry['car']}")


def handle_record_result(results):
    """Record a race result for a driver."""
    race_id = get_int("Race ID: ")
    driver = get_str("Driver name: ")
    position = get_int("Position: ")
    prize = get_int("Prize amount: ")
    damaged = input("Car damaged? (y/n): ").strip().lower() == "y"
    results.record_result(race_id, driver, position, prize, car_damaged=damaged)
    print("Result recorded.")



def handle_create_mission(mission):
    """Create a new mission with required crew roles."""
    mission_type = get_str("Mission type (delivery / rescue): ")
    roles_input = get_str("Required roles (driver / mechanic / owner, comma-separated): ")
    required_roles = [r.strip() for r in roles_input.split(",")]
    mission_id = mission.create_mission(mission_type, required_roles)
    print(f"Created mission '{mission_type}' with ID {mission_id}.")


def handle_start_mission(mission):
    """Start an existing mission."""
    mission_id = get_int("Mission ID: ")
    mission.start_mission(mission_id)
    print(f"Mission {mission_id} started.")


def handle_list_missions(mission):
    """List all missions."""
    missions = mission.list_missions()
    if not missions:
        print("No missions.")
    else:
        for mid, info in missions.items():
            print(
                f"  [{mid}] {info['type']} | "
                f"roles: {info['required_roles']} | {info['status']}"
            )


def handle_repair_car(garage):
    """Repair a damaged car using parts from inventory."""
    car = get_str("Car name: ")
    parts_input = get_str("Required parts (comma-separated): ")
    required_parts = [p.strip() for p in parts_input.split(",")]
    garage.repair_car(car, required_parts)
    print(f"Car '{car}' repaired.")


def handle_view_leaderboard(leaderboard):
    """Display the race leaderboard."""
    board = leaderboard.show_leaderboard()
    if not board:
        print("No results yet.")
    else:
        for i, (driver, total) in enumerate(board, 1):
            print(f"  {i}. {driver}: ${total}")


MENU = """
 1. Register member
 2. List members
 3. Add to crew
 4. List crew
 5. Add car
 6. Add parts
 7. Add tools
 8. Add money
 9. View inventory
10. Create race
11. Add race entry
12. View race entries
13. Record race result
14. Create mission
15. Start mission
16. List missions
17. Repair car
18. View leaderboard
19. Quit
"""


def main():
    """Run the StreetRace Manager CLI."""
    registration = Registration()
    crew = Crew(registration)
    inventory = Inventory()
    race = Race(crew, inventory)
    results = Results(race, inventory)
    mission = Mission(crew)
    garage = Garage(inventory)
    leaderboard = Leaderboard(results)

    handlers = {
        "1":  lambda: handle_register(registration),
        "2":  lambda: handle_list_members(registration),
        "3":  lambda: handle_add_to_crew(crew),
        "4":  lambda: handle_list_crew(crew),
        "5":  lambda: handle_add_car(inventory),
        "6":  lambda: handle_add_parts(inventory),
        "7":  lambda: handle_add_tools(inventory),
        "8":  lambda: handle_add_money(inventory),
        "9":  lambda: handle_view_inventory(inventory),
        "10": lambda: handle_create_race(race),
        "11": lambda: handle_add_race_entry(race),
        "12": lambda: handle_view_race_entries(race),
        "13": lambda: handle_record_result(results),
        "14": lambda: handle_create_mission(mission),
        "15": lambda: handle_start_mission(mission),
        "16": lambda: handle_list_missions(mission),
        "17": lambda: handle_repair_car(garage),
        "18": lambda: handle_view_leaderboard(leaderboard),
    }

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "19":
            print("Goodbye.")
            break
        handler = handlers.get(choice)
        if handler is None:
            print("Invalid option.")
            continue
        try:
            handler()
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
