"""Запуск SQL-миграций через yoyo-migrations."""

from pathlib import Path

from yoyo import get_backend, read_migrations

from src.targeting_service.config import settings


MIGRATIONS_DIR = str(Path(__file__).parent / "migrations")


def run_migrations() -> None:
    """Применить все НОВЫЕ SQL-миграции из каталога migrations."""
    db_url = (
        f"postgresql://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )
    backend = get_backend(db_url)
    migrations = read_migrations(MIGRATIONS_DIR)
    with backend.lock():
        pending = backend.to_apply(migrations)
        if not pending:
            print("Новых миграций нет.")
            return
        for migration in pending:
            print(f"Применение миграции: {migration.id}")
        backend.apply_migrations(pending)
    print("Все миграции применены.")


def main() -> None:
    run_migrations()


if __name__ == "__main__":
    main()
