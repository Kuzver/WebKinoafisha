from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField("Название", max_length=255)
    genre = models.CharField("Жанр", max_length=100)
    duration = models.PositiveIntegerField("Длительность (мин)")
    director = models.CharField("Режиссёр", max_length=255)
    actors = models.TextField("Актёры")
    release_date = models.DateField("Дата выпуска", null=True, blank=True)
    age_limit = models.CharField("Возрастное ограничение", max_length=10)
    description = models.TextField("Описание")
    rating = models.FloatField("Рейтинг", null=True, blank=True)
    poster = models.ImageField("Постер", null=True, blank=True, upload_to="posters/")

    def display_rating(self):
        return f"{self.rating:.1f}" if self.rating is not None else "Нет оценки"

    display_rating.short_description = "Рейтинг"

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def release_year(self):
        return self.release_date.year if self.release_date else "—"

    release_year.short_description = "Год выпуска"

    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else '—'})"


class Cinema(models.Model):
    name = models.CharField("Название", max_length=255)
    address = models.CharField("Адрес", max_length=255)
    hall_count = models.PositiveIntegerField("Количество залов")
    contacts = models.TextField("Контактная информация")

    class Meta:
        verbose_name = "Кинотеатр"
        verbose_name_plural = "Кинотеатры"

    def __str__(self):
        return self.name


class Hall(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, verbose_name="Кинотеатр")
    name = models.CharField("Название/номер зала", max_length=50)
    capacity = models.PositiveIntegerField("Вместимость")

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"

    def __str__(self):
        return f"{self.name} ({self.cinema.name})"


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Фильм")
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, verbose_name="Зал")
    datetime = models.DateTimeField("Дата и время")
    price = models.DecimalField("Стоимость билета", max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = "Сеанс"
        verbose_name_plural = "Сеансы"

    def __str__(self):
        return f"{self.movie.title} - {self.datetime} ({self.hall})"


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('free', 'Свободен'),
        ('reserved', 'Забронирован'),
        ('sold', 'Куплен'),
    ]
    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name="Сеанс")
    seat_number = models.CharField("Место", max_length=10)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default='free')

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"

    def __str__(self):
        return f"{self.session} - Место {self.seat_number}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('cancelled', 'Отменено'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name="Билет")
    reserved_at = models.DateTimeField("Дата бронирования", auto_now_add=True)
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"{self.user} - {self.ticket}"

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

from django.contrib.auth.models import User

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

class HiddenMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Фильм")
    hidden_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата скрытия")

    class Meta:
        unique_together = ('user', 'movie')
        verbose_name = "Скрытый фильм"
        verbose_name_plural = "Скрытые фильмы"

    def __str__(self):
        return f"{self.user.username} скрыл {self.movie.title}"

class MovieReport(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Фильм")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    reason = models.TextField("Причина жалобы")
    reported_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата жалобы")

    class Meta:
        verbose_name = "Жалоба на фильм"
        verbose_name_plural = "Жалобы на фильмы"

    def __str__(self):
        return f"{self.user.username} пожаловался на {self.movie.title}"

