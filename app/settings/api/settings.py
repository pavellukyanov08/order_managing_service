from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    AUTH_USERS_PREFIX: str = '/auth'
    TOKENS_PREFIX: str = '/token'
    USERS_PREFIX: str = '/users'
    ORDERS_PREFIX: str = '/orders'


api_settings = ApiSettings()