from fastapi_users.authentication import JWTAuthentication
from app import settings

token_lifetime = settings.JWT_TOKEN_LIFETIME
jwt_authentication = JWTAuthentication(secret=settings.SECRET,
                                       lifetime_seconds=token_lifetime,
                                       tokenUrl="auth/jwt/login")
