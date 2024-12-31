from abc import ABC, abstractmethod


class AbstractPwdContext(ABC):
    """ Абстрактный класс для управления криптографией пароля. """
    @abstractmethod
    def hash(self, password: str) -> str:
        """
        Рассчитывает ХЭШ сумму указанного пароля.
        :param password: Строка пароля.
        :return: Рассчитанная ХЭШ сумма пароля.
        """
        raise NotImplementedError()

    @abstractmethod
    def verify(self, password, _hash) -> bool:
        """
        Проверяет пароль.
        :param password: Строка пароля для проверки.
        :param _hash: ХЭШ пароля, с которым производится проверка.
        :return: Верный ли пароль.
        """
        raise NotImplementedError
