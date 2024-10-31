from sqlalchemy.orm import Session
from sqlalchemy.testing.pickleable import User

from app.models.models import UserCreate, UserPreferenceCreate, MealPlanCreate


class UserService:
    @staticmethod
    async def create_user(db: Session, user: UserCreate):
        db_user = User(uid=user.uid, email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()


class UserPreferenceService:
    @staticmethod
    def create_preference(db: Session, user_id: int, preferences: UserPreferenceCreate):
        db_preferences = UserPreferenceService(
        )
        db.add(db_preferences)
        db.commit()
        db.refresh(db_preferences)
        return db_preferences

    @staticmethod
    def get_preferences(db: Session, user_id: int):
        return db.query(UserPreferenceService).filter(UserPreferenceService.user_id == user_id).first()


class MealPlanService:
    @staticmethod
    def create_meal_plan(db: Session, user_id: int, meal_plan: MealPlanCreate):
        db_meal_plan = MealPlanService(
        )
        db.add(db_meal_plan)
        db.commit()
        db.refresh(db_meal_plan)
        return db_meal_plan

    @staticmethod
    def get_user_meal_plans(db: Session, user_id: int):
        return db.query(MealPlanService).filter(MealPlanService.user_id == user_id).all()
