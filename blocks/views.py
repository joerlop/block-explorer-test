from django.shortcuts import render
from django.http import HttpResponse, Http404
from blocks.models import BlockRow, Transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def blocks(request):
    blocks_list = BlockRow.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(blocks_list, 10)

    try:
        blocks = paginator.page(page)
    except PageNotAnInteger:
        blocks = paginator.page(1)
    except EmptyPage:
        blocks = paginator.page(paginator.num_pages)
    return blocks

def transactions(request):
    
    txns = Transaction.objects.all()
    return txns
