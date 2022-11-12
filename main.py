import re
import threading
import time
import sources.confitg as config
import iluxaMod as ilm

import telebot


admin_bot = "5654769061:AAHh0_CFtkL7avdi8KchRTNjX7uFWVTlQqc"
admin_group = 0


pickle = ilm.tools.pickle

# pickle('sources/bots').pick([{"token": admin_bot, "bot_id": "0", "admin": "0"}])
# pickle('sources/bonuses').pick([])
# pickle('sources/stages').pick([])
# pickle('sources/user_machines').pick([])
# pickle('sources/mining_balance').pick([])
# pickle("sources/options").pick([])
# pickle('sources/balance').pick([])

class Our_bots:
    def __init__(self):
        self.lst = pickle('sources/bots').unpick()

    def add(self, token, bot_id, admin_id):
        found = False
        for row in self.lst:
            print(row)
            if row['token'] == token:
                found = True
        if not found:
            self.lst.append({"token": token, "bot_id": bot_id, "admin": admin_id})
            pickle('sources/bots').pick({"token": token, "bot_id": bot_id, "admin": admin_id})

    def find_by_id(self, bot_id):
        for row in self.lst:
            if row['bot_id'] == int(bot_id):
                return row

    def find_by_token(self, bot_id):
        for row in self.lst:
            if row['bot_id'] == int(bot_id):
                return row


class Lang:
    def __init__(self, user_id):
        self.user_id = user_id

    def show(self):
        found = False
        for row in pickle('sources/lang').unpick():
            if row['user_id'] == self.user_id:
                found = True
                return row
        if not found:
            new_dict = {"user_id": self.user_id, "lang": None}
            lst = pickle('sources/lang').unpick()
            lst.append(new_dict)
            pickle('sources/lang').pick(lst)

            return {"user_id": self.user_id, "lang": None}

    def show_lang(self):
        return self.show()['lang']

    def set(self, new):
        this_user = self.show()

        lst = pickle('sources/lang').unpick()
        lst.remove(this_user)

        this_user['lang'] = new
        lst.append(this_user)
        pickle('sources/lang').pick(lst)





