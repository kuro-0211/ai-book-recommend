from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Recommendation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("keyword", models.CharField(db_index=True, max_length=255)),
                ("raw_response", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=500)),
                ("author", models.CharField(blank=True, default="", max_length=255)),
                ("summary", models.TextField(blank=True, default="")),
                ("reason", models.TextField(blank=True, default="")),
                ("position", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("recommendation", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="books",
                    to="recommender.recommendation",
                )),
            ],
            options={"ordering": ["position", "id"]},
        ),
        migrations.CreateModel(
            name="WeeklyTopKeyword",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("week_start", models.DateField()),
                ("rank_no", models.IntegerField()),
                ("keyword", models.CharField(max_length=255)),
                ("hit_count", models.IntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-week_start", "rank_no"],
                "unique_together": {("week_start", "rank_no")},
            },
        ),
    ]
