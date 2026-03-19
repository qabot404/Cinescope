from clients.api.auth_api import AuthAPI
from clients.api.movies_api import MoviesApi
from clients.api.user_api import UserAPI
from constants import API_BASE_URL, BASE_URL


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
        self.movies_api = MoviesApi(session, API_BASE_URL)
