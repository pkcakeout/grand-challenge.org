# Generated by Django 2.1.7 on 2019-03-28 12:13

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import grandchallenge.container_exec.models
import grandchallenge.core.storage
import grandchallenge.core.validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Session",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "creator",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Workstation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "title",
                    models.CharField(max_length=255, verbose_name="title"),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="description"
                    ),
                ),
                (
                    "slug",
                    django_extensions.db.fields.AutoSlugField(
                        blank=True,
                        editable=False,
                        populate_from="title",
                        verbose_name="slug",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="WorkstationImage",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "staged_image_uuid",
                    models.UUIDField(blank=True, editable=False, null=True),
                ),
                (
                    "image",
                    models.FileField(
                        blank=True,
                        help_text=".tar.gz archive of the container image produced from the command 'docker save IMAGE > IMAGE.tar | gzip'. See https://docs.docker.com/engine/reference/commandline/save/",
                        storage=grandchallenge.core.storage.PrivateS3Storage(),
                        upload_to=grandchallenge.container_exec.models.docker_image_path,
                        validators=[
                            grandchallenge.core.validators.ExtensionValidator(
                                allowed_extensions=(".tar", ".tar.gz")
                            )
                        ],
                    ),
                ),
                (
                    "image_sha256",
                    models.CharField(editable=False, max_length=71),
                ),
                (
                    "ready",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        help_text="Is this image ready to be used?",
                    ),
                ),
                ("status", models.TextField(editable=False)),
                ("requires_gpu", models.BooleanField(default=False)),
                (
                    "requires_gpu_memory_gb",
                    models.PositiveIntegerField(default=4),
                ),
                ("requires_memory_gb", models.PositiveIntegerField(default=4)),
                (
                    "requires_cpu_cores",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("1.0"), max_digits=4
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workstation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="workstations.Workstation",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.AddField(
            model_name="session",
            name="workstation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="workstations.Workstation",
            ),
        ),
    ]