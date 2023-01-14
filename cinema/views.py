from django.shortcuts import render

from .models import Theater

# Create your views here.

def home(request):
    if request.user.is_authenticated:
        theaters = Theater.objects.order_by('name')
    else:
        theaters = Theater.objects.filter(is_active=True).order_by('name')

    for theater in theaters:
        theater.screens = theater.get_screens(request.user.is_authenticated)
        for screen in theater.screens:
            screen.total_seats_available = screen.get_total_seats_available()

    context = {'theaters': theaters}
    return render(request, 'cinema/home.html', context)
