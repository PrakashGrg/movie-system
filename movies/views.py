from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Movie, Favorite

def home(request):
    movies = Movie.objects.annotate(
        favorites_count=Count('favorite')
    )
    
    if request.user.is_authenticated:
        movies = movies.annotate(
            is_favorite=Count('favorite', filter=Q(favorite__user=request.user))
        )
    
    return render(request, 'movies/home.html', {'movies': movies})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'movies/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'movies/login.html', {'form': form})

@login_required
def dashboard(request):
    total_movies = Movie.objects.count()
    user_favorites_count = Favorite.objects.filter(user=request.user).count()
    user_comments_count = 0
    favorites = Movie.objects.filter(favorite__user=request.user)[:6]
    return render(request, 'movies/dashboard.html', {
        'total_movies': total_movies,
        'user_favorites_count': user_favorites_count,
        'user_comments_count': user_comments_count,
        'favorites': favorites
    })

@login_required
def toggle_favorite(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        movie=movie
    )
    if not created:
        favorite.delete()
    return redirect('home')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')



