from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView


# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import Post, Category, User
from .filters import PostSearch
from .forms import PostForm, UserForm

class NewsList(LoginRequiredMixin, ListView):
   model = Post
   ordering = 'title'
   template_name = 'News.html'
   context_object_name = 'news'
   extra_context = {'title': 'Новости'}
   author = 'author'
   # queryset = Post.objects.order_by('-dateCreation')
   paginate_by = 10

   # Переопределяем функцию получения списка товаров
   def get_queryset(self):
       # Получаем обычный запрос
       queryset = super().get_queryset()
       # Используем наш класс фильтрации.
       # self.request.GET содержит объект QueryDict, который мы рассматривали
       # в этом юните ранее.
       # Сохраняем нашу фильтрацию в объекте класса,
       # чтобы потом добавить в контекст и использовать в шаблоне.
       self.filterset = PostSearch(self.request.GET, queryset)
       # Возвращаем из функции отфильтрованный список товаров
       return self.filterset.qs

   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       # Добавляем в контекст объект фильтрации.
       context['filterset'] = self.filterset
       return context

   def post_search(request):
       f = PostSearch(request.GET,
                      queryset=Post.objects.all())
       return render(request,
                     'news_search.html',
                     {'filter': f})


class NewsDetail(DetailView):
    model = Post
    template_name = 'onenews.html'
    context_object_name = 'onenews'

class PostSearchView(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'search.html'  # указываем имя шаблона, в котором будет лежать HTML, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'NewsSearch'
    paginate_by = 10  # поставим постраничный вывод в 10 элементов
    ordering = ['-id']
    queryset = Post.objects.all()  # Default: Model.objects.all()
    # form_class = PostForm  # добавляем форм класс, чтобы получать доступ к форме через метод POST
    # Помощь ментора обычный get_context_data из PostList не подойдет
    # пагинатор не верно отображает листы
    def get_filter(self):
        return PostSearch(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'filter': self.get_filter(),
        }



class PostCreateNW(PermissionRequiredMixin, CreateView):
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'news_edit.html'
    permission_required = ('create.Post_Create',)

    def form_valid(self, form):
        post = form.save(commit=True)
        post.categoryType = "NW"
        return super().form_valid(form)


class PostEditNW(PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

class PostDeleteNW(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('post_list')



class PostDeleteAR(DeleteView):
    model = Post
    template_name = 'articles_delete.html'
    success_url = reverse_lazy('post_list')

class LoginUser(LoginRequiredMixin, LoginView):
    form_class = UserForm
    template_name = 'user_login.html'
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизация')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return  reverse_lazy('news')

class UserEdit(LoginRequiredMixin, LoginView):
    form_class = UserForm
    # model = User
    template_name = 'user_edit.html'
    success_url = reverse_lazy('post_list')

    def get_object(self, **kwargs):
        return self.request.user

class ProtectedView(LoginRequiredMixin, TemplateView):
    template_name = 'prodected_page.html'


class CategoryList(ListView):
    model = Category
    ordering = 'name'
    template_name = 'category.html'
    context_object_name = 'category'
    paginate_by = 10

@login_required
def add_subscribe(request, pk):
    Category.objects.get(pk=pk).subscribers.add(request.user)
    return redirect('/news/')
