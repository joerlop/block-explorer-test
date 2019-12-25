from django.shortcuts import render
from django.http import HttpResponse, Http404
from blocks.models import BlockRow

# Create your views here.

def blocks(request):
    
    blocks = BlockRow.objects.all()
    return render(request, "db.html", {"Blocks": blocks})
