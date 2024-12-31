document.addEventListener('DOMContentLoaded', function() {
    const HTML_CLASS_HIDDEN = "d-none";
    const host = window.location.origin;

    const tokenField = document.getElementById("token");
    const userInfoField = document.getElementById("user_info");
    const requestBtn = document.getElementById("btn_request");
    const rightsVerificationBlok = document.querySelector("#infoBlock .rights-verification-col");

    const rightsVerification = new RightsVerification(rightsVerificationBlok);

    rightsVerification.init(checkRightRequest);
    // Назначение обработчика кнопке запроса информаци о пользователе.
    requestBtn.addEventListener("click", getUserRequest);
    tokenField.addEventListener('keypress', (ev) => {
        if (ev.key == "Enter") {
            ev.preventDefault();
            requestBtn.click();
        }
    })

    /**
     * Запрашивает пользователя по указанному токену.
     */
    function getUserRequest() {
        const api = "/api/test/get_user";
        const tokenRefresh = `bearer ${tokenField.value}`;
        const headers = tokenField.value != "" ? {Authorization: tokenRefresh} : {};

        rightsVerification.hideAllBadge();
        apiRequest("GET", host, api, successfulResponse, errorResponse, headers, {});
    }

    /**
     * Функция обработки успешного получения токенов.
     * @param {*} data 
     */
        function successfulResponse(data) {
            hideAllertDanger();
            fillUserFields(data);
        }
    
    /**
     * Ошибка при ответе от сервера.
     * @param {*} statusText 
     * @param {*} response 
     */
    function errorResponse(statusText, statusCode, response) {
        clearUserFields();
        if ([400, 401].indexOf(statusCode) != -1)
            response.then(responsen_json => {
                showAlertDanger(`Error: ${statusText}. ${responsen_json['detail']}`);
        });
        else {
            showAlertDanger(`Error: ${statusCode} - ${statusText}`);
        }
    }

    /**
     * Проверка прав ууказанного api.
     * @param {String} api 
     * @param {CallableFunction} successfullResponseFunc Функция обработки успешного овтета на запрос.
     * @param {CallableFunction} errorResposeFunc Функция обработки ошибки ответа на запрос.
     */
    function checkRightRequest(api, successfullResponseFunc, errorResposeFunc) {
        api = `/api/test/${api}`;
        const tokenRefresh = `bearer ${tokenField.value}`;
        const headers = tokenField.value != "" ? {Authorization: tokenRefresh} : {};

        apiRequest("GET", host, api, successfullResponseFunc, errorResposeFunc, headers, {});
    }

    /**
     * Отображет сообшение об ошибке.
     * @param {String} msg Сообшение об ошибке.
     */
    function showAlertDanger(msg) {
        alertDanger.textContent = msg;
        if (alertDanger.classList.contains(HTML_CLASS_HIDDEN)) 
            alertDanger.classList.remove(HTML_CLASS_HIDDEN);
    }
    
    /**
     * Скрывает сообшение об ошибке.
     */
    function hideAllertDanger() {
        if (!alertDanger.classList.contains(HTML_CLASS_HIDDEN)) {
            alertDanger.classList.add(HTML_CLASS_HIDDEN);
            alertDanger.textContent = "";
        }
    }

    /**
     * Заполняет поле пользователя.
     * @param {*} response Ответ от сервера.
     */
    function fillUserFields(response){
        userInfoField.value = convertResponseToUser(response);
    }

    /**
     * Преобразует ответ в данные о пользователе.
     * @param {*} response Ответ от сервера.
     * @returns 
     */
    function convertResponseToUser(response) {
        user = response[0];
        scopes = response[1]
        let result = "";
        for (prop in user) {
            result += `${prop}: ${user[prop]}\n`;
        }
        if (scopes.length > 0)
            result += `scopes: ${scopes.join(", ")}\n`;
        return result;
    }

    /**
    * Очищает поле информации о пользователе.
    */
    function clearUserFields() {
        userInfoField.value = "";
    }
});

/**
 * Проверка на пустой объект.
 * @param obj
 * @returns {boolean}
 */
function isObjectEmpty(obj) {
    for (let key in obj)
        if (obj.hasOwnProperty(key))
            return false;
    return true;
}

/**
 * API запрос.
 * @param {String method} Метод запроса (GET | POST)
 * @param {String} api Эндпоинт.
 * @param {function} successCallback Функция обратного вызова при успешном ответе.
 * @param {function} failedStatusCallback Функция обратного вызова при ошибке ответа.
 * @param {{}} [headers={}] Заголовки запроса.
 * @param {{}} [data={}] Данные запроса.
 */
function apiRequest(method, host, api, successCallback, failedStatusCallback, headers={}, data={}) {
    const url=`${host}${api}`;
    const requiredHeaders = {"content-type": "application/json; charset=UTF-8"};
    Object.assign(headers, requiredHeaders);

    let options = {
        headers: headers,
        method: method,
    };

    // Если переданы доанные формы,
    if (data instanceof FormData) {
        delete (options.headers);
        // то эту форму передает в тело запроса.
        options['body'] = data;
    } else if ((typeof (data) === 'object') && !(isObjectEmpty(data))) {
        // Иначе эти данные должны быть переданы в свойстве body в виде параметра.
        options['body'] = getSearchParams(data);
    }

    fetch(url, options)
    .then(response => {
        if (response.ok) {
            return response.json()
        } else {
            throw new StatusError(response.statusText, response.status, response.json())
        }
    })
    .then(data => {
        successCallback(data);
    })
    .catch(error => {
       failedStatusCallback(error.message, error.statusCode, error.response)
    })
}

/**
 * Класс ошикби статуса
 */
class StatusError extends Error {
    /**
     * Конструктор класса
     * @param {String} message Сообщение ошибки.
     * @param {Number} statusCode Код ответа.
     * @param {*} response Ответ в виде Promise.
     */
    constructor(message, statusCode, response) {
        super(message);
        this.name = "StatusError";
        this.statusCode = statusCode;
        this.response = response;
    }
}