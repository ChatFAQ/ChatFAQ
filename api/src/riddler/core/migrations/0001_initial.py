from pathlib import Path

from django.contrib.postgres.operations import CreateExtension
from django.db import migrations

from riddler.people import migrations as people_mig_mod

people_mig = Path(people_mig_mod.__file__).parent


class Migration(migrations.Migration):
    """
    This migration comes from the Model W template. The problem is that the
    people module needs the citext extension, however the template wants to
    let the developer create their initial migrations in order not to impose
    a model that is unfit from the first migration.

    As a result, this migration exists to install citext before the initial
    migration of people runs. But since this migration doesn't necessarily
    exist, we first check if the file is there before adding it to the
    run_before attribute.
    """

    dependencies = []

    operations = [CreateExtension("citext")]

    if (people_mig / "0001_initial.py").exists():
        run_before = [("people", "0001_initial")]
