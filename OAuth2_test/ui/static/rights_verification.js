/**
 * Класс проверки прав
 */
class RightsVerification {
    /**
     * Конструктор класса.
     * @param {HTMLElement} block Блок в котором должны быть созданы кнопки.
     */
    constructor(block) {
        /** @param {HTMLElement} Блок в котором должны быть созданы кнопки. */
        this.block = block
        /** @param {Array} Список всех эндпоинтов проверки прав. */
        this.api_list = {"scope/me": "Указан scope 'me'", 
            "scope/me_items": "Указаны scope 'me' и 'items'", 
            "only_admin": "Имеет роль администратора", 
            "only_director": "Имеет роль директора", 
            "only_admin_or_director": "Имеет роль администратора или директора", 
            "only_user": "Имеет роль посетителя", 
            "only_authorized_user": "Пользователь авторизован", 
            "only_anonym_user": "Пользователь не авторизован"};
        /** @param {Object} Словарь всех значков с ключём API. */
        this.badgeList = {};
    }

    /**
     * Инициирует работу класса проверки прав.
     * @param {Function} checkRightRequest Функция запроса проверки права со следующей сигнатурой: (api, successfullResponseFunc, errorResposeFunc).
     */
    init(checkRightRequest) {
        this.addButtonRows();
        this.addEventListner(checkRightRequest);
    }

    /**
     * Добавляет строки с кнопками.
     */
    addButtonRows() {
        for (let [api, tooltip] of Object.entries(this.api_list))
            this.block.appendChild(this.createRow(api, tooltip));
    }

    /**
     * Добавляет обработчик для нажатия на кнопки.
     * @param {Function} checkRightRequest Функция запроса проверки права со следующей сигнатурой: (api, successfullResponseFunc, errorResposeFunc).
     */
    addEventListner(checkRightRequest) {
        this.block.addEventListener('click', (ev) => this.buttonClickHandler(ev, checkRightRequest));
        
    }

    /**
     * Обработчик нажатия кнопок.
     * @param {MouseEvent} event Класс события нажатия кнопки мыши.
     * @param {Function} checkRightRequest Функция запроса проверки права со следующей сигнатурой: (api, successfullResponseFunc, errorResposeFunc).
     */
    buttonClickHandler(event, checkRightRequest) {
        /** @param {HTMLButtonElement} Кнопка, которая была нажата. */
        let button = event.target;
        if (button.nodeName != 'BUTTON')
            return;

        const api = button.getAttribute('data-api');
        checkRightRequest(api, 
            () => this.setBadge(api, 'ok'), 
            (statusText, statusCode, response) => {
                if (statusCode == 401)
                    this.setBadge(api, 'invalid');
                else {
                    alert(`Error: ${statusCode} - ${statusText}`);
                }
            })
    }

    /**
     * Устанавливает badge.
     * @param {String} api 
     * @param {String} Параметр установки ok, invalid или hide.
     */
    setBadge(api, param) {
        switch(param) {
            case 'ok':
                this.setBadgeOk(api);
                break;
            case 'invalid':
                this.setBadgeInvalid(api);
                break;
            case 'hide':
                this.setBadgeHide(api);
                break;
        }
    }

    /**
     * Устанавливает значёк в Ok.
     * @param {String} api API к которому относится значёк.
     */
    setBadgeOk(api) {
        /** @param {HTMLElement} */
        let badge = this.badgeList[api];
        if (badge.classList.contains('d-none'))
            badge.classList.remove('d-none');
        
        if (badge.classList.contains('text-bg-danger')) {
            badge.classList.remove('text-bg-danger');
            badge.classList.add('text-bg-success');
            badge.innerText = "Ok";
        }
    }

    /**
     * Устанавливает значок в Invalid.
     * @param {String} api API к которому относится значок.
     */
    setBadgeInvalid(api) {
        /** @param {HTMLElement} */
        let badge = this.badgeList[api];
        if (badge.classList.contains('d-none'))
            badge.classList.remove('d-none');

        if (badge.classList.contains('text-bg-success')) {
            badge.classList.remove('text-bg-success');
            badge.classList.add('text-bg-danger');
            badge.innerText = "Invalid";
        }
    }

    /**
     * Скрывает значок.
     * @param {String} api API к которому относится значок.
     */
    setBadgeHide(api) {
        let badge = this.badgeList[api];
        badge.classList.add('d-none')
    }

    /**
     * Скрывает все значки.
     */
    hideAllBadge() {
        for (let api of Object.keys(this.api_list))
            this.setBadgeHide(api);
    }

    /**
     * Создаёт строку проверки права.
     * @param {String} api API по которой будет проверятся право.
     * @param {String} tooltip Описание для кнопки.
     * @returns 
     */
    createRow(api, tooltip) {
        let div = this.createHTMLElement('div', ['mb-3', 'row'])
        div.appendChild(this.createButton(api, tooltip));
        let badge = this.createSpanBadge();
        div.appendChild(badge);
        // Для дальнейшего урпавления значками, они все сохраняются в объект с ключём API.
        this.badgeList[api] = badge;        
        return div
    }

    /**
     * Создёет кнопку.
     * @param {String} btnName Текст кнопки.
     * @param {String} api API к которой относиться кнопка.
     * @param {String} tooltip Подсказка.
     * @returns {HTMLElement}
     */
    createButton(api, tooltip) {
        let classList = ['col-3', 'btn', 'btn-secondary'];
        let attrs = {type: 'button', 'data-api': api, title: tooltip};
        return this.createHTMLElement('button', classList, attrs, api.replace(/[\/_]/g, ' '));
    }

    /**
     * Создаёет значок.
     * @returns {HTMLElement}
     */
    createSpanBadge () {
        let classList = ['d-none', 'col-1', 'offset-1', 'badge', 'rounded-pill', 'text-bg-success', 'fs-6'];
        return this.createHTMLElement('span', classList, {}, 'OK');
    }

    /**
     * Создаёт элемент HTML.
     * @param {String} tagName Наименование тэга.
     * @param {Array} classList Список классов.
     * @param {Object} atrs Объект с аттрибутами.
     * @param {String} text Текст.
     * @returns {HTMLElement}
     */
    createHTMLElement(tagName, classList, attrs=undefined, text=undefined) {
        let element = document.createElement(tagName);
        for (const list of classList)
            element.classList.add(list);
        if (attrs != undefined)
            for (let key in attrs)
                element.setAttribute(key, attrs[key]);
        if (text != undefined) 
            element.innerText = text;
        return element;
    }
}