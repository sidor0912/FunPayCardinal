"""
CBT - CallBack Texts. В данном модуле расписаны все CallBack'и для Telegram клавиатуры (+ User-state'ы)
"""

# Основное меню
MAIN = "1"
"""
Открыть основное меню настроек.
"""

CATEGORY = "2"
"""
Открыть категорию настроек.
Использование: CBT.CATEGORY:category_name

category_name: str - название категории настроек.
    main - глобальные переключатели.
    telegram - переключатели Telegram-уведомлений.
    autoResponse - настройки автоответчика.
    autoDelivery - настройки авто-выдачи.
    blockList - переключатели ЧС.
"""

SWITCH = "3"
"""
Callback для переключения определенного параметра из основного конфига.
Использование: CBT.SWITCH:section_name:option_name

section_name: название секции.
option_name: название опции.
"""


# Настройки автоответчика
ADD_CMD = "4"
"""
Callback для активации режима ввода текста новой команды / сета команд.


User-state: ожидается сообщение с текстом новой команды / сета команд.
"""


CMD_LIST = "5"
"""
Callback для открытия списка команд.
Использование: CBT.CMD_LIST:offset

offset: int - смещение списка команд.
"""


EDIT_CMD = "6"
"""
Callback для открытия меню редактирования команды.
Использование: CBT.EDIT_CMD:command_index:offset

command_index: int - числовой индекс команды.
offset: int - смещение списка команд.
"""


EDIT_CMD_RESPONSE_TEXT = "7"
"""
Callback для активации режима ввода нового текста ответа на команду.
Использование: CBT.EDIT_CMD_RESPONSE_TEXT:command_index:offset

command_index: int - числовой индекс команды.
offset: int - смещение списка команд.


User-state: ожидается сообщение с новым текстом ответа на команду.
data:
command_index: int - числовой индекс команды.
offset: int - смещение списка команд.
"""


EDIT_CMD_NOTIFICATION_TEXT = "8"
"""
Callback для активации режима ввода нового текста уведомления об использовании команде.
Использование: CBT.EDIT_CMD_NOTIFICATION_TEXT:command_index:offset

command_index: int - числовой индекс команды.
offset: int - смещение списка команд.


User-state: ожидается сообщение с новым текстом уведомления об использовании команде.
data:
command_index: int - числовой индекс команды.
offset: int - смещение списка команд.
"""


SWITCH_CMD_NOTIFICATION = "9"
"""
Callback для вкл/выкл Telegram уведомления об использовании команды.
Использование: CBT.SWITCH_CMD_NOTIFICATION:command_index:offset

command_index: int - числовой индекс команды.
offset: int - смещение списка команд.
"""


DEL_CMD = "10"
"""
Callback для удаления команды из конфига автоответчика.
Использование: CBT.DEL_CMD:command_index:offset

command_index: int - числовой индекс команды.
offset: int - смещение списка команд.
"""


# FUNPAY LOTS LIST
FP_LOTS_LIST = "11"
"""
Callback для открытия списка лотов, спарсенных напрямую с Funpay.
Использование: CBT.FP_LOTS_LIST:offset

offset: int - смещение списка FunPay лотов.
"""

ADD_AD_TO_LOT = "12"
"""
Callback для подключения к лоту автовыдачи.
Использование: CBT.ADD_AD_TO_LOT:lot_index:offset

lot_index: int - числовой индекс FunPay лота.
offset: int - смещение списка FunPay лотов.
"""

ADD_AD_TO_LOT_MANUALLY = "13"
"""
Callback для активации режима ввода названия лота для подключения к нему автовыдачи.
Использование: CBT.ADD_AD_TO_LOT_MANUALLY:offset

offset: int - смещение списка FunPay лотов.


User-state: ожидается сообщение с названием лота для подключения к нему автовыдачи.
data:
offset: int - смещение списка FunPay лотов.
"""


# Настройки лотов с автовыдачей
AD_LOTS_LIST = "14"
"""
Callback для открытия списка лотов с автовыдачей.
Использование: CBT.AD_LOTS_LIST:offset

offset: int - смещение списка лотов с автовыдачей.
"""


EDIT_AD_LOT = "15"
"""
Callback для открытия меню редактирования автовыдачи лота.
Использование: CBT.EDIT_AD_LOT:lot_index:offset

lot_index: int - числовой индекс лота с автовыдачей.
offset: int - смещение списка лотов с автовыдачей.
"""


