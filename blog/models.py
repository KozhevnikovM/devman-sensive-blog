from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class PostQuerySet(models.QuerySet):
    """Custom QuerySet for Post Model"""

    def popular(self):
        """Order posts by likes count"""
        return self.annotate(models.Count("likes", distinct=True)) \
            .order_by("-likes__count")

    def fetch_with_comments_count(self):
        """Fetch posts comments count"""
        post_ids = [post.id for post in self]
        posts_with_comments = Post.objects.filter(id__in=post_ids) \
            .annotate(models.Count("comments", distinct=True))

        id_to_comments = dict(
            posts_with_comments.values_list("id", "comments__count"))

        for post in self:
            post.comments_count = id_to_comments[post.id]

        return self

    def fetch_with_tags_count(self):
        """Fetch posts tags count"""
        prefetch_tags = models.Prefetch(
            "tags",
            queryset=Tag.objects.popular()
        )
        return self.prefetch_related(prefetch_tags)


class Post(models.Model):
    """Post model"""

    title = models.CharField("Заголовок", max_length=200)
    text = models.TextField("Текст")
    slug = models.SlugField("Название в виде url", max_length=200)
    image = models.ImageField("Картинка")
    published_at = models.DateTimeField("Дата и время публикации")

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        limit_choices_to={"is_staff": True})
    likes = models.ManyToManyField(
        User,
        related_name="liked_posts",
        verbose_name="Кто лайкнул",
        blank=True)
    tags = models.ManyToManyField(
        "Tag",
        related_name="posts",
        verbose_name="Теги")

    objects = PostQuerySet.as_manager()

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        """Get absolute url for post"""

        return reverse("post_detail", args={"slug": self.slug})

    class Meta:
        """Custom Post Meta"""
        ordering = ["-published_at"]
        verbose_name = "пост"
        verbose_name_plural = "посты"


class TagQuerySet(models.QuerySet):
    """Custom Tag QuerySet"""

    def popular(self):
        """Sort tags by popularity"""

        return self.annotate(models.Count("posts")).order_by("-posts__count")


class Tag(models.Model):
    """Tag model"""
    title = models.CharField("Тег", max_length=20, unique=True)

    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        """Get absolute tag url"""
        return reverse("tag_filter", args={"tag_title": self.slug})

    class Meta:
        """Custom Tag Meta"""

        ordering = ["title"]
        verbose_name = "тег"
        verbose_name_plural = "теги"


class Comment(models.Model):
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        verbose_name="Пост, к которому написан",
        related_name="comments")

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор")

    text = models.TextField("Текст комментария")
    published_at = models.DateTimeField("Дата и время публикации")

    def __str__(self):
        return f"{self.author.username} under {self.post.title}"

    class Meta:
        """Custom Meta for Comment"""
        ordering = ["published_at"]
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"
