"""Module for recording race results and computing driver rankings."""


class Results:
    """Records race outcomes and calculates cumulative driver standings."""

    def __init__(self, race, inventory):
        self.race = race
        self.inventory = inventory
        # list[dict] — each: {"race_id": int, "driver": str,
        #                      "position": int, "prize": int, "car": str}
        self.results = []

    def record_result(self, race_id, driver, position, prize, **kwargs):
        """Record a race result for a specific driver. Deducts prize from inventory cash.
        Accepts optional keyword argument car_damaged (bool, default False) to mark
        the driver's car as damaged in inventory."""
        car_damaged = kwargs.get("car_damaged", False)
        races = self.race.list_races()
        if race_id not in races:
            raise ValueError(f"Race {race_id} does not exist")

        entries = races[race_id]["entries"]
        car = None
        for entry in entries:
            if entry["driver"] == driver:
                car = entry["car"]
                break
        if car is None:
            raise ValueError(f"{driver} is not entered in race {race_id}")

        if not self.inventory.spend_cash(prize):
            raise ValueError("Not enough cash to pay out prize")

        if car_damaged:
            self.inventory.cars[car] = "damaged"

        self.results.append({
            "race_id": race_id,
            "driver": driver,
            "position": position,
            "prize": prize,
            "car": car,
        })

    def list_results(self):
        """Return all recorded race results."""
        return self.results