EDIT_LOT_DELIVERY_TEXT = "16"
"""
Callback для активации режима ввода нового текста выдачи товара.
Использование: CBT.EDIT_LOT_DELIVERY_TEXT:lot_index:offset

lot_index: int - числовой индекс лота с автовыдачей.
offset: int - смещение списка лотов с автовыдачей.

User-state: ожидается сообщение с новым текстом выдачи товара.
data:
lot_index: int - числовой индекс лота с автовыдачей.
offset: int - смещение списка лотов с автовыдачей.
"""


BIND_PRODUCTS_FILE = "17"
"""
Callback для активации режима ввода названия файла с товарами для привязки к лоту с автовыдачей.
Использование: CBT.BIND_PRODUCTS_FILE:lot_index:offset

lot_index: int - числовой индекс лота с автовыдачей.
offset: int - смещение списка лотов с автовыдачей.

User-state: ожидается сообщение с названием файла с товарами для привязки к лоту с автовыдачей.
data:
lot_index: int - числовой индекс лота с автовыдачей.
offset: int - смещение списка лотов с автовыдачей.
"""


DEL_AD_LOT = "18"
"""
Callback для удаления лота из конфига автовыдачи.
Использование: CBT.DEL_AD_LOT:lot_index:offset

lot_index: int - числовой индекс лота с автовыдачей.
offset: int - смещение списка лотов с автовыдачей.
"""


# Настройки файлов с товарами
PRODUCTS_FILES_LIST = "19"
"""
Callback для открытия списка файлов с товарами.
Использование: CBT.PRODUCTS_FILES_LIST:offset

offset:int - смещение списка файлов с товарами.
"""


EDIT_PRODUCTS_FILE = "20"
"""
Callback для открытия меню редактирования файла с товарами.
Использование: CBT.EDIT_PRODUCTS_FILE:file_index:offset

file_index: int - числовой индекс файла с товарами.
offset: int - смещение списка файлов с товарами.
"""


UPLOAD_PRODUCTS_FILE = "21"
"""
Callback для активации режима выгрузки файла с товарами.


User-state: ожидается сообщение с файлом с товарами.
"""


CREATE_PRODUCTS_FILE = "22"
"""
Callback для активации режима ввода названия нового товарного файла.


User-state: ожидается сообщение с названием нового товарного файла.
"""

ADD_PRODUCTS_TO_FILE = "23"
"""
Callback для активации режима ввода товаров для последующего добавления их в товарный файл.
Использование: CBT.ADD_PRODUCTS_TO_FILE:file_index:index:offset:previous_page

file_index: int - числовой индекс файла с товарами.
element_index: int - числовой индекс файла с товарами / лота с автовыдачей.
offset: int - смещение списка файлов с товарами / списка лотов с автовыдачей.
previous_page: int - предыдущая страница.
    0 - страница редактирования файла с товарами.
    1 - страница редактирования автовыдачи лота.


User-state: ожидается сообщение товарами для последующего добавления их в товарный файл.
data:
file_index: int - числовой индекс файла с товарами.
element_index: int - числовой индекс файла с товарами / лота с автовыдачей.
offset: int - смещение списка файлов с товарами.
previous_page: int - предыдущая страница.
    0 - страница редактирования файла с товарами.
    1 - страница редактирования автовыдачи лота.
"""


# Конфиги
DOWNLOAD_CFG = "24"
"""
Callback для отправки файла конфига
Использование: CBT.DOWNLOAD_CFG:config

config: str - тип конфига.
    main - основной конфиг configs/_main.cfg.
    autoResponse - конфиг автоответчика configs/auto_response.cfg.
    autoDelivery - конфиг автовыдачи configs/auto_delivery.cfg.
"""


# Шаблоны ответов
TMPLT_LIST = "25"
"""
Callback для открытия списка шаблонов ответа.
Использование: CBT.TMPLT_LIST:offset

offset: int - смещение списка шаблонов ответа.
"""


TMPLT_LIST_ANS_MODE = "26"
"""
Callback для открытия списка шаблонов ответа в режиме ответа.
Использование: CBT.TMPLT_LIST_ANS_MODE:offset:node_id:username:prev_page:extra

offset: int - смещение списка шаблонов ответа.
node_id: int - ID переписки, в которую нужно отправить шаблон.
username: str - имя пользователя, с которым ведется переписка.
prev_page: ID предыдущей клавиатуры.
    0 - клавиатура нового сообщения.
    1 - клавиатура нового сообщения (2).
extra: str / int - доп. данные для клавиатуры (через ":").
"""


EDIT_TMPLT = "27"
"""
Callback для открытия меню изменения шаблона ответа.
Использование: CBT.EDIT_TMPLT:template_index:offset

template_index: int - числовой индекс шаблона ответа.
offset: int - смещение списка шаблонов ответа.
"""


