from .forms import SimpleForm
from django.shortcuts import render

def index(request):
	return render(request, 'base.html')

def form_new(request):
    form = SimpleForm()
    return render(request, 'form_edit.html', {'form': form})
