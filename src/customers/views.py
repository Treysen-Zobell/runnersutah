from django.urls.base import reverse_lazy
from django.views.generic.edit import CreateView

from customers.forms import CreateCustomerForm, NotificationGroupFormSet, EmailFormSet
from customers.models import Customer, NotificationGroup


class CustomerCreateView(CreateView):
    model = Customer
    template_name = "customers/customer_create.html"
    form_class = CreateCustomerForm
    success_url = reverse_lazy("customers:customer_create")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["notification_group_formset"] = NotificationGroupFormSet(
                self.request.POST,
                prefix="notification_group_form",
            )
        else:
            context["notification_group_formset"] = NotificationGroupFormSet(
                queryset=NotificationGroup.objects.none(),
                prefix="notification_group_form",
            )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        customer = Customer.objects.create(
            user=self.object,
            display_name=form.cleaned_data["display_name"],
            phone_number=form.cleaned_data["phone_number"],
            products=form.cleaned_data["products"],
        )

        notification_group_formset = NotificationGroupFormSet(
            self.request.POST,
            prefix="notification_group_form",
            instance=customer,
        )
        if notification_group_formset.is_valid():
            for notification_group_form in notification_group_formset:
                if notification_group_form.cleaned_data.get("DELETE"):
                    continue
                notification_group = notification_group_form.save()

                email_formset = EmailFormSet(
                    self.request.POST,
                    prefix=f"{notification_group.prefix}-{EmailFormSet.get_default_prefix()}",
                )
                if email_formset.is_valid():
                    for email_form in email_formset:
                        if email_form.cleaned_data.get("DELETE"):
                            continue
                        email_form.save()

        return response
