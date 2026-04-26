from django.contrib import admin

from .models import Book, Recommendation, WeeklyTopKeyword


class BookInline(admin.TabularInline):
    model = Book
    extra = 0


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "keyword", "created_at")
    list_filter = ("user",)
    search_fields = ("keyword", "user__username")
    inlines = [BookInline]


@admin.register(WeeklyTopKeyword)
class WeeklyTopKeywordAdmin(admin.ModelAdmin):
    list_display = ("week_start", "rank_no", "keyword", "hit_count")
    list_filter = ("week_start",)
