"""Module for creating and managing crew missions."""

from modules.registration import VALID_ROLES

VALID_MISSION_TYPES = {"delivery", "rescue"}


class Mission:
    """Manages missions that require specific crew roles to execute."""

    def __init__(self, crew):
        self.crew = crew
        # dict[int, dict] — mission_id ->
        #   {"type": str ("delivery" | "rescue"), "required_roles": list[str], "status": str}
        self.missions = {}
        self._next_id = 1

    def create_mission(self, mission_type, required_roles):
        """Create a new mission. Type must be one of VALID_MISSION_TYPES."""
        if mission_type not in VALID_MISSION_TYPES:
            valid = ', '.join(sorted(VALID_MISSION_TYPES))
            raise ValueError(
                f"Invalid mission type '{mission_type}'. Must be one of: {valid}"
            )
        for role in required_roles:
            if role not in VALID_ROLES:
                valid = ', '.join(sorted(VALID_ROLES))
                raise ValueError(
                    f"Invalid role '{role}'. Must be one of: {valid}"
                )
        mission_id = self._next_id
        self._next_id += 1
        self.missions[mission_id] = {
            "type": mission_type,
            "required_roles": required_roles,
            "status": "created",
        }
        return mission_id

    def start_mission(self, mission_id):
        """Start a mission, verifying all required roles are available in the crew."""
        if mission_id not in self.missions:
            raise ValueError(f"Mission {mission_id} does not exist")
        mission = self.missions[mission_id]
        for role in mission["required_roles"]:
            if not self.crew.has_role(role):
                raise ValueError(f"No crew member with role '{role}' available")
        mission["status"] = "active"

    def list_missions(self):
        """Return all missions as a dict keyed by mission_id."""
        return self.missions
