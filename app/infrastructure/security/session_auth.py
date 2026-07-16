from functools import wraps

from flask import redirect, session, url_for

SESSION_USER_ID_KEY = "user_id"


def login_user_session(user_id: int) -> None:
    session[SESSION_USER_ID_KEY] = user_id


def logout_user_session() -> None:
    session.pop(SESSION_USER_ID_KEY, None)


def current_user_id():
    return session.get(SESSION_USER_ID_KEY)


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if current_user_id() is None:
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper
