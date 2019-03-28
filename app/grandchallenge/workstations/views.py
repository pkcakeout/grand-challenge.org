from django.views.generic import ListView, CreateView, DetailView, UpdateView

from grandchallenge.core.permissions.mixins import UserIsStaffMixin
from grandchallenge.workstations.forms import (
    WorkstationForm,
    WorkstationImageForm,
)
from grandchallenge.workstations.models import (
    Workstation,
    WorkstationImage,
    Session,
)


class WorkstationList(UserIsStaffMixin, ListView):
    model = Workstation


class WorkstationCreate(UserIsStaffMixin, CreateView):
    model = Workstation
    form_class = WorkstationForm


class WorkstationDetail(UserIsStaffMixin, DetailView):
    model = Workstation


class WorkstationUpdate(UserIsStaffMixin, UpdateView):
    model = Workstation
    form_class = WorkstationForm


class WorkstationImageCreate(UserIsStaffMixin, CreateView):
    model = WorkstationImage
    form_class = WorkstationImageForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.workstation = Workstation.objects.get(
            slug=self.kwargs["slug"]
        )

        uploaded_file = form.cleaned_data["chunked_upload"][0]
        form.instance.staged_image_uuid = uploaded_file.uuid

        return super().form_valid(form)


class WorkstationImageDetail(UserIsStaffMixin, DetailView):
    model = WorkstationImage


class SessionCreate(UserIsStaffMixin, CreateView):
    model = Session
    fields = []

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.workstation = Workstation.objects.get(
            slug=self.kwargs["slug"]
        )
        return super().form_valid(form)


class SessionDetail(UserIsStaffMixin, DetailView):
    model = Session