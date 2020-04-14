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

def error_404_view(request, exception):
    return render(request, '404.html')

def advert_detail(request, pk):
    advert = Advert.objects.get(pk=pk)
    if 'btnAddTag' in request.POST:
        req_tag = request.POST.get('tag').replace(' ', '')
        if advert.tags:
            if not req_tag in advert.tags:
                advert.tags += f' {req_tag}'
        else:
            advert.tags = req_tag
        advert.save()
        return redirect('/id' + str(pk))
    comments = Comment.objects.filter(advert__pk=pk)
    tags = advert.tags.split(' ') if advert.tags else advert.tags
    context = {'advert': advert,
               'tag_list': tags,
               'comment_list': comments}
    return render(request, 'advert_detail.html', context)

def create_comment(request, pk):
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.advert = Advert.objects.get(pk=pk)
        comment.save()
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
        comment = Comment.objects.get(pk=pk)
        comment.author = form.cleaned_data['author']
        comment.content = form.cleaned_data['content']
        comment.update = datetime.now()
        comment.save()
    return redirect('/id' + str(id))

@login_required
def cancel_comment(request, pk):
    advert = Advert.objects.get(pk=pk)
    context = {'advert': advert}
    return render(request, 'comment_default.html', context)

@login_required
def delete_comment(request, pk, id):
    comment = Comment.objects.get(pk=pk)
    comment.delete()
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
        return redirect('/')

class AdvertUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/'
    redirect_field_name = ''
    model = Advert
    form_class = AdvertForm
    success_url = reverse_lazy('ads_app:advert-list')
    template_name = 'advert_edit.html'

    def post(self, request, *args, **kwargs):
        advert = Advert.objects.get(id=kwargs['pk'])
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
            advert.category = Category.objects.get(pk=request.POST.get('category'))
            advert.save()
        return redirect('/')

class AdvertList(ListView):
    model = Advert
    template_name = 'advert_list.html'

    def dispatch(self, request, *args, **kwargs):
        if 'btnLogIn' in request.POST:
            context = {}
            context['advert_list'] = Advert.objects.all()
            context['category_list'] = Category.objects.all()
            form = AuthenticationForm(request=request, data=request.POST)
            if form.is_valid():
                login(request, form.get_user())
                context['errmsg'] = 0
            else:
                context['errmsg'] = 1
            return render(request, 'advert_list.html', context) 
        elif 'btnLogOut' in request.POST:
            logout(self.request)
            return redirect('/')
        elif 'btnAddAdvert' in request.POST:
            return redirect('/create')
        elif 'btnSearch' in request.GET:
            combo_val = request.GET.get('cmbCategoty')
            query = request.GET.get('search', '')
            if not combo_val or combo_val == '0':
                advert_list = Advert.objects.filter(
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
                advert_list = Advert.objects.filter(
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
            categories = Category.objects.all()
            context = {'category_list': categories,
                       'advert_list': advert_list}
            return render(self.request, 'advert_list.html', context)
        else:
            categories = Category.objects.all()
            adverts = Advert.objects.all()
            context = {'category_list': categories,
                       'advert_list': adverts}
            return render(self.request, 'advert_list.html', context)
