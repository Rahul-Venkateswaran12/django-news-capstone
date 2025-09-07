from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import CustomUser, Publisher, Article, Newsletter
from .forms import RegistrationForm, LoginForm, ArticleForm
from .forms import NewsletterForm, SubscriptionForm
from .twitter_api import tweet_new_article
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.decorators import permission_classes, renderer_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework_xml.renderers import XMLRenderer
from django.db.models import Q
from .serializers import ArticleSerializer, ApproveArticleSerializer


def register(request):
    """Handles user registration with role selection."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                return render(request, 'confirmation.html',
                              {'message': 'Registration successful!'})
            except ValueError as e:
                form.add_error(None, f"Error: {e}")
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    """Role-based home dashboard view."""
    if request.user.role == 'reader':
        articles = Article.objects.filter(approved=True).filter(
            Q(publisher__in=request.user.subscribed_publishers.all()) |
            Q(journalist__in=request.user.subscribed_journalists.all())
        )
        newsletters = Newsletter.objects.filter(approved=True).filter(
            Q(publisher__in=request.user.subscribed_publishers.all()) |
            Q(journalist__in=request.user.subscribed_journalists.all())
        )
        return render(request, 'reader_home.html',
                      {'articles': articles, 'newsletters': newsletters})
    elif request.user.role == 'journalist':
        return redirect('journalist_dashboard')
    elif request.user.role == 'editor':
        return redirect('editor_dashboard')
    return HttpResponse("Invalid role", status=400)


@login_required
def journalist_dashboard(request):
    if request.user.role != 'journalist':
        return HttpResponse("Unauthorized", status=403)
    articles = Article.objects.filter(journalist=request.user)
    newsletters = Newsletter.objects.filter(journalist=request.user)
    return render(request, 'journalist_dashboard.html',
                  {'articles': articles, 'newsletters': newsletters})


@login_required
def editor_dashboard(request):
    if request.user.role != 'editor':
        return HttpResponse("Unauthorized", status=403)
    unapproved_articles = Article.objects.filter(approved=False)
    approved_articles = Article.objects.filter(approved=True)
    unapproved_newsletters = Newsletter.objects.filter(approved=False)
    approved_newsletters = Newsletter.objects.filter(approved=True)
    return render(request, 'editor_dashboard.html', {
        'unapproved_articles': unapproved_articles,
        'approved_articles': approved_articles,
        'unapproved_newsletters': unapproved_newsletters,
        'approved_newsletters': approved_newsletters
    })


@login_required
def subscribe(request):
    if request.user.role != 'reader':
        return HttpResponse("Unauthorized", status=403)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            request.user.subscribed_publishers.set(
                form.cleaned_data['publishers'])
            request.user.subscribed_journalists.set(
                form.cleaned_data['journalists'])
            request.user.save()
            return redirect('home')
    else:
        form = SubscriptionForm(initial={
            'publishers': request.user.subscribed_publishers.all(),
            'journalists': request.user.subscribed_journalists.all()
        })
    return render(request, 'subscription.html', {'form': form})


@login_required
def create_article(request):
    if request.user.role != 'journalist':
        return HttpResponse("Unauthorized", status=403)
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.journalist = request.user
            article.save()
            if article.publisher is None:
                request.user.independent_articles.add(article)
            return redirect('journalist_dashboard')
    else:
        form = ArticleForm()
    return render(request, 'article_form.html',
                  {'form': form, 'redirect_url': 'journalist_dashboard'})


@login_required
def edit_article(request, pk):
    if request.user.role not in ['journalist', 'editor']:
        return HttpResponse("Unauthorized", status=403)
    article = get_object_or_404(Article, pk=pk)
    if (request.user.role == 'journalist'
       and article.journalist != request.user):
        return HttpResponse("Unauthorized: "
                            "You can only edit your own articles",
                            status=403)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('journalist_dashboard' if request.user.role ==
                            'journalist' else 'editor_dashboard')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'article_form.html',
                  {'form': form, 'article': article,
                   'redirect_url': 'journalist_dashboard'
                   if request.user.role ==
                   'journalist' else 'editor_dashboard'})


@login_required
def delete_article(request, pk):
    if request.user.role not in ['journalist', 'editor']:
        return HttpResponse("Unauthorized", status=403)
    article = get_object_or_404(Article, pk=pk)
    if (request.user.role == 'journalist'
       and article.journalist != request.user):
        return HttpResponse("Unauthorized", status=403)
    if request.method == 'POST':
        article.delete()
        return redirect('journalist_dashboard'
                        if request.user.role ==
                        'journalist'
                        else 'editor_dashboard')
    return render(request, 'confirm_delete.html',
                  {'object': article,
                   'redirect_url': 'journalist_dashboard'
                   if request.user.role ==
                   'journalist' else 'editor_dashboard'})


@login_required
def approve_article(request, pk):
    if request.user.role != 'editor':
        return HttpResponse("Unauthorized", status=403)
    article = get_object_or_404(Article, pk=pk)
    try:
        article.approve()  # Triggers email/tweet
        return redirect('editor_dashboard')
    except Exception as e:
        return HttpResponse(f"Error approving: {e}", status=500)


@login_required
def create_newsletter(request):
    if request.user.role != 'journalist':
        return HttpResponse("Unauthorized", status=403)
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.journalist = request.user
            newsletter.save()
            if newsletter.publisher is None:
                request.user.independent_newsletters.add(newsletter)
            return redirect('journalist_dashboard')
    else:
        form = NewsletterForm()
    return render(request, 'newsletter_form.html',
                  {'form': form, 'redirect_url': 'journalist_dashboard'})


@login_required
def edit_newsletter(request, pk):
    if request.user.role not in ['journalist', 'editor']:
        return HttpResponse("Unauthorized", status=403)
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if (request.user.role == 'journalist'
       and newsletter.journalist != request.user):
        return HttpResponse("Unauthorized", status=403)
    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            return redirect('journalist_dashboard' if request.user.role ==
                            'journalist' else 'editor_dashboard')
    else:
        form = NewsletterForm(instance=newsletter)
    return render(request, 'newsletter_form.html',
                  {'form': form, 'newsletter': newsletter,
                   'redirect_url': 'journalist_dashboard'
                   if request.user.role ==
                   'journalist' else 'editor_dashboard'})


@login_required
def delete_newsletter(request, pk):
    if request.user.role not in ['journalist', 'editor']:
        return HttpResponse("Unauthorized", status=403)
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if (request.user.role == 'journalist'
       and newsletter.journalist != request.user):
        return HttpResponse("Unauthorized", status=403)
    if request.method == 'POST':
        newsletter.delete()
        return redirect('journalist_dashboard'
                        if request.user.role ==
                        'journalist' else 'editor_dashboard')
    return render(request, 'confirm_delete.html',
                  {'object': newsletter,
                   'redirect_url': 'journalist_dashboard'
                   if request.user.role ==
                   'journalist' else 'editor_dashboard'})


@login_required
def approve_newsletter(request, pk):
    if request.user.role != 'editor':
        return HttpResponse("Unauthorized", status=403)
    newsletter = get_object_or_404(Newsletter, pk=pk)
    try:
        newsletter.approve()
        return redirect('editor_dashboard')
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication])
@renderer_classes((JSONRenderer, XMLRenderer))
def api_articles(request):
    if request.method == 'GET':
        user = request.user
        client_id = request.query_params.get('client_id')
        if client_id:
            client = get_object_or_404(CustomUser,
                                       id=client_id, role='reader')
        else:
            client = user if user.role == 'reader' else None
        if not client:
            return Response({"error": "Invalid client"}, status=403)
        articles = Article.objects.filter(approved=True).filter(
            Q(publisher__in=client.subscribed_publishers.all()) |
            Q(journalist__in=client.subscribed_journalists.all())
        )
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if request.user.role != 'journalist':
            return Response({"error":
                             "Only journalists can create articles"},
                            status=403)
        serializer = ArticleSerializer(data=request.data,
                                       context={'request': request})
        if serializer.is_valid():
            article = serializer.save()
            tweet_new_article(article)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication])
@renderer_classes((JSONRenderer, XMLRenderer))
def api_list_publisher_articles(request, pk):
    if request.user.role not in ['editor', 'journalist']:
        return Response({"error": "Only editors and journalists"},
                        status=403)
    articles = Article.objects.filter(publisher_id=pk)
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication])
@renderer_classes((JSONRenderer, XMLRenderer))
def api_approve_article(request, pk):
    if request.user.role != 'editor':
        return Response({"error":
                         "Only editors can approve articles"},
                        status=403)
    article = get_object_or_404(Article, pk=pk)
    serializer = ApproveArticleSerializer(article,
                                          data={'approved':
                                                True},
                                          partial=True)
    if serializer.is_valid():
        article.approve()
        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication])
@renderer_classes((JSONRenderer, XMLRenderer))
def api_subscribe(request):
    client_id = request.data.get('client_id')
    publisher_id = request.data.get('publisher_id')
    journalist_id = request.data.get('journalist_id')
    if not client_id:
        return Response({"error": "client_id required"}, status=400)
    client = get_object_or_404(CustomUser, id=client_id, role='reader')
    if publisher_id:
        publisher = get_object_or_404(Publisher, id=publisher_id)
        client.subscribed_publishers.add(publisher)
    if journalist_id:
        journalist = get_object_or_404(CustomUser, id=journalist_id,
                                       role='journalist')
        client.subscribed_journalists.add(journalist)
    return Response({"success": "Subscribed"}, status=200)
