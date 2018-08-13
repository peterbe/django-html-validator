from django.shortcuts import render


def home_page(request):
    return render(request, 'index.html')


def not_valid(request):
    return render(request, 'not_valid.html')
