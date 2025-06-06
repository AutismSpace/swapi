import os
from pathlib import Path
import requests

"""
1. Создайте базовый класс APIRequester:

a. Объекты класса при инициализации должны запоминать атрибут base_url,
в который будет передаваться базовый URL от какого-либо API.

b. В классе необходимо реализовать метод get(),
который должен выполнять GET-запрос с помощью библиотеки requests,
а также перехватывать ошибки в случае их возникновения.
Метод должен возвращать объект класса Response.

c. Хорошая практика после выполнения запроса — проверить статус ответа.
При получении статусов с ошибкой он даёт исключение. Для проверки,
что запрос вернул подходящий статус-код,
используйте метод raise_for_status() объекта класса Response.

"""


class APIRequester:
    # Делаем init c base_url в качестве аргумента
    def __init__(self, base_url):
        # Созраним base_url как атрибут класса APIRequester
        self.base_url = base_url

    # Метод для выполнения Get запроса.
    # Запрос будет состоять из родительской ссылки + Endpoint,
    # который получим в методе get_sw_categories
    # Если все хорошо прошло то возвращаем response, а если попали в except,
    # то возвращаем дырку от бублика
    def get(self, endpoint=""):
        # Запишем в переменную url адрес из атрибута.
        # Сделал подгон под тест, чтобы ссылка корректно валидировалась
        url = self.base_url + "/" + endpoint.lstrip("/")

        # Пробуем выполнить запрос
        try:
            # Запишем ответ в переменную response
            response = requests.get(url)
            # Проверим, что response вернул нам не ошибку (4xx/5xx),
            # а нормальный ответ.
            # Если ошибка, то сразу перескочим в except, если все хорошо,
            # то сделаем return response
            response.raise_for_status()
            # Любые ошибки, которые получим в методе raise_for_status()
            # выведем принтом в except
            # Можно разделить на типы ошибок, но в целом оно нам не нужно,
            # так как цель задачи получить 200 статус
            return response
        except requests.exceptions.RequestException:
            print("Возникла ошибка при выполнении запроса")
            # Возвращать ничего не будем, оно нам и не надо
            return


"""
2. Создайте наследника класса APIRequester под названием SWRequester:

a. Реализуйте метод get_sw_categories(), который должен выполнять запрос
к адресу https://swapi.dev/api/ и возвращать список
доступных категорий, например: films, people, planets и т.д.

b. Реализуйте метод get_sw_info(), который должен принимать в качестве
параметра sw_type одну из категорий из предыдущего пункта.
Метод должен выполнять запрос вида https://swapi.dev/api/<имя категории>/
и возвращать весь полученный ответ в виде строки.
"""


class SWRequester(APIRequester):
    # Инициализируем свойства объекта
    def __init__(self, base_url):
        # Вызываем конструктор базового класса и передаем туда значение
        # в base_url
        super().__init__(base_url)

    # Реализуем метод, который вернет нам Endpoint'ы из https://swapi.dev/api
    def get_sw_categories(self):
        # Выполняем get запрос для https://swapi.dev/api и запишем результат
        # в response
        response = self.get()
        # Если response не None
        if response:
            # Попробуем преобразовать в JSON
            try:
                # Записываем преобразование в data
                """
                Подсказка
                Для того чтобы было удобнее работать со списком категорий,
                преобразуйте полученный ответ от страницы
                https://swapi.dev/api/ в словарь Python
                при помощи метода json() объекта класса Response.
                """
                data = response.json()
                # Возвращаем только ключи,
                # они и будут нашими Endpoint'ами
                return data.keys()
            # Если не получилось преобразовать в JSON,
            # значит получили скорее всего HTML
            except ValueError:
                # Подсветим ошибочку
                print("Ошибка JSON")
        # Вернем пустой массив, если сработал except
        return []

    def get_sw_info(self, sw_type):
        # Получаем ответ по конкретной категории и закрываем слешем,
        # чтоб потом не думать
        response = self.get(sw_type + "/")
        # Если response не None
        if response:
            # Вернем ответ в виде строки
            return response.text
        # В противном случае ничего не вернем
        return


"""
3. Напишите функцию save_sw_data(), которая создаст объект класса SWRequester,
а также директорию под названием data, получит полный список категорий SWAPI,
для каждой категории выполнит запрос к ней
и сохранит файл с именем data/<категория>.txt.
"""


def save_sw_data():
    # Делаем экземпляр класса SWRequester
    sw = SWRequester("https://swapi.dev/api")
    # Переменной path присвоим Path("data")
    path = Path("data")
    # Сделаем папку, если она уже есть, то и ладно
    # Не очень то и хотелось...
    path.mkdir(exist_ok=True)

    # Запишем результат по категориям из метода get_sw_categories()
    categories = sw.get_sw_categories()

    # Переберем все категории по одной, получим по ним информацию,
    # а потом запишем все в отдельные файлы, которые называются как
    # наши категории
    for category in categories:
        print(f"Получение данных по категории: {category}")
        data = sw.get_sw_info(category)
        with open(
            os.path.join("data", f"{category}.txt"),
            mode="w",
            encoding="utf-8"
        ) as f:
            f.write(data)
