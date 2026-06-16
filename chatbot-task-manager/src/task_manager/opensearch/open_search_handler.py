from opensearch_logger import OpenSearchHandler

from src.task_manager.config.settings import settings


def create_opensearch_handler() -> OpenSearchHandler:
    return OpenSearchHandler(
        index_name=settings.opensearch_index_prefix,
        hosts=list(settings.opensearch_hosts),
        http_auth=(settings.opensearch_username, settings.opensearch_password),
        http_compress=True,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        raise_on_index_exc=False,
        buffer_size=1000,
        flush_frequency=5.0,
        index_date_format="%Y%m%d",
        extra_fields={
            "service": settings.app_name,
            "environment": settings.environment,
        },
    )
