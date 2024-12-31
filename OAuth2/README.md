# FastAPI_OAuth2
OAuth2 project in FastAPI

Команда создания первой ревизии базы данных:

``` lembic revision --autogenerate -m "Added accounts tables" ```

После этого надо внести изменения в сформированный файл ревизии в каталоге
*version*, а именно добавить импорт 
```
from Auth.db.db_connection import db_session
from Auth.utils import init_users
from Auth.db.db_types import MyDateTime
```
и в конце функции *upgrade*, после добавления колонок, вызвать инициализацию базы данных 
начальными пользователями

``` init_users(db_session) ```

Для инициализации базы данных надо запустить команду alembic из директории OAuth2

``` alembic upgrade head ```
