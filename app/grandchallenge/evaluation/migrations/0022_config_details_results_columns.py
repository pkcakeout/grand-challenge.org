# Generated by Django 2.1.4 on 2019-01-08 10:53

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("evaluation", "0021_auto_20181205_2226")]

    operations = [
        migrations.AddField(
            model_name="config",
            name="details_results_columns",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                default=dict,
                help_text='A JSON object that contains the result details columns from metrics.json that will be displayed on the results detail page. Where the KEYS contain the titles of the columns, and the VALUES contain the JsonPath to the corresponding metric in metrics.json. For example:\n\n{"Accuracy": "aggregates.acc","Dice": "dice.mean"}',
            ),
        )
    ]
