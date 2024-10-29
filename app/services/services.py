from sqlalchemy.orm import Session
from sqlalchemy.testing.pickleable import User

from ..models.models import UserCreate, UserPreferenceCreate, MealPlanCreate


class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        db_user = User(uid=user.uid, email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()


class UserPreference:
    @staticmethod
    def create_preference(db: Session, user_id: int, preferences: UserPreferenceCreate):
        db_preferences = UserPreference(
            user_id=user_id,
            **preferences.dict()
        )
        db.add(db_preferences)
        db.commit()
        db.refresh(db_preferences)
        return db_preferences

    @staticmethod
    def get_preferences(db: Session, user_id: int):
        return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()


class PreferenceService:
    @staticmethod
    def create_preference(db: Session, user_id: int, preferences: UserPreferenceCreate):
        db_preferences = UserPreference(
            user_id=user_id,
            **preferences.dict()
        )
        db.add(db_preferences)
        db.commit()
        db.refresh(db_preferences)
        return db_preferences

    @staticmethod
    def get_preferences(db: Session, user_id: int):
        return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()


class MealPlan:
    @staticmethod
    def create_meal_plan(db: Session, user_id: int, meal_plan: MealPlanCreate):
        db_meal_plan = MealPlan(
            user_id=user_id,
            **meal_plan.dict()
        )
        db.add(db_meal_plan)
        db.commit()
        db.refresh(db_meal_plan)
        return db_meal_plan

    @staticmethod
    def get_user_meal_plans(db: Session, user_id: int):
        return db.query(MealPlan).filter(MealPlan.user_id == user_id).all()


class MealPlanService:
    @staticmethod
    def create_meal_plan(db: Session, user_id: int, meal_plan: MealPlanCreate):
        db_meal_plan = MealPlan(
            user_id=user_id,
            **meal_plan.dict()
        )
        db.add(db_meal_plan)
        db.commit()
        db.refresh(db_meal_plan)
        return db_meal_plan

    @staticmethod
    def get_user_meal_plans(db: Session, user_id: int):
        return db.query(MealPlan).filter(MealPlan.user_id == user_id).all()
