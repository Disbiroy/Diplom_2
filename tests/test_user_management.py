import pytest
import allure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from helpers.api_client import StellarBurgersAPI
from data.test_data import *


@allure.feature("API Tests for User Management")
class TestUserManagement:

    @allure.story("Изменение данных пользователя")
    @allure.title("Успешное изменение данных пользователя с авторизацией")
    def test_update_user_with_auth_success(self, authenticated_user):
        with allure.step("Обновить данные пользователя"):
            response = authenticated_user.update_user(**UPDATED_USER_DATA)

        with allure.step("Проверить успешное обновление"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert response_data["user"]["email"] == UPDATED_USER_DATA["email"]
            assert response_data["user"]["name"] == UPDATED_USER_DATA["name"]

    @allure.story("Изменение данных пользователя")
    @allure.title("Изменение данных пользователя без авторизации")
    def test_update_user_without_auth_fail(self, api_client):
        with allure.step("Попытаться обновить данные без авторизации"):
            response = api_client.update_user(auth=False, **UPDATED_USER_DATA)

        with allure.step("Проверить ошибку авторизации"):
            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] == False
            assert response_data["message"] == "You should be authorised"

    @allure.story("Изменение данных пользователя")
    @allure.title("Изменение email на уже существующий")
    def test_update_user_existing_email_fail(self, api_client):
        # Создаем первого пользователя
        api_client.create_user(**VALID_USER)
        api_client.login_user(VALID_USER["email"], VALID_USER["password"])

        # Создаем второго пользователя
        second_user_api = StellarBurgersAPI()
        second_user_api.create_user(**EXISTING_USER)

        with allure.step("Попытаться изменить email на существующий"):
            response = api_client.update_user(email=EXISTING_USER["email"])

        with allure.step("Проверить ошибку конфликта"):
            assert response.status_code == 403
            response_data = response.json()
            assert response_data["success"] == False
            assert response_data["message"] == "User with such email already exists"

        # Удаляем обоих пользователей
        try:
            api_client.delete_user()
            second_user_api.delete_user()
        except:
            pass