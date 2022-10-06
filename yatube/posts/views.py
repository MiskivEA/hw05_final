from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow

DISPLAY_POST = 10


def get_page_objects(request, page_objects, display_post):
    paginator = Paginator(page_objects, display_post)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20)
def index(request):
    posts = Post.objects.all()
    page_obj = get_page_objects(request, posts, DISPLAY_POST)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    page_obj = get_page_objects(request, posts, DISPLAY_POST)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    all_user_posts = author.posts.all()
    page_obj = get_page_objects(request, all_user_posts, DISPLAY_POST)
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(
            user=request.user,
            author=author
        ).exists():
            following = True
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {'post': post, 'form': form, 'comments': comments}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form_post = PostForm(request.POST, files=request.FILES)
        if form_post.is_valid():
            form = form_post.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('posts:profile', request.user.username)
        context = {'form': form_post}
        return render(request, template, context)

    context = {'form': PostForm()}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author.username != request.user.username:
        return redirect('posts:posts', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:posts', post_id)

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:posts', post_id)


@login_required
def profile_index(request):
    user = request.user
    subscribes = user.follower.all()
    all_posts_subs = []
    for item in subscribes:
        all_posts_subs += item.author.posts.all()
    page_obj = get_page_objects(request, all_posts_subs, DISPLAY_POST)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username_follow):
    user = request.user
    author = get_object_or_404(User, username=username_follow)
    if not Follow.objects.filter(
        user=user,
        author=author
    ).exists() and user != author:
        Follow.objects.create(
            user=user,
            author=author
        )
    return redirect('posts:profile', username_follow)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(
            user=user,
            author=author
    ).exists():
        Follow.objects.get(
            user=user,
            author=author
        ).delete()
    return redirect('posts:profile', username)


