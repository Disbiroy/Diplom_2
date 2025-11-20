import pytest
import allure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from helpers.api_client import StellarBurgersAPI
from data.test_data import *


@allure.feature("API Tests for Orders")
class TestOrders:

    @allure.story("Получение заказов пользователя")
    @allure.title("Получение заказов пользователя с авторизацией")
    def test_get_user_orders_with_auth_success(self, authenticated_user):
        with allure.step("Получить заказы пользователя"):
            response = authenticated_user.get_user_orders()

        with allure.step("Проверить успешное получение заказов"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert "orders" in response_data
            assert isinstance(response_data["orders"], list)

    @allure.story("Получение заказов пользователя")
    @allure.title("Получение заказов пользователя без авторизации")
    def test_get_user_orders_without_auth_fail(self, api_client):
        with allure.step("Попытаться получить заказы без авторизации"):
            response = api_client.get_user_orders(auth=False)

        with allure.step("Проверить ошибку авторизации"):
            assert response.status_code == 401
            response_data = response.json()
            assert response_data["success"] == False
            assert response_data["message"] == "You should be authorised"

    @allure.story("Получение заказов пользователя")
    @allure.title("Получение заказов после создания заказа")
    def test_get_user_orders_after_creating_order_success(self, user_with_order):
        with allure.step("Получить заказы пользователя"):
            response = user_with_order.get_user_orders()

        with allure.step("Проверить что заказ есть в списке"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert "orders" in response_data
            assert len(response_data["orders"]) > 0

    @allure.story("Получение заказов пользователя")
    @allure.title("Получение пустого списка заказов для нового пользователя")
    def test_get_empty_orders_for_new_user_success(self, authenticated_user):
        with allure.step("Получить заказы нового пользователя"):
            response = authenticated_user.get_user_orders()

        with allure.step("Проверить пустой список заказов"):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] == True
            assert "orders" in response_data
            assert response_data["orders"] == []