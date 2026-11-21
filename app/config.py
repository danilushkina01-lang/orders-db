import os


def get_database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://orders_user:orders_pass@localhost:5432/orders_db",
    )


TEST_DATABASE_URL = "postgresql+psycopg2://orders_user:orders_pass@localhost:5432/orders_test"
