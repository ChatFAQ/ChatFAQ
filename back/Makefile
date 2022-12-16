PYTHON_BIN ?= poetry run python

format: isort black

black:
	$(PYTHON_BIN) -m black --exclude '/(\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|node_modules|webpack_bundles)/' .

isort:
	$(PYTHON_BIN) -m isort riddler

run:
	./manage.py runserver 8000

spectacular:
	./manage.py spectacular --file schema.yml

create_fsm_fixtures:
	./manage.py dumpdata fsm --indent 4 > riddler/apps/fsm/fixtures/initial.json

apply_fsm_fixtures:
	./manage.py loaddata riddler/apps/fsm/fixtures/initial.json --app fsm
