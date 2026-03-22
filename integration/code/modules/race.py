"""Module for creating and managing race events and their entries."""


class Race:
    """Manages race events, including creation and driver/car entries."""

    def __init__(self, crew, inventory):
        self.crew = crew
        self.inventory = inventory
        # dict[int, dict] — race_id -> {"name": str, "status": str,
        #                                "entries": list[{"driver": str, "car": str}]}
        self.races = {}
        self._next_id = 1

    def create_race(self, name):
        """Create a new race event. Returns the race_id."""
        race_id = self._next_id
        self._next_id += 1
        self.races[race_id] = {"name": name, "entries": [], "status": "pending"}
        return race_id

    def add_entry(self, race_id, driver, car):
        """Add a driver/car entry to an existing race."""
        if race_id not in self.races:
            raise ValueError(f"Race {race_id} does not exist")
        if self.crew.get_role(driver) != "driver":
            raise ValueError(f"{driver} is not a driver")
        if self.inventory.get_car(car) != "ok":
            raise ValueError(f"Car '{car}' is not available or is damaged")
        entries = self.races[race_id]["entries"]
        if any(e["driver"] == driver for e in entries):
            raise ValueError(f"{driver} is already entered in race {race_id}")
        if any(e["car"] == car for e in entries):
            raise ValueError(f"Car '{car}' is already entered in race {race_id}")
        entries.append({"driver": driver, "car": car})

    def list_races(self):
        """Return all races as a dict keyed by race_id."""
        return self.races
