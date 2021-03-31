from .inlinekeyboardvariables import *

inline_keyboard_types = {
    langs_keyboard: {
        "uz": "O'zbekcha (lotin)",
        "ru": "Русский",
        "cy": "Ўзбекча (kiril)"
    },

    confirm_keyboard: {
        "uz": {1: "Buyurtmani tasqiqlash", 2: "Buyurtmani bekor qilish", 3: "Manzilni xaritadan ko'rish"},
        "ru": {1: "Подтвердить заказ", 2: "Отмена заказа", 3: "Посмотреть местоположение на карте"},
        "cy": {1: "Буюртмани тасқиқлаш", 2: "Буюртмани бекор қилиш", 3: "Манзилни харитадан кўриш"},
    },

    order_keyboard: {
        "uz": {1: "Savatga qo'shish", 2: "Ortga", 3: "dona"},
        "ru": {1: "Добавить в корзину", 2: "Назад", 3: "шт."},
        "cy": {1: "Саватга қўшиш", 2: "Ортга", 3: "дона"},
    },

    orders_keyboard: {
        "uz": {1: "Buyurtmani qabul qilish", 2: "Buyurtmani bekor qilish", 3: "Manzilni xaritadan ko'rish"},
        "ru": {1: "Принять заказ", 2: "Отменить заказ", 3: "Посмотреть на карте"},
        "cy": {1: "Буюртмани қабул қилиш", 2: "Буюртмани бекор қилиш", 3: "Манзилни харитадан кўриш"},

    },

    yes_no_keyboard: {
        "uz": {1: "Ha", 2: "Yo'q"},
        "ru": {1: "Да", 2: "Нет"},
        "cy": {1: "Ҳа", 2: "Йўқ"}
    },

    basket_keyboard: {
        "uz": {1: "Umumiy narx"},
        "ru": {1: "Итоговая цена"},
        "cy": {1: "Умумий нарх"},
    },

    delivery_keyboard: {
        "uz": ["Yetkazib berildi"]
    },

    geo_keyboard: {
        "uz": ["Manzilni xaritadan ko'rish"],
        "ru": ["Посмотреть местоположение на карте"],
        "cy": ["Манзилни харитадан кўриш"]
    }
}
