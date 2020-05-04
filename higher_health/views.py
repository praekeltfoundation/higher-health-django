from .forms import SimpleForm
from django.shortcuts import render

def form_new(request):
    form = SimpleForm()
    return render(request, 'form_edit.html', {'form': form})
