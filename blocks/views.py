from django.shortcuts import render
from django.http import HttpResponse, Http404
from blocks.models import BlockRow, Transaction

# Create your views here.

def blocks(request):
    
    blocks = BlockRow.objects.all()
    print(blocks)
    return blocks

def transactions(request):
    
    txns = Transaction.objects.all()
    return txns
