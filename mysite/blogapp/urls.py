from django.urls import path

from .views import ArticleDetailView, ViewArticle, LatestArticleFeed

app_name = "blogapp"

urlpatterns = [
    path("articles/", ViewArticle.as_view(), name="articles"),
    path("article/<int:pk>/", ArticleDetailView.as_view(), name="article"),
    path("articles/latest/feed/", LatestArticleFeed(), name="articles-feed"),
]
