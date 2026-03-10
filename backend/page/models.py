from django.db import models


class Page(models.Model):
    """Página simple de contenido (pequeño CMS)."""

    slug = models.SlugField(max_length=200, unique=True)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, default="")
    is_public = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Página"
        verbose_name_plural = "Páginas"
        ordering = ["slug"]

    def __str__(self):
        return self.title or self.slug

