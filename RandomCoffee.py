from telebot import types
import numpy as np
import json
from itertools import combinations


class RandomCoffee:
    def __init__(self, load_files=False):
        self.user_preferences = {}
        self.type_of_user = {}
        self.id_to_fac = {}
        self.fac_to_ids = {"Математика": [], "Современное Программирование": [], "Науки о Данных": []}
        self.facs = ["Математика", "Современное Программирование", "Науки о Данных"]
        self.valid_choises = ['Однокурсники', 'Кураторы']
        self.total_choise_variants = ['Однокурсники', 'Кураторы', 'Готово']
        self.preferences_cast = {'odnokur': 'Однокурсники', 'kurator': 'Кураторы', 'choose_done': 'Готово'}
        self.ref_cast = {'Однокурсники': 'odnokur', 'Кураторы': 'kurator', 'Готово': 'choose_done'}
        if load_files:
            with open('files/id_to_fac.json', 'r') as f:
                self.id_to_fac = json.load(f)
            with open('files/fac_to_ids.json', 'r') as f:
                self.fac_to_ids = json.load(f)

    def add_user(self, user_id):
        self.user_preferences[user_id] = []

    def remove_user(self, user_id):
        try:
            del self.user_preferences[user_id]
        except:
            pass

    def set_status_pervak(self, user_id):
        self.type_of_user[user_id] = 'child'

    def add_preference(self, user_id, pref):
        upd_pref = self.preferences_cast[pref]
        if upd_pref == 'Готово':
            return
        if user_id not in self.user_preferences.keys():
            self.user_preferences[user_id] = []
        if upd_pref not in self.user_preferences[user_id]:
            self.user_preferences[user_id].append(upd_pref)
        else:
            self.user_preferences[user_id].remove(upd_pref)

    def get_preferences(self, user_id):
        return self.user_preferences[user_id]

    def update_preferences(self, user_id, new_pref):
        self.add_preference(user_id, self.preferences_cast[new_pref])

    def add_fac_for_user(self, user_id, fac):
        self.id_to_fac[user_id] = fac
        self.fac_to_ids[fac].append(user_id)
        with open('files/id_to_fac.json', 'w') as f:
            json.dump(self.id_to_fac, f)
        with open('files/fac_to_ids.json', 'w') as f:
            json.dump(self.fac_to_ids, f)

    def get_beautiful_choises_buttons_for_user(self, user_id):
        user_preferences = self.user_preferences[user_id]
        beautiful_preferences = []
        for var in self.total_choise_variants:
            if var in user_preferences:
                beautiful_preferences.append(types.InlineKeyboardButton('✅' + var, callback_data=self.ref_cast[var]))
            else:
                beautiful_preferences.append(types.InlineKeyboardButton(var, callback_data=self.ref_cast[var]))
        return beautiful_preferences

    def get_preferences_markup_for_user(self, user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = self.get_beautiful_choises_buttons_for_user(user_id)
        for button in buttons:
            markup.add(button)
        return markup

    def get_pairs(self):
        pairs = []
        for fac in self.facs:
            cur_users = self.fac_to_ids[fac]
            # Only one choise

            pair_founded = []
            for choise in ['Однокурсники']:
                this_type_of = []
                for k, v in self.user_preferences.items():
                    if k in cur_users and set(v) == set(choise):
                        this_type_of.append(k)
                to_select = this_type_of
                while len(to_select) > 1:
                    pair = np.random.choice(to_select, 2, replace=False)
                    for p in pair:
                        to_select.remove(p)
                        pair_founded.append(p)
                    pairs.append(pair)

            # Two choises

            for pair_choise in list(combinations(self.valid_choises, 2)):
                this_type_of = []
                for k, v in self.user_preferences.items():
                    if k in cur_users and set(v) == set(pair_choise):
                        this_type_of.append(k)
                to_select = this_type_of
                while len(to_select) > 1:
                    pair = np.random.choice(to_select, 2, replace=False)
                    for p in pair:
                        to_select.remove(p)
                        pair_founded.append(p)
                    pairs.append(pair)

            # Kto ostalsya

            left_users = set(cur_users).difference(set(pair_founded))
            if len(left_users) == 0:
                return pairs
            else:
                # В текущей реализации не достаться пары (и мы обратим на это внимание) могло только перваку, который
                # попросил первака в пару
                # Или же первак попросил и куратора, но их не хватило.
                # Решено тупа сделать рандомные пары из того что осталось
                left_users_upd = list(left_users)
                while len(left_users_upd) > 1:
                    pair = np.random.choice(left_users_upd, 2, replace=False)
                    for p in pair:
                        left_users_upd.remove(p)
                    pairs.append(pair)
                if len(left_users_upd) == 1 and len(pair_founded) > 0:
                    pairs.append([left_users_upd[0], np.random.choice(pair_founded, 1, replace=False)[0]])
        return pairs
