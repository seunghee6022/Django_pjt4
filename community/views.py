from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Comment
from .forms import ReviewForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
# Create your views here.
def index(request):
    movies = Movie.objects.order_by('-pk')
    context = {
        'movies': movies,
    }
    return render(request, 'community/index.html',context)

def review_list(request,movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    reviews = Review.objects.order_by('-pk')
    context = {
        'reviews': reviews,
        'movie': movie,
    }
    return render(request, 'community/review_list.html', context)

# @login_required
def create(request, movie_pk ):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()

            return redirect('community:review_list', movie.pk)
    else:
        review_form = ReviewForm()
    context = {
        'review_form' : review_form,
        'movie':movie,

    }
    return render(request,'community/form.html',context)

def detail(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk)
    comment_form = CommentForm()
    context = {
        'movie':movie,
        'review':review,
        'comment_form' : comment_form,
    }
    return render(request, 'community/review_detail.html', context)


def update(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        if review.user != request.user:
            return redirect('community:detail', movie.pk, review.pk)
        else :
            if request.method == "POST":
                review_form = ReviewForm(request.POST, instance=review)
                if review_form.is_valid():
                    updated = review_form.save()
                    return redirect('community:detail', movie.pk, updated.pk)
            else :
                review_form = ReviewForm(instance=review)
            context = {
                'movie':movie,
                'review_form' : review_form
            }
            return render(request,'community/form.html', context)
    else:
        return redirect('accounts:login')


@login_required
@require_POST
def delete(request, movie_pk, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        if review.user != request.user:
            return redirect('community:detail', review.pk)
        else:
            if request.method == "POST":
                review = get_object_or_404(Review, pk=review_pk)
                review.delete()
                return redirect('community:review_list', movie_pk)
            else :
                return redirect('community:detail', movie_pk, review.pk)

    else:
        return redirect('accounts:login')


@login_required
def comment_create(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk)

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.review = review
            comment.user = request.user
            comment.save()

        return redirect('community:detail', movie.pk, review.pk)

@require_POST
def comment_delete(request, movie_pk, review_pk, comment_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.user.is_authenticated:
        if request.method == "POST":
            comment = get_object_or_404(Comment, pk=comment_pk)
            if comment.user == request.user:
                comment.delete()
        return redirect('community:detail', movie.pk, review_pk)
    else :
        return redirect('accounts:login')

def like(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user.is_authenticated :
        if review.like_users.filter(id=request.user.pk).exists():
            review.like_users.remove(request.user)
        else:
            review.like_users.add(request.user)

    else :
        return redirect('accounts:login')

    return redirect('community:detail', movie_pk, review_pk)