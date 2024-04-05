from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


@login_required
def index(request):
    return render(request, "inventory/index.html", {})


@login_required
def detail(request):
    return HttpResponse("Hello, world. You're at the inventory detail.")
