from datetime import datetime, timezone

class User:
  def __init__(self, username: str, house_id: str, user_id: str):
    self.username = username
    self.house_id = house_id
    self.user_id = user_id
    self.created_at = datetime.now(timezone.utc).isoformat()