.PHONY: admin-user, test-data

admin-user:
	docker-compose run web python /code/crt_portal/manage.py createsuperuser

test-data:
	docker compose run web python /code/crt_portal/manage.py create_mock_reports 1500