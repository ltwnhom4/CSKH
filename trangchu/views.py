from django.shortcuts import render

def home(request):
    return render(request, 'trangchu/index.html')

def lien_he(request):
    return render(request, 'trangchu/lienhe.html')


