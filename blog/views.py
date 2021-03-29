from django.shortcuts import render

from blog.models import Post, Tag


def serialize_post(post, with_comments=False):
    """Post serializer"""

    serialized = {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.first().title,
    }

    if with_comments:
        serialized['comments_amount'] = post.comments_count

    return serialized

def serialize_tag(tag):
    """tag serializer"""

    return {
        'title': tag.title,
        'posts_with_tag': tag.posts__count,
    }


def index(request):
    """render index page"""

    popular_posts = Post.objects \
        .fetch_with_tags_count() \
        .prefetch_related('author') \
        .popular()

    most_popular_posts = popular_posts[:5]

    most_fresh_posts = popular_posts.order_by('-published_at')[:5] \
        .fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post, True) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }

    return render(request, 'index.html', context)


def post_detail(request, slug):
    """render post page"""

    popular_posts = Post.objects \
        .fetch_with_tags_count() \
        .prefetch_related('author') \
        .popular()

    current_post = popular_posts.get(slug=slug)

    comments = current_post.comments.all() \
        .prefetch_related('author')

    popular_tags = Tag.objects.popular()
    most_popular_tags = popular_tags[:5]
    most_popular_posts = popular_posts.popular()[:5]
    related_tags = current_post.tags.all()

    serialized_comments = [
        {
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        } for comment in comments
    ]

    serialized_post = {
        "title": current_post.title,
        "text": current_post.text,
        "author": current_post.author.username,
        "comments": serialized_comments,
        'likes_amount': current_post.likes__count,
        "image_url": current_post.image.url if current_post.image else None,
        "published_at": current_post.published_at,
        "slug": current_post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(current_post) for current_post in most_popular_posts],
    }

    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    """render tag page"""

    popular_posts = Post.objects \
        .fetch_with_tags_count() \
        .prefetch_related('author') \
        .popular()

    tag = Tag.objects \
        .get(title=tag_title)

    popular_tags = Tag.objects.popular()
    most_popular_tags = popular_tags[:5]

    most_popular_posts = popular_posts[:5]

    related_posts = popular_posts.filter(tags=tag) \
        .order_by('-published_at')[:20] \
        .fetch_with_comments_count()

    context = {
        "tag": tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post, True) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }

    return render(request, 'posts-list.html', context)


def contacts(request):
    """render contacts page
    позже здесь будет код для статистики заходов на эту страницу
    и для записи фидбека
    """
    
    return render(request, 'contacts.html', {})
