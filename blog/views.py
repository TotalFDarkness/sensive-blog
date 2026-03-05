from django.shortcuts import render, get_object_or_404
from blog.models import Comment, Post, Tag
from django.db.models import Count, Prefetch, OuterRef, Subquery
from django.db.models import Q


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def serialize_post(post):
    tags = post.tags.all()
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count if hasattr(post, 'comments_count') else 0,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in tags],
        'first_tag_title': tags[0].title if tags else None,
    }


def index(request):
    most_popular_posts = Post.objects.popular()\
        .select_related('author')\
        .prefetch_related(
            Prefetch('tags', 
                    queryset=Tag.objects.annotate(posts_count=Count('posts')))
        )\
        .annotate(comments_count=Count('comments', distinct=True))[:5]

    most_fresh_posts = Post.objects\
        .select_related('author')\
        .prefetch_related(
            Prefetch('tags', 
                    queryset=Tag.objects.annotate(posts_count=Count('posts')))
        )\
        .annotate(comments_count=Count('comments', distinct=True))\
        .order_by('-published_at')[:5]

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects
        .select_related('author')
        .prefetch_related(
            Prefetch('tags', 
                    queryset=Tag.objects.annotate(posts_count=Count('posts'))),
            Prefetch('comments', 
                    queryset=Comment.objects
                    .select_related('author')
                    .order_by('published_at'))
        )
        .annotate(
            comments_count=Count('comments', distinct=True),
            likes_count=Count('likes', distinct=True)
        ),
        slug=slug
    )

    serialized_comments = [{
        'text': comment.text,
        'published_at': comment.published_at,
        'author': comment.author.username,
    } for comment in post.comments.all()]

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = Post.objects.popular()\
        .select_related('author')\
        .prefetch_related(
            Prefetch('tags', 
                    queryset=Tag.objects.annotate(posts_count=Count('posts')))
        )\
        .annotate(comments_count=Count('comments', distinct=True))[:5]

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(
        Tag.objects.annotate(posts_count=Count('posts')), 
        title=tag_title
    )

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = Post.objects.popular()\
        .select_related('author')\
        .prefetch_related(
            Prefetch('tags', 
                    queryset=Tag.objects.annotate(posts_count=Count('posts')))
        )\
        .annotate(comments_count=Count('comments', distinct=True))[:5]

    related_posts = Post.objects\
        .filter(tags=tag)\
        .popular()\
        .select_related('author')\
        .prefetch_related(
            Prefetch('tags', 
                    queryset=Tag.objects.annotate(posts_count=Count('posts')))
        )\
        .annotate(comments_count=Count('comments', distinct=True))[:5]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})