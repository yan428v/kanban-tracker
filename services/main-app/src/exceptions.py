class TeamNotFoundError(Exception):
    def __init__(self, team_id):
        self.team_id = team_id
        super().__init__()

    def __str__(self):
        return f"Team {self.team_id} not found"


class TeamMemberNotFoundError(Exception):
    def __init__(self, team_id, user_id):
        self.team_id = team_id
        self.user_id = user_id
        super().__init__()

    def __str__(self):
        return f"Team member with team_id {self.team_id} and user_id {self.user_id} not found"


class InvalidCredentialsError(Exception):
    def __init__(self, detail: str = "Could not validate credentials"):
        self.detail = detail
        super().__init__()

    def __str__(self):
        return self.detail
