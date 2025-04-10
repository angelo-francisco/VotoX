from django.shortcuts import render


def home_page(request):
    return render(request, 'votes/home_page.html')


def pollings(request):
    return render(request, 'votes/pollings.html')