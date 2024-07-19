from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.models import Group


class GroupRequiredMixin(AccessMixin):
    group_required = None

    def dispatch(self, request, *args, **kwargs):
        if self.group_required:
            if isinstance(self.group_required, str):
                self.group_required = [self.group_required]
            user_groups = request.user.groups.values_list("name", flat=True)
            if not any(group in user_groups for group in self.group_required):
                return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
