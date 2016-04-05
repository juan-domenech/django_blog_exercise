from django.shortcuts import render, HttpResponse, get_object_or_404
from django.utils import timezone
from .models import Post

# Create your views here.
def test(request):
    return HttpResponse('Test OK!')

def post_list(request):
    posts = Post.objects.filter(published_date__lte = timezone.now() ).order_by('-published_date')
    return render(request, "blogtests.html",{'posts' : posts } )

def post_detail(request,id):
    post = get_object_or_404(Post,pk=id)
    return render(request, "blogdetail.html",{'post' : post} )
