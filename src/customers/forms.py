from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.models import (
    inlineformset_factory,
    BaseInlineFormSet,
)
from django.utils.translation import gettext_lazy as _

from customers.models import Customer, NotificationGroup, Email
from products.models import Product, ProductTemplate


def is_empty_form(form):
    return form.is_valid() and not form.cleaned_data


def is_form_persisted(form):
    return bool(getattr(form.instance, "pk", None))


def is_adding_nested_inlines_to_empty_form(form):
    if (
        not hasattr(form, "nested")
        or is_form_persisted(form)
        or not is_empty_form(form)
    ):
        return False

    non_deleted_forms = set(form.nested.forms).difference(
        set(form.nested.deleted_forms)
    )
    return any(not is_empty_form(nested_form) for nested_form in non_deleted_forms)


EmailFormSet = inlineformset_factory(
    NotificationGroup,
    Email,
    fields=("address",),
    extra=2,
)


class NotificationGroupWithEmailsFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        form.nested = EmailFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix=f"{form.prefix}-{EmailFormSet.get_default_prefix()}",
        )
        form.empty_nested = form.nested.empty_form

    def is_valid(self):
        result = super().is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, "nested"):
                    result = result and form.nested.is_valid()
        return result

    def clean(self):
        super().clean()
        for form in self.forms:
            if not hasattr(form, "nested") or form.cleaned_data.get("DELETE"):
                continue
            if is_adding_nested_inlines_to_empty_form(form):
                form.add_error(
                    field=None,
                    error=_(
                        "You are trying to add emails to a group which does not exist, please add information about"
                        "the group and add the emails again."
                    ),
                )

    def save(self, commit=True):
        result = super().save(commit=commit)
        for form in self.forms:
            if hasattr(form, "nested") and not is_adding_nested_inlines_to_empty_form(
                form
            ):
                form.nested.save(commit=commit)
        return result


NotificationGroupFormSet = inlineformset_factory(
    Customer,
    NotificationGroup,
    formset=NotificationGroupWithEmailsFormSet,
    fields=("name", "templates"),
    extra=2,
)


class CreateCustomerForm(UserCreationForm):
    display_name = forms.CharField(max_length=250)
    phone_number = forms.CharField(max_length=250, required=False)
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = get_user_model()
        fields = [
            "display_name",
            "phone_number",
            "products",
            "email",
            "username",
            "password1",
            "password2",
        ]
