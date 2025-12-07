class TeamNotFoundError(Exception):
    def __init__(self, team_id):
        self.team_id = team_id
        super().__init__()

    def __str__(self):
        return f"Team {self.team_id} not found"


class TeamMemberNotFoundError(Exception):
    def __init__(self, team_member_id):
        self.team_member_id = team_member_id
        super().__init__()

    def __str__(self):
        return f"Team member {self.team_member_id} not found"


class TeamMemberDuplicateError(Exception):
    def __init__(self, team_id, user_id):
        self.team_id = team_id
        self.user_id = user_id
        super().__init__()

    def __str__(self):
        return f"User {self.user_id} is already a member of team {self.team_id}"
