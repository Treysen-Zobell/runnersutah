from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static

register = template.Library()


@register.simple_tag(takes_context=True)
def sort_link(context, ordering, field_name, display_name, page_number):
    if ordering == f"-{field_name}":
        url = f"?ordering={field_name}&page={page_number}"
        img_src = static("resources/desc.png")
        img_alt = "Sort Descending"
    elif ordering == field_name:
        url = f"?ordering=-{field_name}&page={page_number}"
        img_src = static("resources/asc.png")
        img_alt = "Sort Ascending"
    else:
        url = f"?ordering={field_name}&page={page_number}"
        img_src = static("resources/neutral.png")
        img_alt = "Sort Other Column"

    html = f"""
        <a href="{url}">
        {display_name}<br>
        <img src="{img_src}" alt="{img_alt}">
        </a>
    """
    return mark_safe(html)
