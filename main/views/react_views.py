from django.shortcuts import render

# Create your views here.
def react_app_view(request):
    return render(request, 'index.html')

