from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Page, Clap
from django.shortcuts import redirect
from .forms import PageForm
from django.http import JsonResponse
from django.db.models import Q

def blog_list(request):

    tab = request.GET.get('tab')
    search = request.GET.get('search', '')

    posts = Page.objects.filter(page_type='Blog', status='active').order_by('-date')

    # 🔍 LIVE SEARCH (title + content keywords)
    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(category__icontains=search)
        )

    # 🔥 AJAX RESPONSE
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        data = []
        for p in posts[:20]:
            data.append({
                "id": str(p.id),
                "title": p.title,
                "user": str(p.user) if p.user else "Anonymous",
                "date": p.date.strftime("%b %d"),
                "image": p.image.url if p.image else "",
                "claps": p.clap_count,
                "reading_time": p.reading_time(),
            })

        return JsonResponse({"posts": data})

    # NORMAL PAGINATION
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    trending = Page.objects.filter(page_type='Blog', status='active').order_by('-clap_count')[:5]

    return render(request, 'page/blog_list.html', {'posts': posts,'trending': trending,'tab': tab})

@login_required
def create_post(request):
    form = PageForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        post.page_type = "Blog"
        post.save()
        return redirect('blog_detail', pk=post.pk)

    return render(request, 'page/create.html', {'form': form})

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
