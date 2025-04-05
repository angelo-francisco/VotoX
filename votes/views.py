from django.shortcuts import render


def home_page(request):
    return render(request, 'votes/home_page.html')
