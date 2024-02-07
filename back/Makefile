POETRY_RUN ?= poetry run

PYTHON_BIN ?= $(POETRY_RUN) python

format: isort black

black:
	$(PYTHON_BIN) -m black --exclude '/(\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|node_modules|webpack_bundles)/' .

isort:
	$(PYTHON_BIN) -m isort .

run:
	$(POETRY_RUN) ./pmanage runserver 8000

run_daphne:
	$(PYTHON_BIN) daphne back.config.asgi:application

spectacular:
	$(POETRY_RUN) ./pmanage spectacular --file schema.yml

docs:
	$(POETRY_RUN) $(MAKE) -f doc/Makefile html

create_fixtures:
	$(POETRY_RUN) ./pmanage dumpdata auth.group --indent 4 > back/apps/people/fixtures/initial.json

apply_fixtures:
	$(POETRY_RUN) ./pmanage loaddata back/apps/people/fixtures/initial.json --app auth.group
	$(POETRY_RUN) ./pmanage loaddata back/apps/language_model/fixtures/initial.json --app language_model

celery_worker:
	$(POETRY_RUN) celery -A back.config worker -l INFO -P solo

# create_fsm_fixtures:
# 	./manage.py dumpdata fsm.fsmdefinition --indent 4 > back/apps/fsm/fixtures/initial.json
#
# apply_fsm_fixtures:
# 	./manage.py loaddata back/apps/fsm/fixtures/initial.json --app fsm
#
