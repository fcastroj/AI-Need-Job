from django.shortcuts import render
from .models import Offer
# Create your views here.

def offer(request):
    offers = Offer.objects.all()
    return render(request, 'offer.html', {'offers': offers})