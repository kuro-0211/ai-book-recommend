import logging

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import Book, Recommendation
from .ollama_client import recommend_books

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def index(request):
    if request.method == "GET":
        return render(request, "recommender/index.html")

    keyword = (request.POST.get("keyword") or "").strip()
    if not keyword:
        return render(
            request,
            "recommender/index.html",
            {"error": "키워드 또는 기분을 입력해 주세요."},
        )

    try:
        books, raw = recommend_books(keyword)
    except Exception as exc:
        logger.exception("Ollama call failed")
        return render(
            request,
            "recommender/index.html",
            {
                "error": f"AI 추천 호출 중 오류가 발생했습니다: {exc}",
                "keyword": keyword,
            },
        )

    rec = Recommendation.objects.create(
        keyword=keyword,
        raw_response=raw,
        user=request.user if request.user.is_authenticated else None,
    )
    if books:
        Book.objects.bulk_create([
            Book(
                recommendation=rec,
                title=b["title"],
                author=b["author"],
                summary=b["summary"],
                reason=b["reason"],
                position=i,
            )
            for i, b in enumerate(books)
        ])

    return render(
        request,
        "recommender/result.html",
        {"keyword": keyword, "books": books, "raw": raw if not books else ""},
    )


@login_required
def my_history(request):
    """로그인한 사용자 본인의 추천 기록만 표시."""
    recs = (
        Recommendation.objects
        .filter(user=request.user)
        .prefetch_related("books")
        .order_by("-created_at")[:50]
    )
    return render(request, "recommender/my_history.html", {"recs": recs})


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
