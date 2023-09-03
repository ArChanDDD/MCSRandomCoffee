from telebot import types
import numpy as np
import json


class RandomCoffee:
    """Класс для всех операций с системой Random Coffee"""

    def __init__(self, load_files: bool = False):
        """
        :param load_files: True для повторной иницализации, либо иного случая когда файлы с данными о пользователях уже есть
        """
        self.MAX_PERVAK_PER_KURATOR = 3
        self.user_preferences = {}
        self.type_of_user = {}
        self.id_to_fac = {}
        self.total_id_to_fac = self.id_to_fac.copy()
        self.facs = ["Математика", "Современное Программирование", "Науки о Данных"]
        self.valid_choises = ['Однокурсники', 'Кураторы', 'Другое направление']
        self.total_choise_variants = self.valid_choises + ['Готово']
        self.ref_cast = {'Однокурсники': 'odnokur', 'Кураторы': 'kurator', 'Готово': 'choose_done',
                         'Другое направление': 'other_fac'}
        self.preferences_cast = {v: k for k, v in self.ref_cast.items()}
        if load_files:
            with open('files/total_id_to_fac.json', 'r') as f:
                self.total_id_to_fac = {int(k): v for k, v in json.load(f).items()}
            with open('files/type_of_user.json', 'r') as f:
                self.type_of_user = {int(k): v for k, v in json.load(f).items()}

    def add_user(self, user_id: int):
        """Метод добавления нового пользователя
        :param user_id: message.chat.id для нужного чата"""
        self.user_preferences[user_id] = []

    def remove_user(self, user_id: int):
        """
        Удаление информации о пользователе
        :param user_id: message.chat.id для нужного чата
        :return:
        """
        try:
            del self.user_preferences[user_id]
        except:
            pass

    def set_status_pervak(self, user_id: int):
        """
        Установление статуса первокурсника для `user_id`
        :param user_id: message.chat.id для нужного чата
        :return:
        """
        self.type_of_user[user_id] = 'child'
        with open('files/type_of_user.json', 'w') as f:
            json.dump(self.type_of_user, f)

    def set_status_kurator(self, user_id: int):
        """
        Установление статуса куратора для `user_id`, а также всех политик для куратора
        :param user_id: message.chat.id для нужного чата
        :return:
        """
        self.type_of_user[user_id] = 'kurator'
        self.user_preferences[user_id] = ['Однокурсник']
        with open('files/type_of_user.json', 'w') as f:
            json.dump(self.type_of_user, f)

    def add_preference(self, user_id: int, pref: str):
        """
        Добавление предпочтения для пользователя
        :param user_id: message.chat.id для нужного чата
        :param pref: Один из `odnokur`, `kurator`, `other_fac`, `choose_done`
        :return:
        """
        upd_pref = self.preferences_cast[pref]
        if upd_pref == 'Готово':
            return
        if user_id not in self.user_preferences.keys():
            self.user_preferences[user_id] = []
        if upd_pref not in self.user_preferences[user_id]:
            self.user_preferences[user_id].append(upd_pref)
        else:
            self.user_preferences[user_id].remove(upd_pref)

    def get_preferences(self, user_id: int):
        """
        Получить список предпочтений для `user_id`
        :param user_id: message.chat.id для нужного чата
        :return:
        """
        return self.user_preferences[user_id]

    def update_preferences(self, user_id: int, new_pref: str):
        """
        Добавить предпочтение `new_pref` для пользователя `user_id`
        :param user_id: message.chat.id для нужного чата
        :param new_pref: Одно из предпочтений
        :return:
        """
        self.add_preference(user_id, self.preferences_cast[new_pref])

    def add_fac_for_user(self, user_id, fac=None):
        if fac is None:
            self.id_to_fac[user_id] = self.total_id_to_fac[user_id]
        else:
            self.id_to_fac[user_id] = fac
            self.total_id_to_fac[user_id] = fac
            with open('files/total_id_to_fac.json', 'w') as f:
                json.dump(self.id_to_fac, f)

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

    def is_user_enable(self, user_id: int):
        """
        Проверка на наличия пользователя `user_id` в базе
        :param user_id: message.chat.id для нужного чата
        :return:
        """
        return user_id in list(self.type_of_user.keys())

    def get_pairs(self):
        fac_to_ids = {'Математика': [], 'Современное Программирование': [], 'Науки о Данных': []}
        for user_id, fac in self.id_to_fac.items():
            fac_to_ids[fac].append(user_id)

        pairs = []
        next_time = {x: [] for x in self.facs}
        total_students_not_flatten = [fac_to_ids[fac] for fac in self.facs]
        total_students_to_pairing = [item for sublist in total_students_not_flatten for item in sublist if
                                     self.type_of_user[item] == 'child']
        fac_to_kurators = {}
        for fac in self.facs:
            fac_to_kurators[fac] = [user_id for user_id in fac_to_ids[fac]
                                    if self.type_of_user[user_id] == 'kurator']

        # child 2 child
        for fac in self.facs:
            pervaki_for_pair = [user_id
                                for user_id in fac_to_ids[fac]
                                if self.user_preferences[user_id] == ['Однокурсники']
                                and self.type_of_user[user_id] == 'child']
            while len(pervaki_for_pair) > 1:
                pair = np.random.choice(pervaki_for_pair, 2, replace=False)
                for x in pair:
                    pervaki_for_pair.remove(x)
                    total_students_to_pairing.remove(x)
                pairs.append(pair)
            if len(pervaki_for_pair) == 1:
                next_time[fac].append(pervaki_for_pair[0])

        # child 2 kurator
        kurator_pairs_count = {}
        for fac in self.facs:
            kurator_pairs_count[fac] = {user_id: 0 for user_id in fac_to_kurators[fac]}
        for fac in self.facs:
            pervaki_for_pair = [user_id
                                for user_id in fac_to_ids[fac]
                                if self.user_preferences[user_id] == ['Кураторы']
                                and self.type_of_user[user_id] == 'child']
            kuratori_for_pair = [user_id
                                 for user_id in fac_to_ids[fac]
                                 if self.type_of_user[user_id] == 'kurator']
            np.random.shuffle(pervaki_for_pair)
            np.random.shuffle(kuratori_for_pair)
            kur_len = len(kuratori_for_pair)
            if kur_len == 0:
                break
            start_id_no_pair = len(pervaki_for_pair)
            for i, pervak_id in enumerate(pervaki_for_pair):
                kur_id = kuratori_for_pair[i % kur_len]
                if kurator_pairs_count[fac][kur_id] == self.MAX_PERVAK_PER_KURATOR:
                    start_id_no_pair = i
                    break
                pairs.append([pervak_id, kur_id])
                total_students_to_pairing.remove(pervak_id)
                kurator_pairs_count[fac][kur_id] += 1
            for j in range(start_id_no_pair, len(pervaki_for_pair)):
                next_time[fac].append(pervaki_for_pair[j])

        # child 2 (child+kurator) OR (child+other) OR (child+kurator+other) -> we think pair will be "child"
        for fac in self.facs:
            pervaki_for_pair = [user_id
                                for user_id in fac_to_ids[fac]
                                if (set(self.user_preferences[user_id]) == {'Однокурсники', 'Кураторы'}
                                    or set(self.user_preferences[user_id]) == {'Однокурсники', 'Другое направление'}
                                    or set(self.user_preferences[user_id]) == {'Однокурсники', 'Кураторы',
                                                                               'Другое направление'})
                                and self.type_of_user[user_id] == 'child']
            while len(pervaki_for_pair) > 1:
                pair = np.random.choice(pervaki_for_pair, 2, replace=False)
                for x in pair:
                    pervaki_for_pair.remove(x)
                    total_students_to_pairing.remove(x)
                pairs.append(pair)
            if len(pervaki_for_pair) == 1:
                next_time[fac].append(pervaki_for_pair[0])

        # child 2 other OR (kurator+other) -> we think pair will be "other"
        pervaki_for_pair = []
        for fac in self.facs:
            pervaki_for_pair.append([user_id
                                     for user_id in fac_to_ids[fac]
                                     if 'Другое направление' in self.user_preferences[user_id]
                                     and user_id in total_students_to_pairing
                                     and self.type_of_user[user_id] == 'child'])
        pervaki_for_pair = [item for sublist in pervaki_for_pair for item in sublist]
        np.random.shuffle(pervaki_for_pair)
        pervaki_for_pair = list(pervaki_for_pair)

        while len(pervaki_for_pair) > 1:
            pair = np.random.choice(pervaki_for_pair, 2, replace=False)
            for x in pair:
                pervaki_for_pair.remove(x)
                total_students_to_pairing.remove(x)
            pairs.append(pair)
        if len(pervaki_for_pair) == 1:
            next_time[self.id_to_fac[pervaki_for_pair[0]]].append(pervaki_for_pair[0])

        # kto ostalsya
        to_other_napr_part_2 = []
        for fac in self.facs:
            while len(next_time[fac]) != 0:
                cur_user = next_time[fac][0]
                pair_founded = False
                if 'Кураторы' in self.user_preferences[cur_user]:
                    cur_kurator = None
                    for kurator_id in fac_to_kurators[fac]:
                        if kurator_pairs_count[fac][kurator_id] < self.MAX_PERVAK_PER_KURATOR:
                            cur_kurator = kurator_id
                            break
                    if cur_kurator is not None:
                        pairs.append([cur_user, cur_kurator])
                        kurator_pairs_count[fac][cur_kurator] += 1
                        next_time[fac].remove(cur_user)
                        pair_founded = True
                if 'Однокурсники' in self.user_preferences[cur_user] and not pair_founded:
                    cur_user_pair = None
                    for us in next_time[fac][1:]:
                        if 'Однокурсники' in self.user_preferences[us]:
                            cur_user_pair = us
                            break
                    if cur_user_pair is not None:
                        pairs.append([cur_user, cur_user_pair])
                        next_time[fac].remove(cur_user)
                        next_time[fac].remove(cur_user_pair)
                        pair_founded = True
                if 'Другое направление' in self.user_preferences[cur_user] and not pair_founded:
                    to_other_napr_part_2.append(cur_user)
                    next_time[fac].remove(cur_user)
                    pair_founded = True
                if not pair_founded:
                    next_time[fac].remove(cur_user)

        # different napravleniya part 2
        maybe_pairs = to_other_napr_part_2

        while len(maybe_pairs) > 1:
            pair = np.random.choice(maybe_pairs, 2, replace=False)
            for x in pair:
                maybe_pairs.remove(x)
                total_students_to_pairing.remove(x)
            pairs.append(pair)

        total_students_to_pairing_with_kurators = set(
            [item for sublist in total_students_not_flatten for item in sublist])
        students_with_pairs = set([item for sublist in pairs for item in sublist])
        not_found_pairs = list(total_students_to_pairing_with_kurators.difference(students_with_pairs))

        return [list(x) for x in pairs], not_found_pairs
