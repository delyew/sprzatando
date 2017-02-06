from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.template import Template
from .models import Offer, SignedWorker, Rank
from .forms import OfferForm, RankForm, FilterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Q, Count
from django.contrib import messages
from datetime import datetime
import json
from django.core import serializers
from django.template.loader import render_to_string

def index(request):
    """
    Index
    """
    if request.user.is_authenticated():
        offer = Offer.objects.all().order_by('-id')
        workers = SignedWorker.objects.all()
        return render(request, 'cleaning/index.html', {'offer': offer,
                                                       'workers': workers})
    else:
        return render(request, 'registration/login_index.html')


def new_offer(request):
    """
    Sprawdza formularz oferty, jeśli jest prawidłowy to dodaje oferte
    """
    form = OfferForm()
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.author = request.user
            offer.save()
            return redirect('index')
        else:
            return render(request, 'cleaning/new_offer.html', {'form': form})
    else:
        return render(request, 'cleaning/new_offer.html', {'form': form})


def sign(request, pk):
    """
    Zapisanie chętnego pracownika do oferty
    :param pk: ID oferty
    """
    offer = get_object_or_404(Offer, pk=pk)

    signed = SignedWorker(signed_offer=offer, worker=request.user)
    signed.save()
    return redirect('search_offer')


def search_offer(request):
    """
    Filtrowanie ofert w których autor nie jest zalogowanym userem,
    ofert do których zalogowany user sie nie zapisał,
    ofert w których nie ma wybranego i zaakceptowanego pracownika
    """
    # today = datetime.today(), jesli chcemy ukryc starsze niz dzisiaj to robimy filtr target_date__gte=today
    offers = Offer.objects.exclude(author=request.user).exclude(signedworker__worker=request.user).filter(
        chosen_worker__isnull=True).order_by('-id')  # oferty przed filtrowaniem
    if request.GET:
        form = FilterForm(request.GET)
        if form.is_valid():
            queries = []
            for k, v in form.cleaned_data.items():
                if v == '' or v is None or v is False:
                    continue
                else:
                    q_name = Q(**{k: v})
                    queries.append(q_name)
            # ANDowanie queries
            if len(queries) == 0:
                messages.add_message(request, messages.INFO, "nic nie wybrales")
                return redirect('search_offer')
            else:
                query = queries.pop()
                for item in queries:
                    query &= item

            offers = Offer.objects.exclude(author=request.user).exclude(signedworker__worker=request.user).filter(
                chosen_worker__isnull=True).filter(
                query).order_by('-id')  # oferty z filtrowaniem

            return render(request, 'cleaning/search_offer.html', {'offers': offers,
                                                                  'form': form,
                                                                  })
        else:
            return render(request, 'cleaning/search_offer.html', {
                'form': form,
                'offers': offers,
            })
    else:
        form = FilterForm()
        return render(request, 'cleaning/search_offer.html', {
            'form': form,
            'offers': offers,
        })


def my_offer(request):
    """
    Oferty zalogowanego użytkownika:
    -Dodane,
    -Do których się zapisał,
    -Do których został zaakceptowany
    """

    offer = Offer.objects.filter(author=request.user).order_by('-id')
    signed_offer_all = []
    # id ofert z co najmniej jednym zapisanym użytkownikiem
    for s in SignedWorker.objects.all():
        signed_offer_all.append(s.signed_offer.pk)

    signed_offer = SignedWorker.objects.filter(worker=request.user)
    accepted_offer = Offer.objects.filter(chosen_worker__in=signed_offer)
    return render(request, 'cleaning/my_offer.html', {'offer': offer,
                                                      'signed_offer': signed_offer,
                                                      'accepted_offer': accepted_offer,
                                                      'signed_offer_all': signed_offer_all,})


def choose_worker(request, pk):
    """
    Wybranie użytkownika z listy zapisanych do danej oferty,
    Lista składa się z nazwy użytkownika oraz jego średniej oceny
    :param pk: ID oferty
    """
    offer = get_object_or_404(Offer, pk=pk)
    workers = SignedWorker.objects.filter(signed_offer=offer)
    worker_rank = Rank.objects.filter(user__signedworker__in=workers).values('user__signedworker', 'user__username').annotate(
        Avg('grade'))
    users = User.objects.filter(is_active=True)
    return render(request, 'cleaning/choose_worker.html', {'workers': workers,
                                                           'offer': offer,
                                                           'worker_rank': worker_rank,
                                                           'users': users})


def save_worker(request, pk, worker_pk):
    """
    Zaakceptowanie użytkownika który się zapisał do oferty
    :param pk: ID oferty
    :param worker_pk: ID zapisanego użytkownika
    """
    offer = get_object_or_404(Offer, pk=pk)
    worker = get_object_or_404(SignedWorker, pk=worker_pk)
    offer.chosen_worker = worker
    offer.save()
    return redirect('my_offer')


def ranking(request):
    """
    Ranking użytkowników sortowany malejąco po ilości ocen oraz średniej oceny
    """
    rank = Rank.objects.values('user', 'user__username').annotate(avg_grade=Avg('grade'),
                                                                  count=Count('grade')).order_by('-count', '-avg_grade')
    return render(request, 'cleaning/ranking.html', {'rank': rank})


def personal_rank(request, pk):
    """
    Profil danego użytkownika, wyświetla wszystkie opinie oraz oceny
    :param pk: ID usera
    """
    profile = get_object_or_404(User, pk=pk)
    user_rank = Rank.objects.filter(user=profile)
    avg_grade = Rank.objects.filter(user=profile).aggregate(Avg('grade'))
    return render(request, 'cleaning/personal_rank.html', {'user_rank': user_rank,
                                                           'avg_grade': avg_grade,
                                                           'profile': profile})


def rate_user(request, pk):
    """
    Ocena użytkownika po potwierdzeniu wykonania pracy
    :param pk: ID oferty
    """
    user = Offer.objects.get(pk=pk)
    form = RankForm()
    if request.method == "POST":
        form = RankForm(request.POST)
        if form.is_valid():
            rank = form.save(commit=False)
            rank.user = user.chosen_worker.worker
            rank.save()
            user.delete()
            return redirect('ranking')
        else:
            return render(request, 'cleaning/rate.html', {'form': form})

    else:
        return render(request, 'cleaning/rate.html', {'form': form})


def worker_accept(request, pk, yes_no):
    """
    Zapisany użytkownik który został zaakceptowany może potwierdzić chęć pracy
    :param pk: ID oferty
    :param yes_no: 0 - Nie podejmuje się pracy, 1 - Podejmuje się pracy
    """
    offer = get_object_or_404(Offer, pk=pk)
    if offer.worker_accepted:
        return redirect('my_offer')
    else:
        if yes_no == 1 or yes_no == "1":
            offer.worker_accepted = True
            offer.save()
            return redirect('my_offer')
        else:
            signed_offer = SignedWorker.objects.filter(signed_offer=offer, worker=request.user)
            offer.chosen_worker = None
            signed_offer.delete()
            offer.save()
            return redirect('my_offer')
