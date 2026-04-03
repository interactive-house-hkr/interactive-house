from services.src.firebase.firebase_client import get_ref

"""
Store layer for user-related database operations.
Handles reading and writing users and username mappings.
"""

# Retrieves a user from the database by user ID.
def get_user(user_id: str):
    print(f"User store loading user: {user_id}")
    users_ref = get_ref("users")
    return users_ref.child(user_id).get()

# Retrieves a user ID from the username mapping
def get_user_id_by_username(username: str):
    print(f"User store loading username mapping: {username}")
    usernames_ref = get_ref("usernames")
    return usernames_ref.child(username).get()

# Saves user data in the users collection
def save_user(user_id: str, user_data: dict):
    print(f"User store saving user: {user_id}")
    users_ref = get_ref("users")
    users_ref.child(user_id).set(user_data)

# Saves the username to user ID mapping
def save_username(username: str, user_id: str):
    print(f"User store saving username mapping: {username}")
    usernames_ref = get_ref("usernames")
    usernames_ref.child(username).set(user_id)

