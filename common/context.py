def user_context(request):
    """
    Adds user group information to context to visibility of menus on page.
    :param request: HTTP Request
    :return: Additional context information
    """
    ctx = {}
    if request.user.groups.filter(name="admin").exists():
        ctx["is_admin"] = True
    if request.user.groups.filter(name="customer").exists():
        ctx["is_customer"] = True
        ctx["customer_id"] = request.user.id
    return ctx
