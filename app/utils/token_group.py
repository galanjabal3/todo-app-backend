import uuid
from datetime import timedelta
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

_serializer = None

def get_serializer():
    global _serializer

    if _serializer is None:
        from app.config import config
        secret = config.SECRET_KEY
        if not secret:
            raise ValueError("SECRET_KEY not found")
        _serializer = URLSafeTimedSerializer(secret, salt="group-invite")

    return _serializer

# Generate Token Join Group
def generate_group_invite_token(group_id: uuid.UUID, expires_days: int = 7):
    serializer = get_serializer()
    return serializer.dumps({
        "group_id": str(group_id),
        "expires_days": expires_days
    })

def verify_group_invite_token(token: str, expires_days: int = 7):
    serializer = get_serializer()
    max_age = int(timedelta(days=expires_days).total_seconds())
    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except SignatureExpired:
        raise ValueError("Invite link expired")
    except BadSignature:
        raise ValueError("Invalid invite token")
