from django.shortcuts import render
from .models import Post

def home(request):
    context = {
        'posts': Post.objects.all()
}
    return render(request, 'blog/home.html', context)

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def login(request):
    return render(request, 'blog/login.html')

def register(request):
    return render(request, 'blog/register.html')

def instructor(request):
    return render(request, 'blog/instructor.html')

def parent(request):
    return render(request, 'blog/parent.html')

def student(request):
    return render(request, 'blog/student.html')


