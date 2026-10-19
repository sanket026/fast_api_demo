from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """
    Data access repository for User entity operations.
    """

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Fetch a single user by primary ID."""
        return db.scalar(select(User).where(User.id == user_id))

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Fetch a user by exact email match."""
        return db.scalar(select(User).where(User.email == email))

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Fetch a user by exact username match."""
        return db.scalar(select(User).where(User.username == username))

    def get_multi(self, db: Session, skip: int = 0, limit: int = 20) -> Tuple[List[User], int]:
        """
        Fetch paginated users and the total count.
        Returns a tuple of (items, total_count).
        """
        total_count = db.scalar(select(func.count()).select_from(User)) or 0
        statement = select(User).order_by(User.id.asc()).offset(skip).limit(limit)
        items = list(db.scalars(statement).all())
        return items, total_count

    def create(self, db: Session, user_in: UserCreate) -> User:
        """Insert a new user record into the database."""
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            full_name=user_in.full_name,
            is_active=user_in.is_active,
        )
        db.add(db_user)
        db.flush()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, db_user: User, user_in: UserUpdate) -> User:
        """Update an existing user record with non-null provided values."""
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.flush()
        db.refresh(db_user)
        return db_user

    def delete(self, db: Session, db_user: User) -> None:
        """Delete a user record from the database."""
        db.delete(db_user)
        db.flush()


user_repository = UserRepository()

