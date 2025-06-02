from django.contrib import admin
from .models import Movie, Cinema, Hall, Session, Ticket, Reservation
from django.contrib.admin import SimpleListFilter
from datetime import datetime

# Встроенные классы (inlines)
class HallInline(admin.TabularInline):
    model = Hall
    extra = 0

class SessionInline(admin.TabularInline):
    model = Session
    extra = 0

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0

class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 0

class ReleaseYearFilter(SimpleListFilter):
    title = 'Год выпуска'
    parameter_name = 'release_year'

    def lookups(self, request, model_admin):
        years = Movie.objects.values_list('release_date__year', flat=True).distinct()
        years = sorted(set(filter(None, years)))
        return [(year, year) for year in years]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(release_date__year=value)
        return queryset

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", ReleaseYearFilter, "age_limit")
    search_fields = ("title", "genre", "director")
    list_filter = ("genre", ReleaseYearFilter, "age_limit")
    readonly_fields = ("rating",)
    fieldsets = (
        (None, {"fields": ("title", "genre", "duration", "director", "actors", ReleaseYearFilter, "age_limit")}),
        ("Описание", {"fields": ("description", "poster")}),
        ("Дополнительно", {"fields": ("rating",)}),
    )

    @admin.display(description="Рейтинг")
    def display_rating(self, obj):
        return f"{obj.rating:.1f}"


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "hall_count")
    search_fields = ("name", "address")
    list_filter = ("hall_count",)
    inlines = [HallInline]


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "cinema", "capacity")
    search_fields = ("name", "cinema__name")
    list_filter = ("cinema",)
    raw_id_fields = ("cinema",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("movie", "hall", "datetime", "price", "cinema_name")
    list_filter = ("movie", "hall__cinema", "datetime")
    date_hierarchy = "datetime"
    search_fields = ("movie__title",)
    inlines = [TicketInline]

    @admin.display(description="Кинотеатр")
    def cinema_name(self, obj):
        return obj.hall.cinema.name


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("session", "seat_number", "status", "user")
    list_filter = ("status", "session")
    search_fields = ("seat_number", "user__username", "session__movie__title")
    raw_id_fields = ("session", "user")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("user", "ticket", "reserved_at", "status")
    list_filter = ("status", "reserved_at")
    date_hierarchy = "reserved_at"
    search_fields = ("user__username", "ticket__session__movie__title")
    raw_id_fields = ("ticket", "user")
    readonly_fields = ("reserved_at",)
