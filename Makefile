alembic_dev_revision_app:
	docker-compose -f docker-compose.dev.yml run --rm app alembic revision --autogenerate -m "add deleted_at to news"

alembic_dev_upgrade_app:
	docker-compose -f docker-compose.dev.yml run --rm app alembic upgrade head
