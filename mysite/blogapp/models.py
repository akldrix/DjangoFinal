from django.db import models
from django.urls import reverse


class Author(models.Model):
    name = models.CharField(max_length=100, null=False)
    bio = models.TextField(null=False, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=40, null=False)


class Tag(models.Model):
    name = models.CharField(max_length=20, null=False)


class Article(models.Model):
    title = models.CharField(max_length=200, null=False)
    content = models.TextField(null=False)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="articles", null=True, blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="articles",
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(Tag, related_name="articles", blank=True)

    def get_absolute_url(self):
        return reverse("blogapp:article", kwargs={"pk": self.pk})
