from datetime import datetime
from typing import override

from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet

from .models import Article


class BlogSitemap(Sitemap):
    changefreq: str = "never"
    priority: float = 0.5

    @override
    def items(self) -> QuerySet[Article]:
        return Article.objects.order_by("-pub_date")

    def lastmod(self, obj: Article) -> datetime:
        return obj.pub_date
