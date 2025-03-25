from contextvars import ContextVar

user_context = ContextVar("current_user", default=None)