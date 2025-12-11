from django.views.decorators.http import require_POST
from django.urls.base import reverse_lazy
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView
from django.utils.module_loading import import_string
from django.template.loader import render_to_string
from django.http import HttpResponse

from customers.forms import CreateCustomerForm, NotificationGroupFormSet, EmailFormSet
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
            for notification_group_form in notification_group_formset:
                if notification_group_form.cleaned_data.get("DELETE"):
                    continue
                notification_group = notification_group_form.save()

                email_formset = EmailFormSet(
                    self.request.POST,
                    prefix=f"{notification_group_form.prefix}-{EmailFormSet.get_default_prefix()}",
                    instance=notification_group,
                )
                if email_formset.is_valid():
                    for email_form in email_formset:
                        if email_form.cleaned_data.get("DELETE"):
                            continue
                        email_form.save()

        return response


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
