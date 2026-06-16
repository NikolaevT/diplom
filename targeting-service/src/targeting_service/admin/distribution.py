from src.targeting_service.admin.base import BaseModelView
from src.targeting_service.model.view.distribution_admin_model import DistributionTable


class Distribution(BaseModelView, model=DistributionTable):
    identity = "distribution-table"
    name = "Рассылка"
    name_plural = "Рассылки"
    column_list = [
        # DistributionTable.id,
        DistributionTable.name,
        # DistributionTable.bmc_distribution_id,
        # DistributionTable.tags,
        DistributionTable.created_at,
        DistributionTable.updated_at,
        # DistributionTable.created_by,
        # DistributionTable.updated_by,
    ]
    column_default_sort = [(DistributionTable.created_at, False)]
    form_excluded_columns = [DistributionTable.created_at, DistributionTable.tags]
    column_details_exclude_list = [DistributionTable.tags]
    details_related_list = [
        {
            "field": "tags",
            "label": "Теги",
            "identity": "tag-table",
            "set_url_base": "/admin-api/distribution",
            "set_action": "set-tags",
            "body_key": "tag_ids",
            "available_url": "/admin-api/tags",
        },
    ]
    column_formatters = {
        DistributionTable.created_at: BaseModelView.format_datetime,
        DistributionTable.updated_at: BaseModelView.format_datetime,
    }
    column_formatters_detail = {
        DistributionTable.created_at: BaseModelView.format_datetime,
        DistributionTable.updated_at: BaseModelView.format_datetime,
    }
    column_labels = {
        DistributionTable.id: "Идентификатор записи БД",
        DistributionTable.bmc_distribution_id: "Ключ из БМК ИТ",
        DistributionTable.name: "Наименование",
        DistributionTable.created_at: "Создано",
        DistributionTable.updated_at: "Обновлено",
        DistributionTable.tags: "Теги",
        DistributionTable.updated_by: "Обновил(а)",
        DistributionTable.created_by: "Создал(а)",
    }
