# helpers/api_client.py
import requests
from data.test_data import *


class StellarBurgersAPI:
    def __init__(self):
        self.base_url = "https://stellarburgers.education-services.ru"
        self.session = requests.Session()
        self.token = None

    def _get_headers(self, auth=True):
        """Получить заголовки для запроса."""
        headers = {
            'Content-Type': 'application/json'
        }
        if auth and self.token:
            # ИСПРАВЛЕНО: добавлен префикс Bearer
            headers['Authorization'] = f"Bearer {self.token}"
        return headers

    def create_user(self, email, password, name):
        """Создать пользователя."""
        url = f"{self.base_url}/api/auth/register"
        payload = {
            "email": email,
            "password": password,
            "name": name
        }
        response = self.session.post(url, json=payload)

        # Сохраняем токен если регистрация успешна
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success") and "accessToken" in response_data:
                self.token = response_data["accessToken"]

        return response

    def login_user(self, email, password):
        """Логин пользователя."""
        url = f"{self.base_url}/api/auth/login"
        payload = {
            "email": email,
            "password": password
        }
        response = self.session.post(url, json=payload)

        # Сохраняем токен если логин успешен
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("success") and "accessToken" in response_data:
                self.token = response_data["accessToken"]

        return response

    def update_user(self, email=None, password=None, name=None, auth=True):
        """Обновить данные пользователя."""
        url = f"{self.base_url}/api/auth/user"
        payload = {}
        if email:
            payload["email"] = email
        if password:
            payload["password"] = password
        if name:
            payload["name"] = name

        headers = self._get_headers(auth)
        response = self.session.patch(url, json=payload, headers=headers)
        return response

    def get_user_orders(self, auth=True):
        """Получить заказы пользователя."""
        url = f"{self.base_url}/api/orders"
        headers = self._get_headers(auth)
        response = self.session.get(url, headers=headers)
        return response

    def create_order(self, ingredients, auth=True):
        """Создать заказ."""
        url = f"{self.base_url}/api/orders"
        payload = {
            "ingredients": ingredients
        }
        headers = self._get_headers(auth)
        response = self.session.post(url, json=payload, headers=headers)
        return response

    def get_ingredients(self):
        """Получить список ингредиентов."""
        url = f"{self.base_url}/api/ingredients"
        response = self.session.get(url)
        return response

    def delete_user(self):
        """Удалить пользователя (требуется токен)."""
        if not self.token:
            return

        url = f"{self.base_url}/api/auth/user"
        headers = self._get_headers()
        response = self.session.delete(url, headers=headers)
        return response

    def get_user_info(self, auth=True):
        """Получить информацию о пользователе (для отладки)."""
        url = f"{self.base_url}/api/auth/user"
        headers = self._get_headers(auth)
        response = self.session.get(url, headers=headers)
        return response