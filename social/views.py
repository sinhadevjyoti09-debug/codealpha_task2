from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Post, Comment, Like, Follow, Profile
from .forms import RegisterForm, PostForm, CommentForm, ProfileForm


# ─── Authentication Views ────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'social/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'social/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


# ─── Feed & Post Views ───────────────────────────────────────────────

def index_view(request):
    posts = Post.objects.select_related('user', 'user__profile').prefetch_related('likes', 'comments').all()
    form = PostForm()

    # Track which posts the current user has liked
    liked_posts = set()
    if request.user.is_authenticated:
        liked_posts = set(
            Like.objects.filter(user=request.user).values_list('post_id', flat=True)
        )

    return render(request, 'social/index.html', {
        'posts': posts,
        'form': form,
        'liked_posts': liked_posts,
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created!')
    return redirect('index')


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('user', 'user__profile'), id=post_id)
    comments = post.comments.select_related('user', 'user__profile').all()
    comment_form = CommentForm()

    has_liked = False
    if request.user.is_authenticated:
        has_liked = Like.objects.filter(user=request.user, post=post).exists()

    return render(request, 'social/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'has_liked': has_liked,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added!')
    return redirect('post_detail', post_id=post.id)


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()  # Unlike
    # Redirect back to wherever the user came from
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'index'))
    return redirect(next_url)


# ─── Profile & Follow Views ──────────────────────────────────────────

def profile_view(request, username):
    profile_user = get_object_or_404(User.objects.select_related('profile'), username=username)
    posts = Post.objects.filter(user=profile_user)
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, following=profile_user
        ).exists()

    return render(request, 'social/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
    })


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'social/edit_profile.html', {'form': form})


@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    if request.user == target_user:
        messages.error(request, "You can't follow yourself.")
        return redirect('profile', username=username)

    follow, created = Follow.objects.get_or_create(
        follower=request.user, following=target_user
    )
    if not created:
        follow.delete()  # Unfollow
        messages.success(request, f'Unfollowed {target_user.username}.')
    else:
        messages.success(request, f'Following {target_user.username}!')

    return redirect('profile', username=username)
