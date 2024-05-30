from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Импортируем модели и метаданные SQLAlchemy
from FastApi_project.models import Base  # Импортируем Base
from FastApi_project.database import engine  # Импортируем ваш engine

# Это объект MetaData для всех ваших моделей
target_metadata = Base.metadata

# Конфигурация для логгирования
if context.config.config_file_name:
    fileConfig(context.config.config_file_name)

# Конфигурация для Alembic
context.configure(
    url=engine.url if engine else None,
    target_metadata=target_metadata,
    render_as_batch=True,  # Используем render_as_batch вместо literal_binds
    dialect_opts={},
)

# Функция для выполнения миграций в offline режиме
def run_migrations_offline():
    context.configure(
        url='sqlite:///./test.db',  # Здесь должен быть ваш путь к базе данных
        target_metadata=target_metadata,
        literal_binds=False,  # Не используем literal_binds в offline режиме
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Функция для выполнения миграций в online режиме
def run_migrations_online():
    # Для online режима, нужно создать Engine и связать соединение с контекстом
    if engine is None:
        raise Exception("Engine is None")

    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

# Определяем, запускаем ли мы Alembic в offline или online режиме
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
