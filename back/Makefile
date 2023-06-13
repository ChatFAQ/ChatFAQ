PYTHON_BIN ?= poetry run python

format: isort black

black:
	$(PYTHON_BIN) -m black --exclude '/(\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|node_modules|webpack_bundles)/' .

isort:
	$(PYTHON_BIN) -m isort .

run:
	./pmanage runserver 8000

run_daphne:
	$(PYTHON_BIN) daphne back.config.asgi:application

spectacular:
	./pmanage spectacular --file schema.yml

docs:
	poetry run $(MAKE) -f doc/Makefile html

create_fixtures:
	./pmanage dumpdata auth.group --indent 4 > back/apps/people/fixtures/initial.json

apply_fixtures:
	./pmanage loaddata back/apps/people/fixtures/initial.json --app auth.group

celery_worker:
	poetry run celery -A back.config worker -l INFO -P gevent

# create_fsm_fixtures:
# 	./manage.py dumpdata fsm.fsmdefinition --indent 4 > back/apps/fsm/fixtures/initial.json
#
# apply_fsm_fixtures:
# 	./manage.py loaddata back/apps/fsm/fixtures/initial.json --app fsm
#
