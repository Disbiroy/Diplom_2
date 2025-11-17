import requests
import allure


class StellarBurgersAPI:
    BASE_URL = "https://stellarburgers.nomoreparties.site/api"

    def __init__(self):
        self.session = requests.Session()
        self.token = None

    @allure.step("Создать пользователя")
    def create_user(self, email, password, name):
        url = f"{self.BASE_URL}/auth/register"
        payload = {
            "email": email,
            "password": password,
            "name": name
        }
        # Фильтруем None значения
        payload = {k: v for k, v in payload.items() if v is not None}
        response = self.session.post(url, json=payload)
        return response

    @allure.step("Логин пользователя")
    def login_user(self, email, password):
        url = f"{self.BASE_URL}/auth/login"
        payload = {
            "email": email,
            "password": password
        }
        response = self.session.post(url, json=payload)
        if response.status_code == 200:
            self.token = response.json().get("accessToken")
        return response

    @allure.step("Удалить пользователя")
    def delete_user(self):
        if self.token:
            url = f"{self.BASE_URL}/auth/user"
            headers = {"Authorization": self.token}
            response = self.session.delete(url, headers=headers)
            return response
        return None

    @allure.step("Создать заказ")
    def create_order(self, ingredients, auth=True):
        url = f"{self.BASE_URL}/orders"
        headers = {}
        if auth and self.token:
            headers["Authorization"] = self.token

        payload = {"ingredients": ingredients}
        response = self.session.post(url, json=payload, headers=headers)
        return response

    @allure.step("Получить ингредиенты")
    def get_ingredients(self):
        url = f"{self.BASE_URL}/ingredients"
        response = self.session.get(url)
        return response

    @allure.step("Обновить данные пользователя")
    def update_user(self, email=None, password=None, name=None, auth=True):
        url = f"{self.BASE_URL}/auth/user"
        headers = {}
        if auth and self.token:
            headers["Authorization"] = self.token

        payload = {}
        if email is not None:
            payload["email"] = email
        if password is not None:
            payload["password"] = password
        if name is not None:
            payload["name"] = name

        response = self.session.patch(url, json=payload, headers=headers)
        return response

    @allure.step("Получить заказы пользователя")
    def get_user_orders(self, auth=True):
        url = f"{self.BASE_URL}/orders"
        headers = {}
        if auth and self.token:
            headers["Authorization"] = self.token

        response = self.session.get(url, headers=headers)
        return response