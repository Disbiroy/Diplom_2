import pytest
import allure
from helpers.api_client import StellarBurgersAPI
from data.test_data import *


@allure.feature("Создание заказа")
class TestOrderCreation:

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

    @allure.story("Создание заказа")
    @allure.title("Создание заказа с авторизацией")
    def test_create_order_with_auth_success(self):
        # Создаем пользователя и логинимся
        self.api.create_user(**VALID_USER)
        self.api.login_user(VALID_USER["email"], VALID_USER["password"])
        self.user_created = True

        # Получаем список ингредиентов
        ingredients_response = self.api.get_ingredients()
        valid_ingredients = [ingredient["_id"] for ingredient in ingredients_response.json()["data"][:2]]

        with allure.step("Создать заказ с авторизацией"):
            response = self.api.create_order(valid_ingredients)

        with allure.step("Проверить успешное создание заказа"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert "order" in response_data

    @allure.story("Создание заказа")
    @allure.title("Создание заказа без авторизации")
    def test_create_order_without_auth_fail(self):
        # Получаем список ингредиентов
        ingredients_response = self.api.get_ingredients()
        valid_ingredients = [ingredient["_id"] for ingredient in ingredients_response.json()["data"][:2]]

        with allure.step("Создать заказ без авторизации"):
            response = self.api.create_order(valid_ingredients, auth=False)

        with allure.step("Проверить ошибку авторизации"):
            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] == False
            assert response_data["message"] == "You should be authorised"

    @allure.story("Создание заказа")
    @allure.title("Создание заказа без ингредиентов")
    def test_create_order_without_ingredients_fail(self):
        # Создаем пользователя и логинимся
        self.api.create_user(**VALID_USER)
        self.api.login_user(VALID_USER["email"], VALID_USER["password"])
        self.user_created = True

        with allure.step("Создать заказ без ингредиентов"):
            response = self.api.create_order([])

        with allure.step("Проверить ошибку валидации"):
            assert response.status_code == 400
            response_data = response.json()
            assert response_data["success"] == False
            assert response_data["message"] == "Ingredient ids must be provided"

    @allure.story("Создание заказа")
    @allure.title("Создание заказа с неверным хешем ингредиентов")
    def test_create_order_invalid_ingredient_hash(self):
        # Создаем пользователя и логинимся
        self.api.create_user(**VALID_USER)
        self.api.login_user(VALID_USER["email"], VALID_USER["password"])
        self.user_created = True

        invalid_ingredients = ["invalid_hash_1", "invalid_hash_2"]

        with allure.step("Создать заказ с неверными хешами ингредиентов"):
            response = self.api.create_order(invalid_ingredients)

        with allure.step("Проверить ошибку"):
            assert response.status_code == 500
            response_data = response.json()
            assert response_data["success"] == False