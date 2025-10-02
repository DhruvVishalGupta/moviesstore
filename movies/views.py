from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Petition, PetitionVote
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

def petitions(request):
    petitions = Petition.objects.all().order_by('-created_date')
    
    template_data = {}
    template_data['title'] = 'Movie Petitions'
    template_data['petitions'] = petitions
    return render(request, 'movies/petitions.html', {'template_data': template_data})

@login_required
def create_petition(request):
    template_data = {}
    template_data['title'] = 'Create Movie Petition'
    
    if request.method == 'GET':
        return render(request, 'movies/create_petition.html', {'template_data': template_data})
    elif request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if title and description:
            petition = Petition()
            petition.title = title
            petition.description = description
            petition.creator = request.user
            petition.save()
            messages.success(request, 'Your petition has been created successfully!')
            return redirect('movies.petitions')
        else:
            messages.error(request, 'Please fill in both title and description.')
            return render(request, 'movies/create_petition.html', {'template_data': template_data})

def petition_detail(request, id):
    petition = get_object_or_404(Petition, id=id)
    votes = PetitionVote.objects.filter(petition=petition)
    user_has_voted = False
    
    if request.user.is_authenticated:
        user_has_voted = PetitionVote.objects.filter(petition=petition, user=request.user).exists()
    
    template_data = {}
    template_data['title'] = petition.title
    template_data['petition'] = petition
    template_data['votes'] = votes
    template_data['user_has_voted'] = user_has_voted
    template_data['vote_count'] = petition.get_vote_count()
    return render(request, 'movies/petition_detail.html', {'template_data': template_data})

@login_required
def vote_petition(request, id):
    petition = get_object_or_404(Petition, id=id)
    
    # Check if user already voted
    existing_vote = PetitionVote.objects.filter(petition=petition, user=request.user)
    if existing_vote.exists():
        messages.warning(request, 'You have already voted for this petition.')
        return redirect('movies.petition_detail', id=id)
    
    # Create new vote
    vote = PetitionVote()
    vote.petition = petition
    vote.user = request.user
    vote.save()
    
    messages.success(request, 'Your vote has been recorded!')
    return redirect('movies.petition_detail', id=id)

@login_required
def remove_vote(request, id):
    petition = get_object_or_404(Petition, id=id)
    vote = get_object_or_404(PetitionVote, petition=petition, user=request.user)
    vote.delete()
    
    messages.success(request, 'Your vote has been removed.')
    return redirect('movies.petition_detail', id=id)