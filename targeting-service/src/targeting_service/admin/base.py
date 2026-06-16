from typing import ClassVar

from sqladmin import ModelView


class BaseModelView(ModelView):
    """Базовый ModelView для админок: общие настройки по умолчанию."""

    list_template = "sqladmin/table.html"
    details_related_list: ClassVar[list] = []
    can_export = False

    @staticmethod
    def format_datetime(obj, prop):
        """Форматтер даты/времени для списка и деталей (dd.mm.yyyy HH:MM)."""
        val = getattr(obj, prop, None)

        if val is None:
            return ""

        if hasattr(val, "strftime"):
            return val.strftime("%d.%m.%Y %H:%M")

        return str(val)
