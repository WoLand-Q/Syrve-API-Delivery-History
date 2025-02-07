import requests
import json


# Функция для получения токена
def get_access_token(user_id, user_secret):
    url = "https://loyalty.syrve.live/api/0/auth/access_token"
    params = {
        "user_id": user_id,
        "user_secret": user_secret
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        access_token = response.text.strip('"')
        print(f"Access Token: {access_token}")
        return access_token
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {response.text}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None


# Функция для получения истории доставок по телефону
def get_delivery_history(access_token, organization_id, phone):
    url = "https://loyalty.syrve.live/api/0/orders/deliveryHistoryByPhone"
    params = {
        "access_token": access_token,
        "organization": organization_id,
        "phone": phone
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        history = response.json()
        return history
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {response.text}")
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON. Ответ сервера:")
        print(response.text)
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None


# Функция для получения списка организаций
def get_organizations(access_token, request_timeout=30):
    url = "https://loyalty.syrve.live/api/0/organization/list"
    params = {
        "access_token": access_token,
        "request_timeout": request_timeout
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        organizations = response.json()
        return organizations
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching organizations: {http_err} - Response: {response.text}")
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON при получении списка организаций. Ответ сервера:")
        print(response.text)
    except Exception as err:
        print(f"Other error occurred while fetching organizations: {err}")
    return None


# Функция для поиска организации по ID
def find_organization_by_id(organizations, organization_id):
    for org in organizations:
        if org.get("organizationId") == organization_id:
            return org
    return None


# Функция для отображения всех организаций
def display_all_organizations(organizations):
    if not organizations:
        print("Список организаций пуст или не был получен.")
        return

    print("\nСписок всех организаций:")
    for org in organizations:
        org_id = org.get("organizationId", "Неизвестный ID")
        name = org.get("name", "Без названия")
        # Добавьте другие поля по необходимости
        print(f"ID: {org_id}, Название: {name}")


# Основной процесс
def main():
    user_id = ""
    user_secret = ""
    organization_id = ""
    phone = "+"

    # Получение токена
    access_token = get_access_token(user_id, user_secret)
    if not access_token:
        print("Не удалось получить токен доступа.")
        return

    # Получение истории доставок
    history = get_delivery_history(access_token, organization_id, phone)
    if history:
        print("\nИстория доставок:")
        print(json.dumps(history, indent=2, ensure_ascii=False))

        # Извлечение organizationId из первой доставки (предполагается, что все доставки одной организации)
        try:
            first_delivery = history["customersDeliveryHistory"][0]["deliveryHistory"][0]
            org_id = first_delivery.get("organizationId")
            print(f"\nOrganization ID: {org_id}")
        except (IndexError, KeyError, TypeError) as e:
            print("Не удалось извлечь organizationId из истории доставок.")
            org_id = None

        if org_id:
            # Получение списка организаций
            organizations = get_organizations(access_token)
            if organizations:
                # Поиск организации по ID
                organization_info = find_organization_by_id(organizations, org_id)
                if organization_info:
                    print("\nИнформация об организации:")
                    print(json.dumps(organization_info, indent=2, ensure_ascii=False))
                else:
                    print(f"\nОрганизация с ID {org_id} не найдена в списке организаций.")

                # Отображение всех организаций
                display_all_organizations(organizations)
            else:
                print("Не удалось получить список организаций.")
    else:
        print("История доставок не найдена или произошла ошибка.")


if __name__ == "__main__":
    main()
