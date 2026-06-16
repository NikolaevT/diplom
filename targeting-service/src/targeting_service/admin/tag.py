from src.targeting_service.admin.base import BaseModelView
from src.targeting_service.model.view.tag_admin_model import TagTable


class Tag(BaseModelView, model=TagTable):
    name = "Тег"
    name_plural = "Теги"
    column_list = [
        # TagTable.id,
        TagTable.name,
        TagTable.created_at,
        TagTable.updated_at,
    ]
    column_default_sort = [(TagTable.created_at, False)]
    form_excluded_columns = [TagTable.distributions, TagTable.recipients]
    column_details_exclude_list = [TagTable.recipients]
    details_related_list = [
        {
            "field": "recipients",
            "label": "Получатели",
            "identity": "recipient-table",
            "set_url_base": "/admin-api/tag",
            "set_action": "set-recipients",
            "body_key": "recipient_ids",
            "available_url": "/admin-api/recipients",
        },
    ]
    column_formatters = {
        TagTable.created_at: BaseModelView.format_datetime,
        TagTable.updated_at: BaseModelView.format_datetime,
    }
    column_formatters_detail = {
        TagTable.created_at: BaseModelView.format_datetime,
        TagTable.updated_at: BaseModelView.format_datetime,
    }
    column_labels = {
        TagTable.name: "Наименование",
        TagTable.created_at: "Создано",
        TagTable.updated_at: "Обновлено",
        TagTable.distributions: "Рассылки",
        TagTable.recipients: "Получатели",
        TagTable.id: "Идентификатор записи БД",
        TagTable.updated_by: "Обновил(а)",
        TagTable.created_by: "Создал(а)",
    }
