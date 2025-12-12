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


class CommentNotFoundError(Exception):
    def __init__(self, comment_id):
        self.comment_id = comment_id
        super().__init__()

    def __str__(self):
        return f"Comment {self.comment_id} not found"