tx = [
    # welcome
    {"text_id": "welcome", "ru": """<b>Добро пожаловать</b>

💻 <b>Аппаратов:</b> {machines_num}
⏱️ <b>Общяя скорость майнинга:</b> {total_speed} S/H
💰 <b>Баланс: </b>{bal} Satosh ({dollar_bal}$)""", "en": """<b>Добро пожаловать</b>"""},
    # wallet
    {
        "text_id": "wallet",
        "ru": """<b>Кошелек</b>

💵 Ваш баланс: {bal} долларов

⚠️ Минимум для вывода: {min} долларов""",

        "en": """<b>Wallet</b>"""
    },
    # withrow
    {"text_id": "withrow",
     "ru": """<b>Вывод средств</b>

Впишите сумму, которую собираетесь вывести.

Внимание! Сумма для вывода не должна превышать имеющийся баланс
     """,
     "en": """<b>Вывод средств</b>

Впишите сумму, которую собираетесь вывести.

Внимание! Сумма для вывода не должна превышать имеющийся баланс
     """},
    # withrow_mount
    {"text_id": "withrow_mount", "ru": """<b>Ошибка</b>

Вы пытаетесь вывести меньше, чем есть на счету.

""", "en": """<b>Добро пожаловать</b>"""},
    # withrow_minimum
    {
        "text_id": "withrow_minimum",
        "ru": """Ошмбка

Минимальная сумма для вывода - 100$
""",
        "en": "<b></b>"
    },
    # only_nums
    {"text_id": "only_nums",
     "ru": """<b>Ошибка</b>

На данном этапе разрешено вводить только цифры.

""",
     "en": """<b>Ошибка</b>

На данном этапе разрешено вводить только цифры.

"""},
    # buy_machine_template
    {"text_id": "buy_machine_template",
     "ru": """🏷️ <b>Аппарат:</b> {machine_name}
⏱️ <b>Скорость майнинга:</b> {mining_speed} S/H

💸 <b>Стоимость майнера:</b> {miner_cost}$

""",
     "en": """<b>machine_name:</b> {machine_name}

<b>mining_speed:</b> {mining_speed} S/H
<b>miner_cost:</b> {miner_cost}$
"""},
    # buy_machine_list_end
    {"text_id": "buy_machine_list_end",
     "ru": """
Выберите майнер для покупки

""",
     "en": """
Выберите майнер для покупки

"""},
    # mbuy_no_money
    {"text_id": "mbuy_no_money",
     "ru": """
На счету не хватает денег для совершения покупки

""",
     "en": """
На счету не хватает денег для совершения покупки

"""},
    # add_balance
    {"text_id": "add_balance",
     "ru": """<b>Пополнение баланса</b>

Введите сумму в долларах, которую хотите пополнить.


""",
     "en": """<b>Пополнение баланса</b>

Введите сумму в долларах, которую хотите пополнить.

"""},
    # send_link
    {"text_id": "send_link",
     "ru": """<b>Пополнение баланса</b>

Отправьте {mount}$
На биткоин адрес:
{btc_address}

При совершении транзакции вы получите код или ссылку транзакции.
Отправьте сюда код или ссылку на транзакцию. Иначе - платеж не засчитается

""",
     "en": """

"""},
    # payment_done
    {"text_id": "payment_done",
     "ru": """<b>Баланс пополнен</b>

Ваш баланс был пополнен успешно
""",
     "en": ""},
    # payment_deni
    {"text_id": "payment_deni",
     "ru": """<b>Ошибка</b>

В пополнении баланса отказано.

""",
     "en": ""},
    # not_private_error
    {"text_id": "not_private_error",
     "ru": """
Данная опция существует лишь в клонированном боте.
В оригинальном боте данная кнопка не работает.
""",
     "en": ""},
    # set_btc_address
    {"text_id": "set_btc_address",
     "ru": """<b>Установка биткоин кошелька</b>

Текущий адрес кошелька: {adrs}

Тут вы можете изменить адрес биткоин кошелька, по которому будут приходить заработанные средства.

Введя на данном этапе новое адрес нового кошелька - вы этот адрес сохраните вместо старого.
Нажав на кнопку "Назад"  - изменений в адресе не произойдет


""",
     "en": ""},
    # address_setted
    {"text_id": "address_setted",
     "ru": """<b>Адрес сохранен успешно</b>
""",
     "en": ""},
    # clone_bot
    {"text_id": "clone_bot",
     "ru": """<b>Клонирование бота</b>

Хотите такой же бот, только свой, при чем бесплатно?
1. Перейдите к боту @BotFather и введите команду /newbot
2. Выберите любое название и уникальный юзернейм для вашего нового бота.
3. В знак завершения регистрации - вы получите сообщение с токеном нового бота. Отправьте сюда сообщение с токеном сюда.
4. Ну как бы все;) Ваш бот самостоятельно удаляет сервисные сообщения о присоединившихся или покинувших группу участниках!

""",
     "en": ""},
    # bot_cloned
    {"text_id": "bot_cloned",
     "ru": """<b>Бот клонирован успешно</b>

""",
     "en": ""},
    # panel
    {"text_id": "panel",
     "ru": """<b>Панель управления</b>

Выберите действие

""",
     "en": ""},
    # bonus_taked
    {"text_id": "bonus_taked",
     "ru": """
Вы получили вступительный бонус в размере двух майнинг машин

""",
     "en": ""},
    # my_machines
    {"text_id": "my_machines",
     "ru": """
Перед вами список ваших аппаратов для майнинга.


""",
     "en": ""}

]

