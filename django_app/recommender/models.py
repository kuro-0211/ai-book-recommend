from django.conf import settings
from django.db import models


class Recommendation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recommendations",
        null=True, blank=True,
    )
    keyword = models.CharField(max_length=255, db_index=True)
    raw_response = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.keyword} ({self.created_at:%Y-%m-%d %H:%M})"


class Book(models.Model):
    recommendation = models.ForeignKey(
        Recommendation, on_delete=models.CASCADE, related_name="books"
    )
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=255, blank=True, default="")
    summary = models.TextField(blank=True, default="")
    reason = models.TextField(blank=True, default="")
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.title


class WeeklyTopKeyword(models.Model):
    week_start = models.DateField()
    rank_no = models.IntegerField()
    keyword = models.CharField(max_length=255)
    hit_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("week_start", "rank_no")
        ordering = ["-week_start", "rank_no"]
