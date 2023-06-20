from .models import User, UserCollectionType, UserType


def serialize_user(user: User) -> UserType:
    return {"user": user.__dict__}
