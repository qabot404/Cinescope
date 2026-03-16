from clients.api.auth_api import AuthAPI
from clients.api.user_api import UserAPI
from constants import BASE_URL


class ApiManager:
    """
    Класс для управления API-классами с единой HTTP-сессией.
    """

    def __init__(self, session):
        """
        Инициализация ApiManager.

        :param session: HTTP-сессия, используемая всеми API-классами.
        """
        self.session = session
        self.auth_api = AuthAPI(session, BASE_URL)
        self.user_api = UserAPI(session, BASE_URL)
