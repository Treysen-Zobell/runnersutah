from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.models import (
    inlineformset_factory,
    BaseInlineFormSet,
)
from django.utils.translation import gettext_lazy as _

from customers.models import Customer, NotificationGroup, Email
from products.models import Product


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

    for formset in form.nested:
        non_deleted_forms = set(formset.forms).difference(set(formset.deleted_forms))
        for nested_form in non_deleted_forms:
            if not is_empty_form(nested_form):
                return True

    return False


class EmailFormSetBase(BaseInlineFormSet):
    pass


EmailFormSet = inlineformset_factory(
    NotificationGroup,
    Email,
    formset=EmailFormSetBase,
    fields=("address",),
    extra=0,
)


class NotificationGroupWithEmailsFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        email_formset = EmailFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix=f"{form.prefix}-{EmailFormSet.get_default_prefix()}",
        )
        form.nested = (email_formset,)

    def is_valid(self):
        result = super().is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, "nested"):
                    result = result and all(f.is_valid() for f in form.nested)
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
        result = []

        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                if form.instance.pk and commit:
                    form.instance.delete()
                continue

            instance = form.save(commit=commit)
            result.append(instance)

            if hasattr(form, "nested") and not is_adding_nested_inlines_to_empty_form(
                form
            ):
                for formset in form.nested:
                    formset.save(commit=commit)

        return result


NotificationGroupFormSet = inlineformset_factory(
    Customer,
    NotificationGroup,
    formset=NotificationGroupWithEmailsFormSet,
    fields=("name",),
    extra=0,
)


class CreateCustomerForm(UserCreationForm):
    display_name = forms.CharField(max_length=250)
    phone_number = forms.CharField(max_length=250, required=False)
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
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

    def save(self, commit=True):
        user = super().save(commit=commit)

        customer = Customer.objects.create(
            user=user,
            display_name=self.cleaned_data.get("display_name"),
            phone_number=self.cleaned_data.get("phone_number", ""),
        )
        customer.products.set(self.cleaned_data.get("products", []))

        return customer


class UpdateCustomerForm(forms.ModelForm):
    display_name = forms.CharField(max_length=250)
    phone_number = forms.CharField(max_length=250, required=False)
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Customer
        fields = [
            "display_name",
            "phone_number",
            "products",
            "email",
        ]

    def save(self, commit=True):
        customer = super().save(commit=False)

        user = customer.user
        user.email = self.cleaned_data.get("email")
        user.save(commit=commit)

        customer.display_name = self.cleaned_data.get("display_name")
        customer.phone_number = self.cleaned_data.get("phone_number", "")
        if commit:
            customer.save()
            customer.products.set(self.cleaned_data.get("products", []))
        return customer