bt = [
    # Back
    {
        "btn_id": "back",
        "ru": "🔙 Назад",
        "en": "🔙 Back"
    },
    # Wallet
    {
        "btn_id": "wallet",
        "ru": "💳 Кошелек",
        "en": "💳 Wallet"
    },
    # buy_machine
    {
        "btn_id": "buy_machine",
        "ru": "🛒 Купить Майнер",
        "en": "🛒 "
    },
    # mbuy
    {
        "btn_id": "mbuy",
        "ru": "➡️ Купить Майнер",
        "en": ""
    },
    # my_machines
    {
        "btn_id": "my_machines",
        "ru": "💻 Мои майнеры",
        "en": "💻 "
    },
    # add_balance
    {
        "btn_id": "add_balance",
        "ru": "Пополнить баланс",
        "en": ""
    },
    # clone_bot
    {
        "btn_id": "clone_bot",
        "ru": "Клонировать этот бот",
        "en": ""
    },
    # set_btc_address
    {
        "btn_id": "set_btc_address",
        "ru": "Настроить биткоин адрес",
        "en": ""
    },
    # support
    {
        "btn_id": "support",
        "ru": "⚙️ Тех.Поддержка",
        "en": ""
    },
    # bonus
    {
        "btn_id": "bonus",
        "ru": "🎁 Получить бонус",
        "en": ""
    },
    # bonus
    {
        "btn_id": "withrow",
        "ru": "Вывод средств",
        "en": ""
    }
]

# Our_bots().add("5654769061:AAHh0_CFtkL7 avdi8KchRTNjX7uFWVTlQqc", "None", 0)


class Texts:
    def __init__(self, user_id):
        self.user_id = user_id
        pickle('sources/texts').pick(tx)
        pickle('sources/btns').pick(bt)

    def get_text(self, text_id) -> str:
        # lng = Lang(self.user_id).show_lang()
        #if lng != None:
        for row in pickle('sources/texts').unpick():
            if row['text_id'] == text_id:
                return row["ru"]

    def get_btn(self, btn_id) -> str:
        founded = False
        # lng = Lang(self.user_id).show_lang()
        # if lng != None:
        for row in pickle('sources/btns').unpick():
            # lng = Lang(self.user_id).show_lang()
            # if lng != None:
            if row['btn_id'] == btn_id:
                return row["ru"]


def bonuses(bot_id, user_id, new=None):
    lst = pickle('sources/bonuses').unpick()
    if new != None:
        if {"bot_id": bot_id, "user_id": user_id} not in lst:
            lst.append({"bot_id": bot_id, "user_id": user_id})
            pickle('sources/bonuses').pick(lst)


    return {"bot_id": bot_id, "user_id": user_id} not in lst






