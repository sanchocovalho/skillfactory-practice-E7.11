from django.shortcuts import redirect, render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.template import loader, RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from ads_app.models import Comment, Category, Advert
from ads_app.forms import CommentForm, AdvertForm
from datetime import datetime
import pickle
import redis

redis_cache = redis.Redis(host='127.0.0.1', port=6379)

def get_advert_context():
    adverts = redis_cache.get('advert_list')
    if adverts:
        adverts = pickle.loads(adverts)
    else:
        adverts = Advert.objects.all()
        redis_cache.set('advert_list', pickle.dumps(adverts))
    return adverts

def get_category_context():
    categories = redis_cache.get('category_list')
    if categories:
        categories = pickle.loads(categories)
    else:
        categories = Category.objects.all()
        redis_cache.set('category_list', pickle.dumps(categories))
    return categories

def get_comment_context():
    comments = redis_cache.get('comment_list')
    if comments:
        comments = pickle.loads(comments)
    else:
        comments = Comment.objects.all()
        redis_cache.set('comment_list', pickle.dumps(comments))
    return comments

def error_404_view(request, exception):
    return render(request, '404.html')

def advert_detail(request, pk):
    advert = get_advert_context().get(pk=pk)
    if 'btnAddTag' in request.POST:
        req_tag = request.POST.get('tag').replace(' ', '')
        if advert.tags:
            if not req_tag in advert.tags:
                advert.tags += f' {req_tag}'
        else:
            advert.tags = req_tag
        advert.save()
        redis_cache.set('adverts_list', pickle.dumps(Advert.objects.all()))
        return redirect('/id' + str(pk))
    context = {}
    context['comment_list'] = get_comment_context().filter(advert__pk=pk)
    context['tag_list'] = advert.tags.split(' ') if advert.tags else advert.tags
    context['advert'] = advert
    return render(request, 'advert_detail.html', context)

def create_comment(request, pk):
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.advert = get_advert_context().get(pk=pk)
        comment.save()
        redis_cache.set('comments_list', pickle.dumps(Comment.objects.all()))
    return redirect('/id' + str(pk))

@login_required
def comment_update_form(request, pk, id):
    comment = Comment.objects.get(pk=pk)
    context = {'comment': comment,
               'advert_id': id}
    return render(request, 'comment_edit.html', context)

@login_required
def update_comment(request, pk, id):
    form = CommentForm(request.POST)
    if form.is_valid():
        comments = Comment.objects.all()
        comment = comments.get(pk=pk)
        comment.author = form.cleaned_data['author']
        comment.content = form.cleaned_data['content']
        comment.update = datetime.now()
        comment.save()
        redis_cache.set('comments_list', pickle.dumps(comments))
    return redirect('/id' + str(id))

@login_required
def cancel_comment(request, pk):
    advert = get_advert_context().get(pk=pk)
    context = {'advert': advert}
    return render(request, 'comment_default.html', context)

@login_required
def delete_comment(request, pk, id):
    comments = Comment.objects.all()
    comment = comments.get(pk=pk)
    comment.delete()
    redis_cache.set('comments_list', pickle.dumps(comments))
    return redirect('/id' + str(id))

class AdvertDelete(LoginRequiredMixin, DeleteView):
    login_url = '/'
    redirect_field_name = ''
    model = Advert
    success_url = reverse_lazy('ads_app:advert-list')
    template_name = 'advert_delete.html'

    def delete(self, request, *args, **kwargs):
        adverts = Advert.objects.all()
        advert = adverts.get(id=kwargs['pk'])
        if advert.photo:
            advert.photo.delete(False)
        advert.delete()
        redis_cache.set('advert_list', pickle.dumps(adverts))
        return redirect('/')

class AdvertUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/'
    redirect_field_name = ''
    model = Advert
    form_class = AdvertForm
    success_url = reverse_lazy('ads_app:advert-list')
    template_name = 'advert_edit.html'

    def post(self, request, *args, **kwargs):
        adverts = Advert.objects.all()
        advert = adverts.get(id=kwargs['pk'])
        form = AdvertForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.cleaned_data['photo']
            if photo == False:
                advert.photo.delete(False)
                advert.photo = None
            elif photo:
                advert.photo.delete(False)
                advert.photo = form.cleaned_data['photo']
            advert.title = form.cleaned_data['title']
            advert.content = form.cleaned_data['content']
            advert.tags = form.cleaned_data['tags']
            advert.category = Category.objects.get(pk=request.POST.get('category'))
            advert.updated = datetime.now()
            advert.save()
            redis_cache.set('advert_list', pickle.dumps(adverts))
        return redirect('/id' + str(kwargs['pk']))

class AdvertCreate(LoginRequiredMixin, CreateView):
    login_url = '/'
    redirect_field_name = ''
    model = Advert
    form_class = AdvertForm
    success_url = reverse_lazy('ads_app:advert-list')
    template_name = 'advert_create.html'

    def post(self, request, *args, **kwargs):
        form = AdvertForm(request.POST, request.FILES)
        if form.is_valid():
            advert = Advert()
            advert.photo = form.cleaned_data['photo']
            advert.author = request.user
            advert.title = form.cleaned_data['title']
            advert.content = form.cleaned_data['content']
            advert.tags = form.cleaned_data['tags']
            advert.category = get_category_context().get(pk=request.POST.get('category'))
            advert.save()
            redis_cache.set('advert_list', pickle.dumps(Advert.objects.all()))
        return redirect('/')

class AdvertList(ListView):
    model = Advert
    template_name = 'advert_list.html'

    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context['advert_list'] = get_advert_context()
        context['category_list'] = get_category_context()
        return context

    def dispatch(self, request, *args, **kwargs):
        if 'btnLogIn' in request.POST:
            context = {}
            context['advert_list'] = get_advert_context()
            context['category_list'] = get_category_context()
            form = AuthenticationForm(request=request, data=request.POST)
            if form.is_valid():
                login(request, form.get_user())
                context['errmsg'] = 0
            else:
                context['errmsg'] = 1
            return render(request, 'advert_list.html', context) 
        elif 'btnLogOut' in request.POST:
            logout(request)
            return redirect('/')
        elif 'btnAddAdvert' in request.POST:
            return redirect('/create')
        elif 'btnSearch' in request.GET:
            context = {}
            adverts = get_advert_context()
            context['category_list'] = get_category_context()
            combo_val = request.GET.get('cmbCategoty')
            query = request.GET.get('search', '')
            if not combo_val or combo_val == '0':
                context['advert_list'] = adverts.filter(
                    Q(title__icontains=query.lower())|
                    Q(content__icontains=query.lower())|
                    Q(tags__icontains=query.lower())|
                    Q(title__icontains=query.upper())|
                    Q(content__icontains=query.upper())|
                    Q(tags__icontains=query.upper())|
                    Q(title__icontains=query.capitalize())|
                    Q(content__icontains=query.capitalize())|
                    Q(tags__icontains=query.capitalize()))
            else:
                context['advert_list']= adverts.filter(
                    Q(category__id=int(combo_val))&
                   (Q(title__icontains=query.lower())|
                    Q(content__icontains=query.lower())|
                    Q(tags__icontains=query.lower())|
                    Q(title__icontains=query.upper())|
                    Q(content__icontains=query.upper())|
                    Q(tags__icontains=query.upper())|
                    Q(title__icontains=query.capitalize())|
                    Q(content__icontains=query.capitalize())|
                    Q(tags__icontains=query.capitalize())))
            return render(request, 'advert_list.html', context)
        return super(AdvertList, self).dispatch(request, *args, **kwargs)
