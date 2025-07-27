from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView,
    UpdateView,
    CreateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import (
    CommentEditForm,
    PostEditForm,
    UserEditForm,
    UserRegistrationForm,
)
from .constants import PAGINATE_BY
from .mixins import PostMixin, CommentMixin, AuthorRequiredMixin
from .models import Category, Comment, Post
from .services import filter_published_posts, annotate_posts_with_comment_count

User = get_user_model()


class SignUpView(CreateView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/registration_form.html'


class BasePostListView(ListView):
    model = Post
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return annotate_posts_with_comment_count(
            filter_published_posts(Post.objects.all())
        )

    class Meta:
        abstract = True


class PostListView(BasePostListView):
    template_name = 'blog/index.html'


class CategoryPostsView(BasePostListView):
    template_name = 'blog/category.html'

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        self.category = self.get_category()
        return annotate_posts_with_comment_count(
            filter_published_posts(Post.objects.filter(category=self.category))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class UserPostsView(PostListView):
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        queryset = self.author.posts.all()
        queryset = annotate_posts_with_comment_count(queryset)
        if self.author != self.request.user:
            queryset = filter_published_posts(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class PostDetailView(ListView):
    model = Comment
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    paginate_by = PAGINATE_BY

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return get_object_or_404(
            Post,
            pk=self.kwargs['post_id'],
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    def get_queryset(self):
        post = self.get_object()
        return post.comments.all().select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['comments'] = context['page_obj']
        context['form'] = CommentEditForm()
        return context


@login_required
def profile_update(request):
    user = request.user
    form = UserEditForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=user.username)
    return render(request, 'blog/user.html', {'form': form})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(PostMixin, UpdateView):
    form_class = PostEditForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return super().get_success_url()

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class CommentCreateView(CommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, AuthorRequiredMixin, UpdateView):
    form_class = CommentEditForm


class CommentDeleteView(AuthorRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
