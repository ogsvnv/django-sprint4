from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)

from .forms import (
    CommentEditForm,
    PostEditForm,
    UserEditForm,
    UserRegistrationForm,
)
from .models import Category, Comment, Post

User = get_user_model()


def get_all_posts():
    return (Post.objects.select_related('category', 'location', 'author')
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date'))


def get_published_posts():
    return get_all_posts().filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def check_post_visibility(post, user=None):
    if user and user == post.author:
        return True
    return (
        post.is_published
        and post.pub_date <= timezone.now()
        and (post.category is None or post.category.is_published)
    )


class SignUpView(CreateView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/registration_form.html'


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = get_published_posts()
    paginate_by = 10


class CategoryPostsView(PostListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class UserPostsView(PostListView):
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        if self.author == self.request.user:
            return get_all_posts().filter(author=self.author)
        return super().get_queryset().filter(author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if not check_post_visibility(post, self.request.user):
            raise Http404('Пост не доступен')
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['form'] = CommentEditForm()
            context['flag'] = True
        context['comments'] = (
            self.object.comments.all().select_related('author')
        )
        return context


@login_required
def profile_update(request):
    user = request.user
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=user.username)
    else:
        form = UserEditForm(instance=user)
    return render(request, 'blog/user.html', {'form': form})


class PostCreateView(CreateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostEditForm(instance=self.object)
        context['delete_confirm'] = True
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentEditForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        self.post_data = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if not check_post_visibility(self.post_data, request.user):
            raise Http404('Пост не доступен')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_data
        response = super().form_valid(form)
        self.send_author_email()
        return response

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def send_author_email(self):
        post_url = self.request.build_absolute_uri(
            reverse(
                'blog:post_detail',
                kwargs={'post_id': self.kwargs['post_id']}
            )
        )
        send_mail(subject='Новый комментарий',
                  message=(f'Пользователь {self.request.user} добавил '
                           f'комментарий к посту {self.post_data.title}.\n'
                           f'Читать комментарий: {post_url}'),
                  from_email='from@example.com',
                  recipient_list=[self.post_data.author.email],
                  fail_silently=True)


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentEditForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        self.post_data = get_object_or_404(Post, id=self.kwargs['post_id'])
        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, id=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.object
        context['post'] = self.post_data
        return context


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        self.post_data = get_object_or_404(Post, id=self.kwargs['post_id'])
        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Comment, id=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.object
        context['post'] = self.post_data
        context['delete_confirm'] = True
        return context
