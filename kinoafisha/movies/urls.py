from django.urls import path
from . import views
from .views import MovieBrowserView  # <--- добавьте этот импорт

urlpatterns = [
    path('', views.index, name='index'),
    path('favorite/add/<int:movie_id>/', views.add_favorite, name='add_favorite'),
    path('favorite/remove/<int:movie_id>/', views.remove_favorite, name='remove_favorite'),
    path('browse/', MovieBrowserView.as_view(), name='movie_browser'),
    path('movie/<int:movie_id>/hide/', views.hide_movie, name='hide_movie'),
    path('movie/<int:movie_id>/report/', views.report_movie, name='report_movie'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('sessions/', views.sessions_stub, name='sessions_list'),
    path('search/', views.movie_search, name='movie_search'),
    path('hidden/', views.HiddenMoviesView.as_view(), name='hidden_movies'),
    path('hidden/unhide/<int:movie_id>/', views.unhide_movie, name='unhide_movie'),

]

