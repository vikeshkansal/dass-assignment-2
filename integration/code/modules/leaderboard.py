"""Module for computing and displaying the race leaderboard."""


class Leaderboard:
    """Computes driver standings from recorded race results."""

    def __init__(self, results):
        self.results = results

    def _compute_rankings(self):
        """Aggregate total prize money per driver and return sorted standings."""
        totals = {}
        for result in self.results.list_results():
            driver = result["driver"]
            totals[driver] = totals.get(driver, 0) + result["prize"]
        return sorted(totals.items(), key=lambda x: x[1], reverse=True)

    def show_leaderboard(self):
        """Return the current driver standings as a sorted list of (driver, total_prize)."""
        return self._compute_rankings()

    def get_rank(self, driver):
        """Return the 1-based rank of a driver, or None if they have no recorded results."""
        for rank, (name, _) in enumerate(self._compute_rankings(), start=1):
            if name == driver:
                return rank
        return None
