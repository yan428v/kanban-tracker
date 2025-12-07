class TeamNotFoundError(Exception):
    def __init__(self, team_id):
        self.team_id = team_id
        super().__init__()

    def __str__(self):
        return f"Team {self.team_id} not found"

