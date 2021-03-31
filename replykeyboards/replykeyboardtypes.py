from .replykeyboardvariables import *

reply_keyboard_types = {
    admin_menu_keyboard: {
        "uz": {
            1: "Yangi buyurtmalar",
            2: "Qabul qilingan buyutmalar",
            3: "Tarix",
            4: "Sozlamalar",
            5: "Menyu",
            6: "Foydalanuvchilarga xabar yuborish"
        },
        "ru": {
            1: "Новые заказы",
            2: "Принятые заказы",
            3: "История",
            4: "Настройки",
            5: "Меню",
            6: "Отправить сообщение пользователям"
        },
        "cy": {
            1: "Янги буюртмалар",
            2: "Қабул қилинган буютмалар",
            3: "Тарих",
            4: "Созламалар",
            5: "Меню",
            6: "Фойдаланувчиларга хабар юбориш"
        }
    },

    client_menu_keyboard: {
        "uz": {
            1: "Menyu",
            2: "Xarid savati",
            3: "Biz bilan bog'lanish",
            4: "Sozlamalar",
        },
        "ru": {
            1: "Меню",
            2: "Корзина",
            3: "Свяжитесь с нами",
            4: "Настройки"
        },
        "cy": {
            1: "Меню",
            2: "Харид савати",
            3: "Биз билан боғланиш",
            4: "Созламалар",
        }

    },

    menu_keyboard: {
        "uz": {1: "Osh", 2: "Salatlar", 3: "Ichimliklar", 4: "Non", 5: "Qo'shimcha", 6: "Bosh menyu",
               7: "Xarid savati"},
        "ru": {1: "Плов", 2: "Салаты", 3: "Напитки", 4: "Хлеб", 5: "Дополнительный", 6: "Главное меню", 7: "Корзина"},
        "cy": {1: "Ош", 2: "Салатлар", 3: "Ичимликлар", 4: "Нон", 5: "Қўшимча", 6: "Бош меню", 7: "Харид савати"},
    },

    settings_keyboard: {
        "uz": {1: "Ism,familyani o'zgartirish", 2: "Tilni o'zgartirish", 3: "Ortga"},
        "ru": {1: "Изменить имя, фамилию", 2: "Изменить язык", 3: "Назад"},
        "cy": {1: "Исм,фамиляни ўзгартириш", 2: "Тилни ўзгартириш", 3: "Ортга"},
    },

    phone_number_keyboard: {
        "uz": {1: "Telefon raqamini yuborish"},
        "ru": {1: "Отправить номер телефона"},
        "cy": {1: "Телефон рақамини юбориш"},
    },

    location_keyboard: {
        "uz": {1: 'keyingisi', 2: 'Geolokatsiyamni yuborish'},
        "ru": {1: 'keyingisi', 2: 'Отправить мою геолокацию'},
        "cy": {1: 'keyingisi', 2: 'Геолокациямни юбориш'}
    }
}
