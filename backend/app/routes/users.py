"""
User management routes.

Provides basic CRUD for system users (admins, managers, viewers).
Authentication / hashing is intentionally stubbed for now.
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import User, UserCreate

router = APIRouter(prefix="/users", tags=["Users"])

# ── In-memory store ──────────────────────────────────────────────────────────

_users: dict[int, User] = {}
_next_id: int = 1


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[User], summary="List all users")
async def list_users():
    return list(_users.values())


@router.get("/{user_id}", response_model=User, summary="Get user by ID")
async def get_user(user_id: int):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    return _users[user_id]


@router.post("/", response_model=User, status_code=201, summary="Register a new user")
async def create_user(user_in: UserCreate):
    global _next_id
    # TODO: hash password, check duplicates
    user = User(id=_next_id, username=user_in.username, email=user_in.email, role=user_in.role)
    _users[_next_id] = user
    _next_id += 1
    return user


@router.delete("/{user_id}", status_code=204, summary="Delete a user")
async def delete_user(user_id: int):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    del _users[user_id]
