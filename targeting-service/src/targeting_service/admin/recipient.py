from src.targeting_service.admin.base import BaseModelView
from src.targeting_service.model.view.recipient_admin_model import RecipientTable


class Recipient(BaseModelView, model=RecipientTable):
    identity = "recipient-table"
    name = "Получатель"
    name_plural = "Получатели"
    column_list = [
        # RecipientTable.id,
        RecipientTable.name,
        # RecipientTable.tags,
        # RecipientTable.telegram_id,
        RecipientTable.type,
        # RecipientTable.is_admin,
        RecipientTable.created_at,
        RecipientTable.updated_at,
    ]
    column_default_sort = [(RecipientTable.created_at, False)]
    column_details_exclude_list = [RecipientTable.tags]
    details_related_list = [
        {
            "field": "tags",
            "label": "Теги",
            "identity": "tag-table",
            "set_url_base": "/admin-api/recipient",
            "set_action": "set-tags",
            "body_key": "tag_ids",
            "available_url": "/admin-api/tags",
        },
    ]
    form_excluded_columns = [RecipientTable.created_at, RecipientTable.tags]
    column_formatters = {
        RecipientTable.created_at: BaseModelView.format_datetime,
        RecipientTable.updated_at: BaseModelView.format_datetime,
    }
    column_formatters_detail = {
        RecipientTable.created_at: BaseModelView.format_datetime,
        RecipientTable.updated_at: BaseModelView.format_datetime,
    }
    column_labels = {
        RecipientTable.name: "Наименование",
        RecipientTable.created_at: "Создано",
        RecipientTable.updated_at: "Обновлено",
        RecipientTable.tags: "Теги",
        RecipientTable.id: "Идентификатор записи БД",
        RecipientTable.telegram_id: "Телеграм ID",
        RecipientTable.type: "Тип получателя",
        RecipientTable.is_admin: "Является ли администратором",
        RecipientTable.created_by: "Создал(а)",
        RecipientTable.updated_by: "Обновил(а)",
    }
