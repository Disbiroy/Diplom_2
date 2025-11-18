import pytest
import allure
from helpers.api_client import StellarBurgersAPI
from data.test_data import *


@allure.feature("Создание пользователя")
class TestUserCreation:

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
                # Игнорируем ошибки при удалении в тестах
                pass

    @allure.story("Создание пользователя")
    @allure.title("Создание уникального пользователя")
    def test_create_unique_user_success(self):
        with allure.step("Создать уникального пользователя"):
            response = self.api.create_user(**VALID_USER)

        with allure.step("Проверить статус код и ответ"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert "accessToken" in response_data
            self.user_created = True

    @allure.story("Создание пользователя")
    @allure.title("Создание пользователя без обязательного поля")
    @pytest.mark.parametrize("user_data,missing_field", [
        (INVALID_USER_MISSING_EMAIL, "email"),
        (INVALID_USER_MISSING_PASSWORD, "password")
    ])
    def test_create_user_missing_required_field(self, user_data, missing_field):
        with allure.step(f"Создать пользователя без поля {missing_field}"):
            response = self.api.create_user(
                email=user_data["email"],
                password=user_data["password"],
                name=user_data["name"]
            )

        with allure.step("Проверить ошибку валидации"):
            assert response.status_code == 403
            response_data = response.json()
            assert response_data["success"] == False
            assert "message" in response_data