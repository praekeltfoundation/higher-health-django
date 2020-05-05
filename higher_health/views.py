from .forms import CheckerForm
from django.shortcuts import render

def index(request):
	return render(request, 'base.html')

def form_new(request):
    form = CheckerForm()
    return render(request, 'form_edit.html', {'form': form})
