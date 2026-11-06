from typing import override

from django.contrib.syndication.views import Feed
from django.db.models import QuerySet
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView

from .models import Article


class ViewArticle(ListView):
    model = Article
    template_name = "article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        return (
            Article.objects.select_related("author", "category")
            .prefetch_related("tags")
            .defer("content")
            .all()
        )


class ArticleDetailView(DetailView):
    model = Article


class LatestArticleFeed(Feed):
    title = "Blog Articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:articles")

    def items(self) -> QuerySet[Article]:
        return Article.objects.filter(pub_date__isnull=False).order_by("-pub_date")[:5]

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]