DEL_TMPLT = "28"
"""
Callback для удаления шаблона ответа.
Использование: CBT.DEL_TMPLT:template_index:offset

template_index: int - числовой индекс шаблона ответа.
offset: int - смещение списка шаблонов ответа.
"""


ADD_TMPLT = "29"
"""
Callback для активации режима ввода текста нового шаблона ответа.
Использование: CBT.ADD_TMPLT:offset

offset: int - смещение списка шаблонов ответа.


User-state: ожидается сообщение с текстом нового шаблона ответа.
data:
offset: int - смещение списка шаблонов ответа.
"""

SEND_TMPLT = "30"
"""
Callback для отправки шаблона в ЛС FunPay.
Использование: CBT.SEND_TMPLT:index:node_id:username:prev_page:extra

index: int - числовой индекс шаблона.
node_id: int - ID переписки, в которую нужно отправить шаблон.
username: str - имя пользователя, с которым ведется переписка.
prev_page: ID предыдущей клавиатуры.
    0 - клавиатура нового сообщения.
    1 - клавиатура нового сообщения (2).
extra: str / int - доп. данные для клавиатуры (через ":").
"""


# Прочее
SWITCH_TG_NOTIFICATIONS = "31"
"""
Callback для вкл. / выкл. определенного типа уведомлений в определенном Telegram чате.
Использование: switch_tg_notification:chat_id:notification_type

chat_id: int - ID Telegram чата.
notification_type: str - тип уведомлений (tg_bot.utils.NotificationTypes).
"""


REQUEST_REFUND = "32"
"""
Callback для обновления меню с действиями по заказу (уточнение по возврату средств)
Использование: CBT.REQUEST_REFUND:order_id

order_id: str - ID заказа (без #).
"""

REFUND_CONFIRMED = "33"
"""
Callback для подтверждения возврата средств.
Использование: CBT.REFUND_CONFIRMED:order_id:node_id:nickname

order_id: str - ID заказа (без #).
node_id: int - ID переписки с покупателем.
username: str - никнейм покупателя.
"""

REFUND_CANCELLED = "34"
"""
Callback для отмены возврата средств.
Использование: CBT.REFUND_CANCELLED:order_id:node_id:nickname

order_id: str - ID заказа (без #).
node_id: int - ID переписки с покупателем.
username: str - никнейм покупателя.
"""


BAN = "35"
"""
Callback для активации режима ввода никнейма FunPay пользователя для добавления его в ЧС.


User-state: ожидается сообщение с никнеймом FunPay пользователя для добавления его в ЧС.
"""

UNBAN = "36"
"""
Callback для активации режима ввода никнейма FunPay пользователя для удаления его из ЧС.


User-state: ожидается сообщение с никнеймом FunPay пользователя для удаления его из ЧС.
"""


SHUT_DOWN = "37"
"""
Callback для отключения бота.
Использование: CBT.SHUT_DOWN:stage:instance_id

stage: int - текущая стадия подтверждения (0-6).
instance_id: int - ID запуска FPC.
"""

CANCEL_SHUTTING_DOWN = "38"
"""
Callback для отмены отключения бота.
"""


SEND_FP_MESSAGE = "to_node"
"""
Callback для отправки сообщения в чат FunPay.
Использование: CBT.SEND_FP_MESSAGE:node_id:username

node_id: int - ID переписки, в которую нужно отправить сообщение.
username: str - никнейм пользователя, переписка с которым ведется.
"""


UPLOAD_IMAGE = "upload_image"
"""
User-state: ожидается сообщение с изображением для выгрузки на сервер Funpay.
"""


UPDATE_PROFILE = "39"
"""
Callback для обновления статистики аккаунта.
"""


MANUAL_AD_TEST = "40"
"""
Callback для активации режима ввода названия лота для теста автовыдачи.


User-state: ожидается сообщение с названием лота для теста автовыдачи.
"""


CLEAR_STATE = "41"
"""
Callback для установки состояния пользователя на None.
"""


BACK_TO_REPLY_KB = "42"
"""
Callback для редактирования Telegram-сообщения: возвращение в клавиатуру нового сообщения.
Использование: CBT.BACK_TO_REPLY_KB:node_id:username:again:extend

node_id: int - ID чата.
username: str - никнейм пользователя, с которым ведется переписка.
again: 0/1 - вариант клавиатуры.
extend: 0/1 - добавить ли кнопку "Расширить"?
"""


