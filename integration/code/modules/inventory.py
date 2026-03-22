"""Module for managing team inventory including cars, parts, tools, and cash."""


class Inventory:
    """Tracks cars, parts, tools, and cash available to the team."""

    def __init__(self):
        self.cars = {}   # dict[str, str] — car_name -> status ("ok" | "damaged")
        self.parts = []  # list[str] — part names available for repairs
        self.tools = []  # list[str] — tool names in inventory
        self.cash = 0    # int — current cash balance

    def add_car(self, name):
        """Add a new car to inventory with status 'ok'."""
        self.cars[name] = "ok"

    def add_parts(self, part):
        """Add a part to the parts list."""
        self.parts.append(part)

    def add_tools(self, tool):
        """Add a tool to the tools list."""
        self.tools.append(tool)

    def add_cash(self, amount):
        """Increase the cash balance by the given amount."""
        self.cash += amount

    def spend_cash(self, amount):
        """Deduct amount from cash if sufficient funds exist. Returns True on success."""
        if self.cash >= amount:
            self.cash -= amount
            return True
        return False

    def get_car(self, name):
        """Return the status of a car, or None if not found."""
        return self.cars.get(name)

    def list_inventory(self):
        """Return a summary of all inventory items."""
        return {
            "cars": self.cars,
            "tools": self.tools,
            "cash": self.cash,
            "parts": self.parts,
        }
