from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Page, Clap


def blog_list(request):
    posts = Page.objects.filter(page_type='Blog', status='active').order_by('-date')

    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    return render(request, 'page/blog_list.html', {'posts': posts})


def blog_detail(request, pk):
    page = get_object_or_404(Page, pk=pk)
    return render(request, 'page/detail.html', {'page': page})


# 👏 CLAP
@login_required
def clap_post(request, pk):
    page = get_object_or_404(Page, pk=pk)

    clap, created = Clap.objects.get_or_create(user=request.user, page=page)

    if clap.count < 50:
        clap.count += 1
        clap.save()

        page.clap_count += 1
        page.save()

    return JsonResponse({
        "claps": page.clap_count,
        "user_claps": clap.count
    })


# 🔖 BOOKMARK
@login_required
def bookmark_post(request, pk):
    page = get_object_or_404(Page, pk=pk)

    if request.user in page.bookmarks.all():
        page.bookmarks.remove(request.user)
        bookmarked = False
    else:
        page.bookmarks.add(request.user)
        bookmarked = True

    return JsonResponse({
        "bookmarked": bookmarked
    })