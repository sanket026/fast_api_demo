from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for shared user attributes."""

    email: EmailStr = Field(..., description="Unique email address of the user", examples=["john.doe@example.com"])
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Unique username containing letters, numbers, underscores, and hyphens",
        examples=["johndoe"],
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional full name of the user",
        examples=["John Doe"],
    )
    is_active: bool = Field(True, description="Whether the user account is active")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating an existing user (all fields optional)."""

    email: Optional[EmailStr] = Field(None, description="Updated email address", examples=["john.updated@example.com"])
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Updated username",
        examples=["johndoe_updated"],
    )
    full_name: Optional[str] = Field(None, max_length=255, description="Updated full name")
    is_active: Optional[bool] = Field(None, description="Updated active status")


class UserResponse(UserBase):
    """Schema for user responses returned by the API."""

    id: int = Field(..., description="Primary identifier of the user", examples=[1])
    created_at: datetime = Field(..., description="Timestamp when user was created")
    updated_at: datetime = Field(..., description="Timestamp when user was last updated")

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for paginated list of users."""

    items: List[UserResponse] = Field(..., description="List of user records")
    total: int = Field(..., ge=0, description="Total number of users matching the query", examples=[42])
    skip: int = Field(..., ge=0, description="Number of items skipped", examples=[0])
    limit: int = Field(..., ge=1, description="Number of items per page", examples=[20])

