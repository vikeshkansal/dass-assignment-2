"""Module for managing crew members and their assigned roles."""


class Crew:
    """Tracks registered members and their roles and skill levels."""

    def __init__(self, registration):
        self.registration = registration
        # dict[str, dict] — name -> {"role": str, "skill_level": int}
        # role is the same value set during registration (e.g. "driver", "mechanic")
        self.skills = {}

    def assign_role(self, name, skill_level):
        """Add a registered member to the crew using their registration role."""
        role = self.registration.get_member(name)
        if role is None:
            raise ValueError(f"{name} is not registered")
        self.skills[name] = {"role": role, "skill_level": skill_level}

    def get_role(self, name):
        """Return the role of a crew member, or None if not found."""
        entry = self.skills.get(name)
        if entry:
            return entry["role"]
        return None

    def has_role(self, role):
        """Return True if any crew member holds the given role."""
        return any(entry["role"] == role for entry in self.skills.values())

    def list_crew(self):
        """Return all crew members and their skill entries."""
        return self.skills
