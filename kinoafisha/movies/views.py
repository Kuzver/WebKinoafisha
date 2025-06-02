from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.db.models import Count, Avg, Q
from django.http import HttpResponse
import datetime
from .models import Movie, Review, Session, Favorite, HiddenMovie, MovieReport


def index(request):
    today = datetime.date.today().isoformat()
    query = request.GET.get('q', '')

    now = timezone.now()
    current_year = now.year
    one_month_ago = (now - timedelta(days=30)).date()
    in_60_days = (now + timedelta(days=60)).date()

    # Поиск
    search_results = Movie.objects.filter(title__icontains=query) if query else None

    # Популярные фильмы
    popular_movies = Movie.objects.annotate(
        avg_rating=Avg('review__rating'),
        session_count=Count('session', filter=Q(session__datetime__gte=now))
    ).filter(avg_rating__gte=3.5).order_by('-avg_rating')[:10]

    # Предстоящие релизы (по году >= текущего)
    upcoming_releases = Movie.objects.filter(
        release_date__year__gte=current_year
    ).order_by('release_date')[:10]

    # Ближайшие сеансы
    upcoming_sessions = Session.objects.filter(datetime__gte=now).order_by('datetime')[:10]

    # Последние рецензии
    latest_reviews = Review.objects.select_related('movie').order_by('-id')[:10]

    # Новинки за последний месяц (условие можно уточнить при наличии поля release_date)
    new_releases = Movie.objects.filter(
        release_date__gte=one_month_ago
    ).order_by('-release_date')[:10]

    # Топ премьер (в ближайшие 60 дней) с рейтингом
    top_movies = Movie.objects.annotate(
        avg_rating=Avg('review__rating'),
        session_count=Count('session', filter=Q(session__datetime__gte=now))
    ).filter(avg_rating__gte=3.5).order_by('-avg_rating')[:10]

    # Избранное пользователя
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = request.user.favorites.values_list('movie_id', flat=True)

    context = {
        'popular_movies': popular_movies,
        'upcoming_releases': upcoming_releases,
        'upcoming_sessions': upcoming_sessions,
        'latest_reviews': latest_reviews,
        'search_results': search_results,
        'new_releases': new_releases,
        'query': query,
        'results': search_results or [],
        'upcoming_movies': upcoming_releases,
        'top_movies': top_movies,
        'user_favorites': user_favorites,
    }

    return render(request, 'movies/index.html', context)


def search(request):
    query = request.GET.get('q', '')
    results = Movie.objects.filter(title__icontains=query) if query else []
    return render(request, 'search_results.html', {'results': results, 'query': query})


def top_releases_widget(request):
    now = timezone.now()
    two_months_later = now + timedelta(days=60)

    top_movies = Movie.objects.filter(
        release_date__gt=now,
        release_date__lte=two_months_later
    ).order_by('release_date')[:5]

    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(user=request.user).values_list('movie_id', flat=True)

    return render(request, 'widgets/top_releases.html', {
        'top_movies': top_movies,
        'user_favorites': user_favorites,
    })


@method_decorator(login_required, name='dispatch')
class MovieBrowserView(ListView):
    model = Movie
    template_name = 'movies/movie_browser.html'
    context_object_name = 'movies'

    def get_queryset(self):
        hidden = HiddenMovie.objects.filter(user=self.request.user).values_list('movie_id', flat=True)
        return Movie.objects.exclude(id__in=hidden)


@require_POST
@login_required
def hide_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    HiddenMovie.objects.get_or_create(user=request.user, movie=movie)
    return redirect('movie_browser')


@require_POST
@login_required
def report_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    reason = request.POST.get('reason')
    if reason:
        MovieReport.objects.create(user=request.user, movie=movie, reason=reason)
    return redirect('movie_browser')


@login_required
def add_favorite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    request.user.profile.favorites.add(movie)
    return redirect('movie_detail', movie_id=movie.id)


@login_required
def remove_favorite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    request.user.profile.favorites.remove(movie)
    return redirect('favorites')


def sessions_stub(request):
    return HttpResponse("Страница сеансов в разработке.")


def movie_search(request):
    query = request.GET.get('q', '')
    results = Movie.objects.filter(title__icontains=query) if query else []
    return render(request, 'movies/index.html', {
        'query': query,
        'results': results,
    })

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movies/movie_detail.html', {'movie': movie})

@method_decorator(login_required, name='dispatch')
class HiddenMoviesView(ListView):
    model = Movie
    template_name = 'movies/hidden_movies.html'
    context_object_name = 'movies'

    def get_queryset(self):
        hidden = HiddenMovie.objects.filter(user=self.request.user).values_list('movie_id', flat=True)
        return Movie.objects.filter(id__in=hidden)

@require_POST
@login_required
def unhide_movie(request, movie_id):
    hidden_entry = HiddenMovie.objects.filter(user=request.user, movie_id=movie_id)
    if hidden_entry.exists():
        hidden_entry.delete()
    return redirect('hidden_movies')

from django.contrib import messages

@require_POST
@login_required
def report_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    reason = request.POST.get('reason')
    if reason:
        MovieReport.objects.create(user=request.user, movie=movie, reason=reason)
        messages.success(request, "Жалоба успешно отправлена.")
    else:
        messages.error(request, "Пожалуйста, укажите причину жалобы.")
    return redirect('movie_browser')
