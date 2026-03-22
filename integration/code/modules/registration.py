"""Module for registering and tracking team members."""


VALID_ROLES = {"driver", "mechanic", "owner"}


class Registration:
    """Maintains a registry of team members and their roles."""

    def __init__(self):
        self.members = {}  # dict[str, str] — name -> role ("driver" | "mechanic" | "owner")

    def register(self, name, role):
        """Register a member with the given name and role. Role must be one of VALID_ROLES."""
        if role not in VALID_ROLES:
            valid = ', '.join(sorted(VALID_ROLES))
            raise ValueError(f"Invalid role '{role}'. Must be one of: {valid}")
        if name in self.members:
            raise ValueError(f"'{name}' is already registered")
        self.members[name] = role

    def is_registered(self, name):
        """Return True if the member is already registered."""
        return name in self.members

    def get_member(self, name):
        """Return the role of a member, or None if not found."""
        return self.members.get(name)

    def list_members(self):
        """Return all registered members as a dict."""
        return self.members
