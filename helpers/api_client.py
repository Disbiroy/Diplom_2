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