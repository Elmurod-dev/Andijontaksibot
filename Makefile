
mig:
	alembic revision --autogenerate -m "Create a baseline migrations"
#	alembic revision -m "Create a baseline migrations"
	alembic upgrade head

