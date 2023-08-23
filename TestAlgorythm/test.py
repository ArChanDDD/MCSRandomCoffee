import json
from RandomCoffee import RandomCoffee

RC = RandomCoffee()
with open('preferences.json', 'r') as f:
    RC.user_preferences = json.load(f)


def test1():
    # Проверка отличимости ребенка от куратора
    RC.user_preferences = {
        1: ['odnokur'],
        2: ['odnokur', 'kurator'],
        3: ['odnokur'],
        4: ['odnokur', 'kurator'],
        5: ['odnokur', 'kurator'],
        6: ['kurator'],
        7: ['kurator'],
        8: ['kurator'],
        9: ['kurator'],
        10: ['kurator']
    }
    RC.type_of_user = {
        1: 'child',
        2: 'child',
        3: 'child',
        4: 'child',
        5: 'child',
        6: 'kurator',
        7: 'kurator',
        8: 'kurator',
        9: 'kurator',
        10: 'kurator'
    }
    RC.id_to_fac = {
        1: "Математика",
        2: "Математика",
        3: "Математика",
        4: "Математика",
        5: "Математика",
        6: "Математика",
        7: "Математика",
        8: "Математика",
        9: "Математика",
        10: "Математика"
    }
    RC.fac_to_ids = {"Математика": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "Современное Программирование": [],
                     "Науки о Данных": []}

    print(RC.get_pairs())


test1()
