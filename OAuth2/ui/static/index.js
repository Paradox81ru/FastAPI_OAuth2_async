document.addEventListener('DOMContentLoaded', function() {
    const HTML_CLASS_HIDDEN = "d-none";
    const host = window.location.origin;

    const formAuth = document.getElementById("formAuth");
    const alertDanger = document.getElementById("alertDanger");
    const fieldUsername = document.getElementById("fldUsername");
    const fieldPassword = document.getElementById("fldPassword");
    const checkboxScopeMe = document.getElementById("chbScopeMe");
    const checkboxScopeItems = document.getElementById("chbScopeItems");
    const btnRequestTokens = document.getElementById("btnRequestTokens");

    const fieldTokenAccess = document.getElementById("fldTokenAccess");
    const fieldTokenRefresh = document.getElementById("fldTokenRefresh");
    const btnTokenRefresh = document.getElementById("btnTokenRefresh");

    btnRequestTokens.addEventListener("click", requestTokenHandler);
    btnTokenRefresh.addEventListener('click', requestRefreshTokenHandler);
    formAuth.addEventListener('keypress', (ev) => {
        if (ev.key == "Enter") {
            ev.preventDefault();
            btnRequestTokens.click();
        }
    })

    /**
     * Обработчик кнопки запроса токенов.
     * @param {MouseEvent} ev
     */
    function requestTokenHandler(ev) {
        authorizationRequest();
    }

    /**
     * Обработчик кнопки обновления токенов.
     * @param {MouseEvent} ev 
     */
    function requestRefreshTokenHandler(ev) {
        tokenRefreshRequest();
    }

    /**
     * Запрос получения токенов.
     */
    function authorizationRequest() {
        const api = "/api/oauth/token";
        const formData = getFormData();

        apiRequest("POST", host, api, successfulResponse, errorResponse, {}, formData);
    }

    /**
     * Формирует данные формы.
     * @returns Данные формы.
     */
    function getFormData() {
        let formData = new FormData(formAuth);
        let scopes = [];
        let forDelete = []
        // Проходит по всем полям формы,
        for (let [name, value] of formData) {
            if (name.startsWith('scope')) {
                // если есть Scope, то добавляет его в общий массив scopes,
                scopes.push(value);
                // а само поле добавляется в массив для дальнейшего удаления его из формы.
                forDelete.push(name)
            }
        }
        // Удаление ненужных scope полей из формы.
        for (item of forDelete)
            formData.delete(item);
        
        // Добавление в форму нового поля, со списком значений scope разделённых пробелом.
        formData.set('scope', scopes.join(' '));
        return formData;
    }

    /**
     * Запрос обновления токенов.
     */
    function tokenRefreshRequest() {
        const api = "/api/oauth/token-refresh";
        const tokenRefresh = `bearer ${fieldTokenRefresh.value}`;
        const expiredToken = fieldTokenAccess.value;
        const headers = {Authorization: tokenRefresh, expiredToken: expiredToken};

        apiRequest("POST", host, api, successfulResponse, errorResponse, headers, {});
    }

    /**
     * Функция обработки успешного получения токенов.
     * @param {Object} data 
     */
    function successfulResponse(data) {
        hideAlertDanger();
        fillTokenFields(data['access_token'], data['refresh_token'])
    }
 

    /**
     * Ошибка при ответе от сервера.
     * @param {String} statusText Статус ответа.
     * @param {*} response Ответ в виде Promise.
     */
    function errorResponse(statusText, statusCode, response) {
        clearTokenFields();
        if ([400, 401].indexOf(statusCode) != -1)
            response.then(response_json => {
                showAlertDanger(`Error: ${statusText}. ${response_json['detail']}`);
        });
        else {
            showAlertDanger(`Error: ${statusCode} - ${statusText}`);
        }
    }

    /**
     * Заполняет поля токенов данными.
     * @param {String} accessToken Токен доступа.
     * @param {String} refreshToken Токен обновления.
     */
    function fillTokenFields(accessToken, refreshToken) {
        fieldTokenAccess.value = accessToken;
        fieldTokenRefresh.value =  refreshToken;
    }

    /**
     * Очищает поля токенов.
     */
    function clearTokenFields() {
        fieldTokenAccess.value = '';
        fieldTokenRefresh.value = '';
    }


    /**
     * Отображает сообщение об ошибке.
     * @param {String} msg Сообщение об ошибке.
     */
    function showAlertDanger(msg) {
        alertDanger.textContent = msg;
        if (alertDanger.classList.contains(HTML_CLASS_HIDDEN)) 
            alertDanger.classList.remove(HTML_CLASS_HIDDEN);
    }

    /**
     * Скрывает сообщение об ошибке.
     */
    function hideAlertDanger() {
        if (!alertDanger.classList.contains(HTML_CLASS_HIDDEN)) {
            alertDanger.classList.add(HTML_CLASS_HIDDEN);
            alertDanger.textContent = "";
        }

    }
});

/**
 * Проверка на пустой объект.
 * @param obj Проверяемый объект.
 * @returns {boolean}
 */
function isObjectEmpty(obj) {
    for (let key in obj)
        if (obj.hasOwnProperty(key))
            return false;
    return true;
}

/**
 * Формирует и возвращает строку параметра запроса.
 * @param {Object} data
 * @returns {string}
 */
function getSearchParams(data) {
    let searchParams = new URLSearchParams();
    for (let key in data)
        searchParams.append(key, data[key]);

    return searchParams.toString();
}

/**
 * API запрос.
 * @param {String method} Метод запроса (GET | POST).
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
            // throw new ResonseError(response.statusText, response.status, response);
            throw new StatusError(response.statusText, response.status, response.json())
        }
    })
    .then(data => {
        successCallback(data);
    })
    .catch(error => {
        // return error.resopnse.json
       failedStatusCallback(error.message, error.statusCode, error.response)
    })
}

/**
 * СОбственный класс ошибуи статуса.
 */
class StatusError extends Error {
    constructor(message, statusCode, response) {
        super(message);
        this.name = "StatusError";
        this.statusCode = statusCode;
        this.response = response;
    }
}