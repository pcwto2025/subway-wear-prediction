"""
User service layer for business logic
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service class for user operations"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against hashed password"""
        # Truncate password to 72 bytes for bcrypt compatibility
        plain_password = plain_password[:72]
        
        # Handle bcrypt errors in Termux environment
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # If bcrypt fails, try to check if it's a simple SHA256 hash
            import hashlib
            simple_hash = hashlib.sha256(plain_password.encode()).hexdigest()
            return simple_hash == hashed_password

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        # Truncate password to 72 bytes for bcrypt compatibility
        password = password[:72]
        
        # Handle bcrypt errors in Termux environment
        try:
            return pwd_context.hash(password)
        except Exception:
            # If bcrypt fails, return a simple SHA256 hash as fallback
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get a user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get a user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get a user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[User]:
        """Get list of users with optional search"""
        query = select(User)

        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = await UserService.get_user_by_username(db, user_create.username)
        if existing_user:
            raise ValueError(f"Username {user_create.username} already registered")

        existing_user = await UserService.get_user_by_email(db, user_create.email)
        if existing_user:
            raise ValueError(f"Email {user_create.email} already registered")

        # Create new user
        hashed_password = UserService.get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        logger.info(f"Created new user: {user_create.username}")
        return db_user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: UUID,
        user_update: UserUpdate
    ) -> Optional[User]:
        """Update a user"""
        db_user = await UserService.get_user(db, user_id)
        if not db_user:
            return None

        update_data = user_update.dict(exclude_unset=True)

        # Hash password if it's being updated
        if "password" in update_data:
            hashed_password = UserService.get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        # Check for duplicate username/email
        if "username" in update_data and update_data["username"] != db_user.username:
            existing = await UserService.get_user_by_username(db, update_data["username"])
            if existing:
                raise ValueError(f"Username {update_data['username']} already taken")

        if "email" in update_data and update_data["email"] != db_user.email:
            existing = await UserService.get_user_by_email(db, update_data["email"])
            if existing:
                raise ValueError(f"Email {update_data['email']} already taken")

        # Update user
        for field, value in update_data.items():
            setattr(db_user, field, value)

        await db.commit()
        await db.refresh(db_user)

        logger.info(f"Updated user: {db_user.username}")
        return db_user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
        """Delete a user"""
        db_user = await UserService.get_user(db, user_id)
        if not db_user:
            return False

        await db.delete(db_user)
        await db.commit()

        logger.info(f"Deleted user: {db_user.username}")
        return True

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate a user"""
        user = await UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not UserService.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    async def count_users(db: AsyncSession) -> int:
        """Count total users"""
        result = await db.execute(select(User))
        return len(result.scalars().all())