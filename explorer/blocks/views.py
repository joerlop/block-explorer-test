from django.shortcuts import render
from django.http import HttpResponse, Http404
from blocks.models import BlockRow, Transaction

# Create your views here.

def blocks(request):
    
    blocks = BlockRow.objects.all()
    return render(request, "blocks.html", {"Blocks": blocks})

def transactions(request):
    
    txns = Transaction.objects.all()
    return render(request, "txns.html", {"Txns": txns})
