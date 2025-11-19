import pytest
import allure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from helpers.api_client import StellarBurgersAPI
from data.test_data import *


@allure.feature("Логин пользователя")
class TestUserLogin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.api = StellarBurgersAPI()
        self.user_created = False
        yield
        # Удаляем пользователя после теста, если он был создан
        if self.user_created:
            try:
                self.api.delete_user()
            except:
                pass

    @allure.story("Логин пользователя")
    @allure.title("Успешный логин под существующим пользователем")
    def test_login_existing_user_success(self):
        # Сначала создаем пользователя
        self.api.create_user(**EXISTING_USER)
        self.user_created = True

        with allure.step("Выполнить логин"):
            response = self.api.login_user(EXISTING_USER["email"], EXISTING_USER["password"])

        with allure.step("Проверить успешный логин"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert "accessToken" in response_data

    @allure.story("Логин пользователя")
    @allure.title("Логин с неверными credentials")
    def test_login_invalid_credentials_fail(self):
        with allure.step("Попытаться войти с неверными данными"):
            response = self.api.login_user("wrong@email.com", "wrongpassword")

        with allure.step("Проверить ошибку авторизации"):
            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] == False
            assert response_data["message"] == "email or password are incorrect"