import logging
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.core.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.db.models.user import User
from app.repositories.user_repository import UserRepository, user_repository
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger("app.services.user")


class UserService:
    """
    Business logic layer for User entity management.
    """

    def __init__(self, repo: UserRepository = user_repository) -> None:
        self.repo = repo

    def get_user_by_id(self, db: Session, user_id: int) -> User:
        """
        Retrieves a user by ID or raises UserNotFoundError.
        """
        user = self.repo.get_by_id(db, user_id)
        if not user:
            raise UserNotFoundError(user_id=user_id)
        return user

    def get_users(self, db: Session, skip: int = 0, limit: int = 20) -> Tuple[List[User], int]:
        """
        Retrieves a paginated list of users and the total count.
        """
        return self.repo.get_multi(db, skip=skip, limit=limit)

    def create_user(self, db: Session, user_in: UserCreate) -> User:
        """
        Creates a new user ensuring email and username uniqueness.
        """
        if self.repo.get_by_email(db, user_in.email):
            raise UserAlreadyExistsError(field="email", value=user_in.email)

        if self.repo.get_by_username(db, user_in.username):
            raise UserAlreadyExistsError(field="username", value=user_in.username)

        try:
            user = self.repo.create(db, user_in)
            db.commit()
            db.refresh(user)
            logger.info("Created user with ID %d (username: %s)", user.id, user.username)
            return user
        except Exception:
            db.rollback()
            raise

    def update_user(self, db: Session, user_id: int, user_in: UserUpdate) -> User:
        """
        Updates an existing user, validating uniqueness when email/username change.
        """
        db_user = self.get_user_by_id(db, user_id)

        # Validate unique email if changing
        if user_in.email and user_in.email != db_user.email:
            existing = self.repo.get_by_email(db, user_in.email)
            if existing and existing.id != user_id:
                raise UserAlreadyExistsError(field="email", value=user_in.email)

        # Validate unique username if changing
        if user_in.username and user_in.username != db_user.username:
            existing = self.repo.get_by_username(db, user_in.username)
            if existing and existing.id != user_id:
                raise UserAlreadyExistsError(field="username", value=user_in.username)

        try:
            updated_user = self.repo.update(db, db_user, user_in)
            db.commit()
            db.refresh(updated_user)
            logger.info("Updated user with ID %d", user_id)
            return updated_user
        except Exception:
            db.rollback()
            raise

    def delete_user(self, db: Session, user_id: int) -> None:
        """
        Deletes a user by ID or raises UserNotFoundError.
        """
        db_user = self.get_user_by_id(db, user_id)
        try:
            self.repo.delete(db, db_user)
            db.commit()
            logger.info("Deleted user with ID %d", user_id)
        except Exception:
            db.rollback()
            raise


user_service = UserService()

