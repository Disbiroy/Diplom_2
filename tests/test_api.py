import pytest
import allure
from helpers.api_client import StellarBurgersAPI
from data.test_data import *


@allure.feature("API Tests for Stellar Burgers")
class TestStellarBurgersAPI:

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

    @allure.story("Изменение данных пользователя")
    @allure.title("Успешное изменение данных пользователя с авторизацией")
    def test_update_user_with_auth_success(self):
        # Создаем пользователя и логинимся
        self.api.create_user(**VALID_USER)
        self.api.login_user(VALID_USER["email"], VALID_USER["password"])
        self.user_created = True

        with allure.step("Обновить данные пользователя"):
            updated_data = {
                "email": generate_random_email(),
                "name": "Updated Name",
                "password": "newpassword123"
            }
            response = self.api.update_user(**updated_data)

        with allure.step("Проверить успешное обновление"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert response_data["user"]["email"] == updated_data["email"]
            assert response_data["user"]["name"] == updated_data["name"]

    @allure.story("Изменение данных пользователя")
    @allure.title("Изменение данных пользователя без авторизации")
    def test_update_user_without_auth_fail(self):
        with allure.step("Попытаться обновить данные без авторизации"):
            updated_data = {
                "email": generate_random_email(),
                "name": "Updated Name"
            }
            response = self.api.update_user(auth=False, **updated_data)

        with allure.step("Проверить ошибку авторизации"):
            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] == False
            assert response_data["message"] == "You should be authorised"

    @allure.story("Изменение данных пользователя")
    @allure.title("Изменение email на уже существующий")
    def test_update_user_existing_email_fail(self):
        # Создаем первого пользователя
        self.api.create_user(**VALID_USER)
        self.api.login_user(VALID_USER["email"], VALID_USER["password"])
        self.user_created = True

        # Создаем второго пользователя (используем EXISTING_USER)
        second_user_api = StellarBurgersAPI()
        second_user_api.create_user(**EXISTING_USER)

        with allure.step("Попытаться изменить email на существующий"):
            response = self.api.update_user(email=EXISTING_USER["email"])

        with allure.step("Проверить ошибку конфликта"):
            assert response.status_code == 403
            response_data = response.json()
            assert response_data["success"] == False
            assert "already exists" in response_data["message"]

        # Удаляем второго пользователя
        second_user_api.login_user(EXISTING_USER["email"], EXISTING_USER["password"])
        second_user_api.delete_user()

    @allure.story("Получение заказов пользователя")
    @allure.title("Получение заказов пользователя с авторизацией")
    def test_get_user_orders_with_auth_success(self):
        # Создаем пользователя и логинимся
        self.api.create_user(**VALID_USER)
        self.api.login_user(VALID_USER["email"], VALID_USER["password"])
        self.user_created = True

        with allure.step("Получить заказы пользователя"):
            response = self.api.get_user_orders()

        with allure.step("Проверить успешное получение заказов"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert "orders" in response_data
            assert isinstance(response_data["orders"], list)

    @allure.story("Получение заказов пользователя")
    @allure.title("Получение заказов пользователя без авторизации")
    def test_get_user_orders_without_auth_fail(self):
        with allure.step("Попытаться получить заказы без авторизации"):
            response = self.api.get_user_orders(auth=False)

        with allure.step("Проверить ошибку авторизации"):
            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] == False
            assert response_data["message"] == "You should be authorised"

    @allure.story("Получение заказов пользователя")
    @allure.title("Получение заказов после создания заказа")
    def test_get_user_orders_after_creating_order_success(self):
        # Создаем пользователя и логинимся
        self.api.create_user(**VALID_USER)
        self.api.login_user(VALID_USER["email"], VALID_USER["password"])
        self.user_created = True

        # Создаем заказ
        ingredients_response = self.api.get_ingredients()
        valid_ingredients = [ingredient["_id"] for ingredient in ingredients_response.json()["data"][:2]]
        self.api.create_order(valid_ingredients)

        with allure.step("Получить заказы пользователя"):
            response = self.api.get_user_orders()

        with allure.step("Проверить что заказ есть в списке"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert len(response_data["orders"]) > 0
            assert "ingredients" in response_data["orders"][0]
            assert "_id" in response_data["orders"][0]

    @allure.story("Получение заказов пользователя")
    @allure.title("Получение пустого списка заказов для нового пользователя")
    def test_get_empty_orders_for_new_user_success(self):
        # Создаем пользователя и логинимся
        self.api.create_user(**VALID_USER)
        self.api.login_user(VALID_USER["email"], VALID_USER["password"])
        self.user_created = True

        with allure.step("Получить заказы нового пользователя"):
            response = self.api.get_user_orders()

        with allure.step("Проверить пустой список заказов"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert response_data["orders"] == []