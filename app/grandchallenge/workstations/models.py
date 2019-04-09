from datetime import timedelta
from urllib.parse import unquote, urljoin

from django.conf import settings
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models
from django_extensions.db.models import TitleSlugDescriptionModel
from rest_framework.authtoken.models import Token

from grandchallenge.container_exec.backends.docker import Service
from grandchallenge.container_exec.models import ContainerImageModel
from grandchallenge.container_exec.tasks import start_service, stop_service
from grandchallenge.core.models import UUIDModel
from grandchallenge.subdomains.utils import reverse


class Workstation(UUIDModel, TitleSlugDescriptionModel):
    def get_absolute_url(self):
        return reverse("workstations:detail", kwargs={"slug": self.slug})


class WorkstationImage(UUIDModel, ContainerImageModel):
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE)
    http_port = models.PositiveIntegerField(
        default=8080, validators=[MaxValueValidator(2 ** 16 - 1)]
    )
    websocket_port = models.PositiveIntegerField(
        default=4114, validators=[MaxValueValidator(2 ** 16 - 1)]
    )
    initial_path = models.CharField(
        max_length=256,
        default="Applications/GrandChallengeViewer/index.html",
        validators=[
            RegexValidator(
                regex=r"^(?:[^/][^\s]*)\Z",
                message="This path is invalid, it must not start with a /",
            )
        ],
    )

    def get_absolute_url(self):
        return reverse(
            "workstations:image-detail",
            kwargs={"slug": self.workstation.slug, "pk": self.pk},
        )


class Session(UUIDModel):
    QUEUED = 0
    STARTED = 1
    RUNNING = 2
    FAILED = 3
    STOPPED = 4

    STATUS_CHOICES = (
        (QUEUED, "Queued"),
        (STARTED, "Started"),
        (RUNNING, "Running"),
        (FAILED, "Failed"),
        (STOPPED, "Stopped"),
    )

    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=QUEUED
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    workstation_image = models.ForeignKey(
        WorkstationImage, on_delete=models.CASCADE
    )
    maximum_duration = models.DurationField(default=timedelta(minutes=10))
    # Is the user done with this session?
    user_finished = models.BooleanField(default=False)

    @property
    def task_kwargs(self):
        # The kwargs that need to be passed to celery to get this object
        return {
            "app_label": self._meta.app_label,
            "model_name": self._meta.model_name,
            "pk": self.pk,
        }

    @property
    def hostname(self):
        return (
            f"{self.pk}.{self._meta.model_name}.{self._meta.app_label}".lower()
        )

    @property
    def expires_at(self):
        return self.created + self.maximum_duration

    @property
    def environment(self):
        env = {
            "GRAND_CHALLENGE_PROXY_URL_MAPPINGS": "",
            "GRAND_CHALLENGE_QUERY_IMAGE_URL": unquote(
                reverse("api:image-detail", kwargs={"pk": "{key}"})
            ),
        }

        if self.creator:
            env.update(
                {
                    "GRAND_CHALLENGE_AUTHORIZATION": f"TOKEN {Token.objects.get_or_create(user=self.creator)[0].key}"
                }
            )

        if settings.DEBUG:
            # Allow the container to communicate with the dev environment
            env.update({"GRAND_CHALLENGE_UNSAFE": "True"})

        return env

    @property
    def service(self):
        return Service(
            job_id=self.pk,
            job_model=f"{self._meta.app_label}-{self._meta.model_name}",
            exec_image=self.workstation_image.image,
            exec_image_sha256=self.workstation_image.image_sha256,
        )

    @property
    def workstation_url(self):
        return urljoin(
            self.get_absolute_url(), self.workstation_image.initial_path
        )

    def start(self):
        try:
            self.service.start(
                http_port=self.workstation_image.http_port,
                websocket_port=self.workstation_image.websocket_port,
                hostname=self.hostname,
                environment=self.environment,
            )
            self.update_status(status=self.STARTED)
        except RuntimeError:
            self.update_status(status=self.FAILED)

    def stop(self):
        self.service.stop_and_cleanup()
        self.update_status(status=self.STOPPED)

    def update_status(self, *, status: STATUS_CHOICES):
        self.status = status
        self.save()

    def get_absolute_url(self):
        return reverse(
            "workstations:session-detail",
            kwargs={
                "slug": self.workstation_image.workstation.slug,
                "pk": self.pk,
            },
        )

    def save(self, *args, **kwargs):
        created = self._state.adding

        super().save(*args, **kwargs)

        if created:
            start_service.apply_async(kwargs=self.task_kwargs)
        elif self.user_finished and self.status != self.STOPPED:
            stop_service.apply_async(kwargs=self.task_kwargs)