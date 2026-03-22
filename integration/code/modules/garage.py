"""Module for managing car repairs in the garage."""


class Garage:
    """Handles repair of damaged cars using parts from inventory."""

    def __init__(self, inventory):
        self.inventory = inventory

    def repair_car(self, car_name, required_parts):
        """Repair a damaged car. required_parts is a list of part names needed.
        Each required part must exist in inventory; they are consumed on repair."""
        if self.inventory.get_car(car_name) is None:
            raise ValueError(f"Car '{car_name}' not in inventory")
        if self.inventory.get_car(car_name) == "ok":
            raise ValueError(f"Car '{car_name}' is not damaged")
        for part in required_parts:
            if part not in self.inventory.parts:
                raise ValueError(f"Missing required part: '{part}'")
        for part in required_parts:
            self.inventory.parts.remove(part)
        self.inventory.cars[car_name] = "ok"

    def list_damaged(self):
        """Return a list of car names currently marked as damaged."""
        return [name for name, status in self.inventory.cars.items() if status == "damaged"]
