import pytest
from unittest.mock import Mock, patch
import requests


@pytest.fixture(autouse=True)
def mock_requests():
    """Мокаем все HTTP запросы для тестирования без интернета"""

    # Мок для успешного создания пользователя
    success_response = Mock()
    success_response.status_code = 200
    success_response.json.return_value = {
        "success": True,
        "accessToken": "test_token_123",
        "refreshToken": "refresh_token_123",
        "user": {"email": "test@test.com", "name": "Test User"}
    }

    # Мок для ошибки "пользователь уже существует"
    user_exists_response = Mock()
    user_exists_response.status_code = 403
    user_exists_response.json.return_value = {
        "success": False,
        "message": "User already exists"
    }

    # Мок для ошибки авторизации
    auth_error_response = Mock()
    auth_error_response.status_code = 401
    auth_error_response.json.return_value = {
        "success": False,
        "message": "email or password are incorrect"
    }

    # Мок для ошибки валидации
    validation_error_response = Mock()
    validation_error_response.status_code = 403
    validation_error_response.json.return_value = {
        "success": False,
        "message": "Email, password and name are required fields"
    }

    # Мок для получения ингредиентов
    ingredients_response = Mock()
    ingredients_response.status_code = 200
    ingredients_response.json.return_value = {
        "success": True,
        "data": [
            {"_id": "ingredient_1", "name": "Булка", "type": "bun", "price": 100},
            {"_id": "ingredient_2", "name": "Котлета", "type": "main", "price": 200},
            {"_id": "ingredient_3", "name": "Сыр", "type": "main", "price": 50}
        ]
    }

    # Мок для успешного создания заказа
    order_success_response = Mock()
    order_success_response.status_code = 200
    order_success_response.json.return_value = {
        "success": True,
        "name": "Бургер",
        "order": {"number": 12345}
    }

    # Мок для ошибки создания заказа без авторизации
    order_auth_error_response = Mock()
    order_auth_error_response.status_code = 401
    order_auth_error_response.json.return_value = {
        "success": False,
        "message": "You should be authorised"
    }

    # Мок для ошибки создания заказа без ингредиентов
    order_no_ingredients_response = Mock()
    order_no_ingredients_response.status_code = 400
    order_no_ingredients_response.json.return_value = {
        "success": False,
        "message": "Ingredient ids must be provided"
    }

    # Мок для успешного удаления пользователя
    delete_success_response = Mock()
    delete_success_response.status_code = 200
    delete_success_response.json.return_value = {
        "success": True,
        "message": "User successfully deleted"
    }

    # Мок для ошибки с неверными хешами ингредиентов
    invalid_hash_response = Mock()
    invalid_hash_response.status_code = 500
    invalid_hash_response.json.return_value = {
        "success": False,
        "message": "Internal Server Error"
    }

    # Создаем словарь для хранения моков
    mock_responses = {
        'register_success': success_response,
        'register_exists': user_exists_response,
        'register_validation': validation_error_response,
        'login_success': success_response,
        'login_error': auth_error_response,
        'ingredients': ingredients_response,
        'order_success': order_success_response,
        'order_auth_error': order_auth_error_response,
        'order_no_ingredients': order_no_ingredients_response,
        'delete_success': delete_success_response,
        'invalid_hash': invalid_hash_response
    }

    # Патчим requests.Session методы
    with patch('requests.Session.post') as mock_post, \
            patch('requests.Session.get') as mock_get, \
            patch('requests.Session.delete') as mock_delete:

        def side_effect_post(url, **kwargs):
            if 'register' in url:
                data = kwargs.get('json', {})
                if data.get('email') == 'existing_user@test.com':
                    return mock_responses['register_exists']
                elif not data.get('email') or not data.get('password') or not data.get('name'):
                    return mock_responses['register_validation']
                else:
                    return mock_responses['register_success']
            elif 'login' in url:
                data = kwargs.get('json', {})
                if data.get('email') == 'wrong@email.com':
                    return mock_responses['login_error']
                else:
                    return mock_responses['login_success']
            elif 'orders' in url:
                data = kwargs.get('json', {})
                headers = kwargs.get('headers', {})

                if not headers.get('Authorization'):
                    return mock_responses['order_auth_error']
                elif not data.get('ingredients'):
                    return mock_responses['order_no_ingredients']
                elif data.get('ingredients') == ['invalid_hash_1', 'invalid_hash_2']:
                    return mock_responses['invalid_hash']
                else:
                    return mock_responses['order_success']
            return mock_responses['register_success']

        def side_effect_get(url, **kwargs):
            if 'ingredients' in url:
                return mock_responses['ingredients']
            return mock_responses['register_success']

        def side_effect_delete(url, **kwargs):
            if 'user' in url:
                return mock_responses['delete_success']
            return mock_responses['register_success']

        mock_post.side_effect = side_effect_post
        mock_get.side_effect = side_effect_get
        mock_delete.side_effect = side_effect_delete

        yield