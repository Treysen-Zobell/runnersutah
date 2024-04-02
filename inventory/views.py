from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'inventory/index.html', {})


def detail(request):
    return HttpResponse("Hello, world. You're at the inventory detail.")
