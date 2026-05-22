from app.extension import db
from app.api.models.user import User
from sqlalchemy.exc import SQLAlchemyError

# 允许更新的字段白名单（防止批量赋值漏洞）
ALLOWED_UPDATE_FIELDS = {'username', 'email', 'is_active'}


class UserDao:
    @staticmethod
    def create_user(username, password, email):
        try:
            user = User(username=username, password=password, email=email)
            db.session.add(user)
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_user_by_id(user_id):
        # 使用 db.session.get() 替代已弃用的 query.get()
        return db.session.get(User, user_id)

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def update_user(user_id, data):
        try:
            user = db.session.get(User, user_id)
            if not user:
                return None

            # 使用白名单只允许更新特定字段
            for key, value in data.items():
                if key in ALLOWED_UPDATE_FIELDS:
                    setattr(user, key, value)

            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_user(user_id):
        try:
            user = db.session.get(User, user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