def looper(token):
    import iluxaMod as ilm

    # b_token = "5654769061:AAHh0_CFtkL7avdi8KchRTNjX7uFWVTlQqc"

    tgbot = ilm.tgBot(token)
    bot = tgbot.bot
    bot.parse_mode = "HTML"
    import datetime
    kmarkup = tgbot.kmarkup
    btn = tgbot.btn
    send = tgbot.send

    class Balance:
        def __init__(self, user_id, bot_id=None):
            self.user_id = user_id
            self.bot_id = bot_id

        def show(self) -> dict:
            found = False
            lst = pickle('sources/balance').unpick()
            for row in lst:
                if self.bot_id != None:
                    if row['user_id'] == self.user_id and self.bot_id == row['bot_id']:
                        return row
                else:
                    if row['user_id'] == self.user_id:
                        return row
            if not found:
                if self.bot_id == None:
                    lst.append({"bot_id": bot.get_me().id, "user_id": self.user_id, "balance": 0})
                    pickle("sources/balance").pick(lst)
                    return {"bot_id": bot.get_me().id, "user_id": self.user_id, "balance": 0}
                else:
                    lst.append({"bot_id": self.bot_id, "user_id": self.user_id, "balance": 0})
                    pickle("sources/balance").pick(lst)
                    return {"bot_id": self.bot_id, "user_id": self.user_id, "balance": 0}

        def show_balance(self) -> int:
            return self.show()['balance']

        def set(self, new_balance):
            lst = pickle('sources/balance').unpick()
            if self.bot_id == None:

                new_dict = {"bot_id": self.bot_id, "user_id": self.user_id, "balance": self.show_balance()}
                lst.remove(new_dict)
            else:
                new_dict = {"bot_id": bot.get_me().id, "user_id": self.user_id, "balance": self.show_balance()}

            new_dict['balance'] = new_dict['balance'] + int(new_balance)
            lst.append(new_dict)
            pickle('sources/balance').pick(lst)

    class Options:
        def __init__(self, bot_id):
            self.bot_id = bot_id

        def show(self):
            found = False
            lst = pickle('sources/options').unpick()
            for row in lst:
                if row['bot_id'] == self.bot_id:
                    found = True
                    return row
            if not found:
                new_val = {
                    "bot_id": bot.get_me().id,
                    "min_withrow": 100,
                    "btc_wallet": "None",
                    "admin_wallet": "bc1q9vm9u3erczm60q2vwy2kswa9n6prdgllvf545yq7ye6p45mc6susnvp6xp"
                }
                lst.append(new_val)
                pickle("sources/options").pick(lst)
                return new_val

        def show_min_withrow(self):
            return self.show()['min_withrow']

        def show_wallet(self):
            return self.show()['btc_wallet']

        def show_admin_wallet(self):
            return self.show()['admin_wallet']

        def set_min_withrow(self, new):
            found = False
            lst = pickle('sources/options').unpick()
            for row in lst:
                if row['bot_id'] == bot.get_me().id:
                    new_dict = row
                    lst.remove(row)
                    new_dict['min_withrow'] = new
                    lst.append(new_dict)
                    pickle('sources/options').pick(lst)
                    break

            if not found:
                lst = pickle('sources/options').unpick()
                lst.append(
                    {
                        "bot_id": bot.get_me().id,
                        "min_withrow": new,
                        "btc_wallet": "None"
                    }
                )
                pickle('sources/options').pick(lst)

        def set_new_address(self, new_address):
            lst = pickle('sources/options').unpick()
            for row in lst:
                if row['bot_id'] == int(self.bot_id):
                    lst.remove(row)
                    row['admin'] = new_address
                    lst.append(row)

                    pickle('sources/options').pick(lst)

    class User_machine:
        def __init__(self, user_id=None):
            self.user_id = user_id
            self.lst = pickle('sources/user_machines').unpick()

        def add(self, machine_id) -> None:
            self.lst.append({"bot_id": bot.get_me().id, "user_id": self.user_id, "machine_id": machine_id,
                             "start_from": datetime.datetime.now(), "last_update": datetime.datetime.now()})
            pickle('sources/user_machines').pick(self.lst)

        def list_user_machines(self) -> list:
            result = []
            for row in self.lst:
                if row['bot_id'] == bot.get_me().id and row['user_id'] == self.user_id:
                    result.append(row)
            return result

        def total_speed(self) -> int:
            t_speeds = 0
            for row in self.lst:
                if row['user_id'] == self.user_id:
                    t_speeds += Machine(row['machine_id']).show_mining_speed()
            return t_speeds

    class Machine:
        def __init__(self, machine_id=None):
            self.machine_id = machine_id

            m = [
                {
                    "machine_id": "micron3".lower(),
                    "machine_name": "micron3",
                    "mining_speed": 3,
                    "miner_cost": speed_to_usd(3)
                },
                {
                    "machine_id": "Linear_v15".lower(),
                    "machine_name": "Linear_v15",
                    "mining_speed": 15,
                    "miner_cost": speed_to_usd(15)
                },
                {
                    "machine_id": "BigDaddy42".lower(),
                    "machine_name": "BigDaddy42",
                    "mining_speed": 42,
                    "miner_cost": speed_to_usd(42)
                },
                {
                    "machine_id": "FLuX91_w".lower(),
                    "machine_name": "FLuX91_w",
                    "mining_speed": 91,
                    "miner_cost": speed_to_usd(91)
                },
                {
                    "machine_id": "Dragon140s".lower(),
                    "machine_name": "Dragon140s",
                    "mining_speed": 140,
                    "miner_cost": speed_to_usd(140)
                }
            ]

            pickle('sources/machines').pick(m)

        def list_all(self):
            return pickle('sources/machines').unpick()

        def show(self):
            if self.machine_id != None:
                for row in self.list_all():
                    if row['machine_id'].lower() == self.machine_id:
                        return row

        def show_machine_name(self):
            if self.machine_id != None:
                for row in self.list_all():
                    if row['machine_id'].lower() == self.machine_id:
                        return row['machine_name']

        def show_mining_speed(self):
            if self.machine_id != None:
                for row in self.list_all():
                    if row['machine_id'].lower() == self.machine_id:
                        return row['mining_speed']

        def show_miner_cost(self):
            if self.machine_id != None:
                for row in self.list_all():
                    if row['machine_id'].lower() == self.machine_id:
                        return row['miner_cost']

    class Mining_bal:
        def __init__(self, bot_id=None):
            self.bot_id = bot_id
            self.lst = pickle('sources/mining_balance').unpick()

        def one_time_adder(self):

            for mchn in User_machine().lst:
                add_money = Machine(mchn['machine_id']).show_mining_speed()
                add_to_user = mchn['user_id']

                mb = pickle('sources/mining_balance')
                mb_list = mb.unpick()
                found = False
                for mining_bal in mb_list:
                    if add_to_user == mining_bal['user_id']:
                        mb_list.remove(mining_bal)
                        mining_bal['balance'] += add_money
                        mb_list.append(mining_bal)
                        mb.pick(mb_list)
                        found = True

                if not found:
                    mb_list.append({"bot_id": bot.get_me().id, "user_id": add_to_user, "balance": add_money})
                    mb.pick(mb_list)
            config.loopst_num += 1
        def show_balance(self, user_id) -> int:
            found = False
            for i in self.lst:
                if i['user_id'] == user_id and i['bot_id'] == bot.get_me().id:
                    return i['balance']

            if not found:
                self.lst.append({"bot_id": bot.get_me().id, "user_id": user_id, "balance": 0})
                pickle('sources/mining_balance').pick(self.lst)
                return 0

    def stages(bot_id, chat_id, new=None):
        found = False
        lst = pickle('sources/stages').unpick()
        for row in lst:
            if row[0] == bot_id and row[1] == chat_id:
                found = True
                if new != None:
                    lst.remove(row)
                    lst.append({"bot_id": bot_id, "user_id": chat_id, "stage": new})
                    pickle('sources/stages').pick([lst])

                    return new

                return row['stage']

        if not found:
            if new != None:
                lst = pickle('sources/stages').unpick()
                lst.append({"bot_id": bot_id, "user_id": chat_id, "stage": new})
                pickle('sources/stages').pick([lst])

            return "None"


    def satosh_to_usd(satosh) -> float:
        return satosh/4828


    def speed_to_usd(satosh_speed):
        return int(round(satosh_to_usd(satosh_speed * 365 * 20), 0))


    def back(chat_id, callback_data):
        return tgbot.back(callback_data, bname=Texts(chat_id).get_btn('back'))

    bot_id = bot.get_me().id

    def adding_bot(bot_id):
        lst = Our_bots().lst
        for row in lst:
            if row['token'] == token:
                lst.remove(row)
                row['bot_id'] = bot_id
                lst.append(row)
                pickle('sources/bots').pick(lst)

    adding_bot(bot_id)


    def lpd():
        while True:

            Mining_bal().one_time_adder()
            time.sleep(60*60)


    if config.looped == False:
        tt = threading.Thread(target=lpd)
        tt.daemon = True
        tt.start()
        threading.main_thread()
    config.looped = True



    @bot.message_handler(commands=['start'])
    def start_msg(message):
        chat_id = message.chat.id
        stages(bot_id, chat_id, "None")

        k = kmarkup()
        bal = Mining_bal(bot_id).show_balance(chat_id) + (Balance(chat_id).show_balance() * 4828)
        msg = Texts(chat_id).get_text("welcome").format(**{
            "machines_num": str(len(User_machine(chat_id).list_user_machines())),
            "total_speed": str(User_machine(chat_id).total_speed()),
            "bal": str(bal),
            "dollar_bal":  str(bal/4828)[:6]
        })
        if bonuses(bot_id, chat_id) == True:
            k.row(btn(Texts(chat_id).get_btn("bonus"), callback_data=f"bonus"))
        k.row(btn(Texts(chat_id).get_btn("buy_machine"), callback_data=f"buy_machine"))
        k.row(btn(Texts(chat_id).get_btn("my_machines"), callback_data=f"my_machines"))
        k.row(btn(Texts(chat_id).get_btn("wallet"), callback_data=f"wallet"))
        send(chat_id, msg, reply_markup=k)


    @bot.message_handler(commands=['settings'])
    def settings_tab(message):
        chat_id = message.chat.id
        if message.chat.type == "private":
            if Our_bots().find_by_id(bot_id)['admin'] == chat_id:
                k = kmarkup()
                msg = Texts(chat_id).get_text("panel")
                k.row(btn(Texts(chat_id).get_btn("set_btc_address"), callback_data=f"set_btc_address"))
                k.row(back(chat_id, f"home"))
                send(chat_id, msg, reply_markup=k)
                stages(bot_id, chat_id, "None")
            elif bot.get_me().id == 5654769061:
                k = kmarkup()
                msg = Texts(chat_id).get_text("panel")
                k.row(btn(Texts(chat_id).get_btn("set_btc_address"), callback_data=f"set_btc_address"))
                k.row(btn(Texts(chat_id).get_btn("clone_bot"), callback_data=f"clone_bot"))
                k.row(back(chat_id, f"home"))
                send(chat_id, msg, reply_markup=k)
                stages(bot_id, chat_id, "None")


    @bot.message_handler(content_types=['text'])
    def global_text(message):
        chat_id = message.chat.id
        if message.chat.type == "private":
            if stages(bot_id, chat_id) == "withrow":
                try:
                    if int(message.text) > Balance(chat_id).show_balance():
                        k = kmarkup()
                        msg = Texts(chat_id).get_text("withrow_minimum")
                        k.row(back(chat_id, f"withrow"))
                        send(chat_id, msg, reply_markup=k)
                    else:
                        send(chat_id, Texts(chat_id).get_text("withrow_mount"))

                except [TypeError, ValueError]:
                    send(chat_id, Texts(chat_id).get_text("only_nums"))
            elif stages(bot_id, chat_id) == "add_balance":
                try:
                    mount = int(message.text.replace('$', ''))
                    k = kmarkup()
                    msg = Texts(chat_id).get_text("send_link").format(**{
                        "mount": message.text.replace('$', ''),
                        "btc_address": Options(bot_id).show_admin_wallet()
                    })
                    k.row(back(chat_id, "add_balance"))
                    send(chat_id, msg, reply_markup=k)
                    stages(bot_id, chat_id, f"send_link||{str(mount)}")

                except [TypeError, ValueError]:
                    send(chat_id, Texts(chat_id).get_text("only_nums"))
            elif stages(bot_id, chat_id).split('||')[0] == "send_link":
                send(chat_id, Texts(chat_id).get_text("link_sended"))

                stc = int(stages(bot_id, chat_id).split('||')[1])

                k = kmarkup()
                k.row(btn("Allow",
                          callback_data=f"allow_payment||{str(bot_id)}||{str(chat_id)}||{str(stages(bot_id, chat_id).split('||')[1])}"),
                      btn("Deni", callback_data=f"deni_payment||{str(bot_id)}||{str(chat_id)}"))
                amsg = """<b>Оплата</b>
    
Проверте сумму: {sum_to_check} 
ПО коду / ссылке:
{link}

И отправьте: {send}$
По адресу: 
<code>{to_address}</code>
    
                """.format(**{
                    "sum_to_check": str(stc),
                    "link": message.text,
                    "send": str(int(round(stc/10*8, 0))),
                    "to_address": Options(bot_id).show_wallet()
                })

                telebot.TeleBot(admin_bot).send_message(admin_group, amsg, reply_markup=k)
                stages(bot_id, chat_id, "None")
            elif stages(bot_id, chat_id) == "set_btc_address":
                Options(bot_id).set_new_address(message.text)

                send(chat_id, Texts(chat_id).get_text("address_setted"))

                k = kmarkup()
                msg = Texts(chat_id).get_text("panel")
                k.row(btn(Texts(chat_id).get_btn("set_btc_address"), callback_data=f"set_btc_address"))
                if bot.get_me().id == 5654769061:
                    k.row(btn(Texts(chat_id).get_btn("clone_bot"), callback_data=f"clone_bot"))
                k.row(btn(Texts(chat_id).get_btn("support"), url=f"t.me/"))
                k.row(back(chat_id, f"home"))
                send(chat_id, msg, reply_markup=k)
                stages(bot_id, chat_id, "None")
            elif stages(bot_id, chat_id) == "clone_bot":
                r = re.search(r"\d\d\d\d\d\d\d\d\d\d:\S+", message.text)
                if r != None:
                    if {'token': r, 'bot_id': bot_id, 'admin': chat_id} not in Our_bots().lst:
                        Our_bots().add(r, "None", chat_id)
                        th = threading.Thread(target=looper, args=(r,))
                        th.daemon = True
                        th.start()
                        threading.main_thread()
                        send(chat_id, Texts(chat_id).get_text("bot_cloned"))

                        k = kmarkup()
                        msg = Texts(chat_id).get_text("panel")
                        k.row(btn(Texts(chat_id).get_btn("set_btc_address"), callback_data=f"set_btc_address"))
                        if bot.get_me().id == 5654769061:
                            k.row(btn(Texts(chat_id).get_btn("clone_bot"), callback_data=f"clone_bot"))
                        k.row(back(chat_id, f"home"))
                        send(chat_id, msg, reply_markup=k)
                        stages(bot_id, chat_id, "None")




    @bot.callback_query_handler(func=lambda m: True)
    def g_calls(call):
        chat_id = call.message.chat.id

        def dm():
            try:
                bot.delete_message(chat_id, call.message.message_id)
            except:
                pass

        cd = call.data.split("||")
        if call.message.chat.type == "private":
            if call.data == "home":
                start_msg(call.message)
                dm()
            elif call.data == f"wallet":
                 k = kmarkup()
                 msg = Texts(chat_id).get_text("wallet").format(**{
                     "bal": str(Balance(chat_id).show_balance()),
                     "min": str(Options(bot_id).show_min_withrow())
                 })
                 k.row(btn(Texts(chat_id).get_btn("withrow"), callback_data=f"withrow"))
                 k.row(btn(Texts(chat_id).get_btn("add_balance"), callback_data=f"add_balance"))
                 k.row(back(chat_id, f"home"))
                 send(chat_id, msg, reply_markup=k)
                 stages(bot_id, chat_id, "None")
                 dm()
            elif call.data == "withrow":
                msg = Texts(chat_id).get_text("withrow_minimum")
                bot.answer_callback_query(call.id, msg, show_alert=True)
            elif call.data == "buy_machine":
                for row in Machine().list_all():
                    k = kmarkup()
                    msg = Texts(chat_id).get_text("buy_machine_template").format(**{
                        "machine_name": row['machine_name'],
                        "mining_speed": str(row['mining_speed']),
                        "miner_cost": str(row['miner_cost'])
                    })
                    k.row(btn(Texts(chat_id).get_btn("mbuy"), callback_data=f"mbuy||{str(row['machine_id'])}"))
                    send(chat_id, msg, reply_markup=k)

                gk = kmarkup()
                gmsg = Texts(chat_id).get_text("buy_machine_list_end")
                gk.row(back(chat_id, f"home"))
                send(chat_id, gmsg, reply_markup=gk)
            elif call.data == "add_balance":
                k = kmarkup()
                msg = Texts(chat_id).get_text("add_balance")
                k.row(back(chat_id, f"home"))
                send(chat_id, msg, reply_markup=k)
                stages(bot_id, chat_id, "None")
            elif call.data == "set_btc_address":
                if bot.get_me().id == 5654769061:
                    bot.answer_callback_query(call.id, Texts(chat_id).get_text("not_private_error"), show_alert=True)
                else:
                    infos = Options(bot_id).show_wallet()

                    k = kmarkup()
                    msg = Texts(chat_id).get_text("set_btc_address").format(**{"adrs": infos})
                    k.row(back(chat_id, "panel"))
                    send(chat_id, msg, reply_markup=k)
                    stages(bot_id, chat_id, "set_btc_address")
            elif call.data == "panel":
                k = kmarkup()
                msg = Texts(chat_id).get_text("panel")
                k.row(btn(Texts(chat_id).get_btn("set_btc_address"), callback_data=f"set_btc_address"))
                if bot.get_me().id == 5654769061:
                    k.row(btn(Texts(chat_id).get_btn("clone_bot"), callback_data=f"clone_bot"))
                k.row(btn(Texts(chat_id).get_btn("support"), url=f"t.me/"))
                k.row(back(chat_id, f"home"))
                send(chat_id, msg, reply_markup=k)
                stages(bot_id, chat_id, "None")
                dm()
            elif call.data == "clone_bot":
                k = kmarkup()
                msg = Texts(chat_id).get_text("clone_bot")
                k.row(back(chat_id, "panel"))
                send(chat_id, msg, reply_markup=k)
                stages(bot_id, chat_id, "clone_bot")
            elif call.data == "bonus":
                if bonuses(bot_id, chat_id) == True:
                    bonuses(bot_id, chat_id, True)

                    User_machine(user_id=chat_id).add('micron3')
                    User_machine(user_id=chat_id).add('micron3')


                    bot.answer_callback_query(call.id, Texts(chat_id).get_text("bonus_taked"), show_alert=True)
                start_msg(call.message)
                dm()
            elif call.data == "my_machines":
                for row in User_machine(chat_id).list_user_machines():
                    machine_id = row['machine_id']
                    machine = Machine(machine_id)

                    send(chat_id, "<b>Название майнера:</b> {name}\n<b>Скорость майнера:</b> {speed} S/H".format(**{
                        "name": machine.show_machine_name(),
                        "speed": machine.show_mining_speed()
                    }))

                k = kmarkup()
                msg = Texts(chat_id).get_text("my_machines")
                k.row(back(chat_id, "home"))
                send(chat_id, msg, reply_markup=k)
                dm()

            elif cd[0] == "set_lang":
                new_lang = cd[1]
                Lang(chat_id).set(new_lang)

                start_msg(call.message)
                dm()
            elif cd[0] == "mbuy":
                machine_id = cd[1]
                machine_cost = Machine(machine_id).show_miner_cost()

                if Balance(chat_id).show_balance() >= machine_cost:
                    Balance(chat_id).set(Balance(chat_id).show_balance() - machine_cost)

                    User_machine(user_id=chat_id).add(machine_id)

                    msg = Texts(chat_id).get_text("mbuy")
                    bot.answer_callback_query(call.id, msg, show_alert=True)
                else:
                    msg = Texts(chat_id).get_text("mbuy_no_money")
                    bot.answer_callback_query(call.id, msg, show_alert=True)
            elif cd[0] == "allow_payment":
                _, new_bot_id, user_id, mount = cd

                Balance(user_id=int(user_id), bot_id=int(new_bot_id)).set(Balance(user_id=int(user_id), bot_id=int(new_bot_id)).show_balance() + int(mount))

                telebot.TeleBot(Our_bots().find_by_id(int(new_bot_id))['token']).send_message(int(user_id), Texts(chat_id).get_text("payment_done"))

                send(chat_id, call.message.text + f"\n\nConfirmed by @{call.from_user.id}")
                dm()
            elif cd[0] == "deni_payment":
                _, new_bot_id, user_id = cd

                telebot.TeleBot(Our_bots().find_by_id(int(new_bot_id))['token']).send_message(int(user_id), Texts(chat_id).get_text("payment_deni"))



    while True:
        try:
            bot.polling()
        except Exception as ex:
            print(ex)



for inf in pickle('sources/bots').unpick():
    t = inf['token']
    th = threading.Thread(target=looper, args=(t, ))
    th.daemon = True
    th.start()
    threading.main_thread()

while True:
    try:
        time.sleep(60)
    except KeyboardInterrupt as ki:
        break
exit(0)