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


class CommentNotFoundError(Exception):
    def __init__(self, comment_id):
        self.comment_id = comment_id
        super().__init__()

    def __str__(self):
        return f"Comment {self.comment_id} not found"


class TaskMemberAlreadyExistsError(Exception):
    def __init__(self, task_id, user_id):
        self.task_id = task_id
        self.user_id = user_id
        super().__init__()

    def __str__(self):
        return f"Task member with task_id {self.task_id} and user_id {self.user_id} already exists"


class TeamMemberConflictError(Exception):
    def __init__(self, team_id, user_id):
        self.team_id = team_id
        self.user_id = user_id
        super().__init__()

    def __str__(self):
        return f"Team member with team_id {self.team_id} and user_id {self.user_id} already exists"


class UserNotFoundError(Exception):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__()

    def __str__(self):
        return f"User {self.user_id} not found"
