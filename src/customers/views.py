from django.views.decorators.http import require_POST
from django.urls.base import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.utils.module_loading import import_string
from django.template.loader import render_to_string
from django.http import HttpResponse

from customers.forms import (
    CreateCustomerForm,
    NotificationGroupFormSet,
    UpdateCustomerForm,
)
from customers.models import Customer


def assign_class(formset):
    formset.formset_class = (
        f"{formset.__class__.__bases__[0].__module__}.{formset.__class__.__name__}"
    )

    for form in formset.forms:
        if hasattr(form, "nested"):
            for nested in form.nested:
                assign_class(nested)

    if hasattr(formset.empty_form, "nested"):
        for nested in formset.empty_form.nested:
            assign_class(nested)


class CustomerCreateView(CreateView):
    model = Customer
    template_name = "customers/customer_create.html"
    form_class = CreateCustomerForm
    success_url = reverse_lazy("customers:customer_create")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        notification_group_formset = NotificationGroupFormSet(
            self.request.POST or None,
            prefix="notification_group_formset",
        )
        assign_class(notification_group_formset)

        context["formsets"] = (notification_group_formset,)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        notification_group_formset = NotificationGroupFormSet(
            self.request.POST,
            instance=self.object,
            prefix="notification_group_formset",
        )

        if notification_group_formset.is_valid():
            notification_group_formset.save()

        return response


class CustomerUpdateView(UpdateView):
    model = Customer
    template_name = "customers/customer_update.html"
    form_class = UpdateCustomerForm
    success_url = reverse_lazy("customers:customer_create")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        notification_group_formset = NotificationGroupFormSet(
            self.request.POST or None,
            instance=self.object,
            prefix="notification_group_formset",
        )
        assign_class(notification_group_formset)

        context["formsets"] = (notification_group_formset,)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        notification_group_formset = NotificationGroupFormSet(
            self.request.POST,
            instance=self.object,
            prefix="notification_group_formset",
        )

        if notification_group_formset.is_valid():
            notification_group_formset.save()

        return response

    def get_initial(self):
        initial = super().get_initial()

        initial["email"] = self.object.user.email

        return initial


@require_POST
def add_form(request):
    class_path = request.POST.get("formset_class")
    prefix = request.POST.get("formset_prefix")
    total_forms = int(request.POST.get(f"{prefix}-TOTAL_FORMS", 0))

    FormSetClass = import_string(class_path)
    formset = FormSetClass(prefix=prefix)
    empty_form = formset.empty_form

    if hasattr(empty_form, "nested"):
        for nested_fs in empty_form.nested:
            assign_class(nested_fs)

    form_html = render_to_string(
        "customers/partials/form.html", {"form": empty_form}, request=request
    )
    form_html = form_html.replace("__prefix__", str(total_forms))

    return HttpResponse(form_html)
