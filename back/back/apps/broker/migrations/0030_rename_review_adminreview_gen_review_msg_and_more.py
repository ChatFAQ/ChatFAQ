# Generated by Django 4.1.13 on 2024-01-05 13:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("broker", "0029_alter_adminreview_review"),
    ]

    operations = [
        migrations.RenameField(
            model_name="adminreview",
            old_name="review",
            new_name="gen_review_msg",
        ),
        migrations.RenameField(
            model_name="adminreview",
            old_name="data",
            new_name="ki_review_data",
        ),
        migrations.AddField(
            model_name="adminreview",
            name="gen_review_val",
            field=models.IntegerField(
                choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)], null=True
            ),
        ),
    ]