BACK_TO_ORDER_KB = "43"
"""
Callback для редактирования Telegram-сообщения: возвращение в клавиатуру нового заказа.
Использование: CBT.BACK_TO_ORDER_KB:node_id:username:order_id:no_refund

node_id: int - ID чата.
username: str - никнейм пользователя, сделавшего заказ.
order_id: str - ID заказа.
no_refund: 0/1 - убрать ли кнопку возврата средств.
"""


# Плагины
PLUGINS_LIST = "44"
"""
Callback для открытия списка плагинов.
Использование: CBT.PLUGINS_LIST:offset

offset: int - смещение списка плагинов.
"""


EDIT_PLUGIN = "45"
"""
Callback для открытия меню информации о плагине.
Использование: CBT.EDIT_PLUGIN:UUID:offset

UUID: str - UUID плагина.
offset: int - смещение списка плагинов.
"""


TOGGLE_PLUGIN = "46"
"""
Callback для активации / деактивации плагина.
Использование: CBT.TOGGLE_PLUGIN:UUID:offset

UUID: str - UUID плагина.
offset: int - смещение списка плагинов.
"""


PLUGIN_SETTINGS = "47"
"""
Callback для открытия страницы настроек плагины.
Использование: CBT.PLUGIN_SETTING:UUID:offset

UUID: str - UUID плагина.
offset: int - смещение списка плагинов.
"""


PLUGIN_COMMANDS = "48"
"""
Callback для открытия списка команд плагина.
Использование: CBT.PLUGIN_COMMANDS:UUID:offset

UUID: str - UUID плагина.
offset: int - смещение списка плагинов.
"""


DELETE_PLUGIN = "49"
"""
Callback для удаление плагина.
Использование: CBT.DELETE_PLUGIN:UUID:offset

UUID: str - UUID плагина.
offset: int - смещение списка плагинов.
"""


CANCEL_DELETE_PLUGIN = "50"
"""
Callback для отмены удаления плагина.
Использование: CBT.CANCEL_DELETE_PLUGIN:UUID:offset

UUID: str - UUID плагина.
offset: int - смещение списка плагина.
"""


CONFIRM_DELETE_PLUGIN = "51"
"""
Callback для подтверждения удаления плагина.
Использование: CBT.CONFIRM_DELETE_PLUGIN:UUID:offset

UUID: str - UUID плагина.
offset: int - смещение списка плагинов.
"""


UPLOAD_PLUGIN = "52"
"""
Callback для активации режима ожидания отправки файла-плагина.
Использование: CBT.UPLOAD_PLUGIN:offset

offset: int - смещение списка плагинов.


User-state: ожидается файл-плагин.
data:
offset: int - смещение списка плагинов.
"""


PARAM_DISABLED = "53"
"""
Callback для обозначения отключенного параметра.
"""


MAIN2 = "54"
"""
Callback для вызова второй страницы основного меню настроек.
"""


EDIT_GREETINGS_TEXT = "55"
"""
Callback для активации режима ввода текста приветственного сообщения.

User-state: ожидается сообщение с текстом приветственного сообщения.
"""


EDIT_ORDER_CONFIRM_REPLY_TEXT = "56"
"""
Callback для активации режима ввода текста ответа на подтверждение заказа.

User-state: ожидается сообщение с текстом ответа на подтверждение заказа.
"""


SEND_REVIEW_REPLY_TEXT = "57"
"""
Callback для отправки текста ответа на отзыв.
Использование: CBT.SEND_REVIEW_REPLY_TEXT:start

stars: int - кол-во звезд (от 1 до 5)
"""


EDIT_REVIEW_REPLY_TEXT = "58"
"""
Callback для активации режима ожидания текста ответа на отзыв.
Использование: CBT.OPEN_REVIEW_REPLY_EDIT_MENU:stars

stars: int - кол-во звезд (от 1 до 5)

User-state: ожидается текст ответа на отзыв.
data:
stars: int - кол-во звезд (от 1 до 5)
"""


EDIT_WATERMARK = "59"
"""
Callback для активации режима ожидания текста вотемарки сообщений.

User-state: ожидается сообщение с текстом вотемарки сообщений.
"""


EXTEND_CHAT = "60"
"""
Callback для редактирования уведомления для показа последних 10 сообщений и того, что смотрит написавший.
Использование: CBT.EXTEND_CHAT:{node_id}:{username}
"""


OLD_MOD_HELP = "61"
"""
Callback для отправки справки о старом режиме получения сообщений.
"""


EMPTY = "62"
"""
Callback-затычка. Получает моментальный ответ и ничего не делает.
"""


LANG = "63"
"""
Callback для смены языка.
Использование: CBT.LANG:{lang}

lang: ru / eng - язык.
"""