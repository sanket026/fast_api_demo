from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService, user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
    description="Registers a new user record in the database. Email and username must be unique.",
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    service: UserService = Depends(lambda: user_service),
) -> UserResponse:
    """Create a new user."""
    return service.create_user(db, user_in)


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Users",
    description="Retrieves a paginated list of user records.",
)
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max number of records to return"),
    db: Session = Depends(get_db),
    service: UserService = Depends(lambda: user_service),
) -> UserListResponse:
    """Retrieve users with pagination."""
    items, total = service.get_users(db, skip=skip, limit=limit)
    return UserListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User by ID",
    description="Retrieves a single user record by its unique ID.",
)
def get_user(
    user_id: int = Path(..., ge=1, description="The unique ID of the user"),
    db: Session = Depends(get_db),
    service: UserService = Depends(lambda: user_service),
) -> UserResponse:
    """Get user by primary ID."""
    return service.get_user_by_id(db, user_id=user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User",
    description="Updates existing user fields. If updating email or username, uniqueness is verified.",
)
def update_user(
    user_in: UserUpdate,
    user_id: int = Path(..., ge=1, description="The unique ID of the user"),
    db: Session = Depends(get_db),
    service: UserService = Depends(lambda: user_service),
) -> UserResponse:
    """Update an existing user."""
    return service.update_user(db, user_id=user_id, user_in=user_in)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User",
    description="Deletes a user record by ID. Returns 204 No Content on success.",
)
def delete_user(
    user_id: int = Path(..., ge=1, description="The unique ID of the user"),
    db: Session = Depends(get_db),
    service: UserService = Depends(lambda: user_service),
) -> None:
    """Delete a user by primary ID."""
    service.delete_user(db, user_id=user_id)

