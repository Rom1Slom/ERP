from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Stagiaire, SessionFormation, Formation
from django.contrib import messages
from django.urls import reverse

@login_required
def inscrire_stagiaire_session(request, stagiaire_id):
    stagiaire = get_object_or_404(Stagiaire, id=stagiaire_id, entreprise=request.user.profil.entreprise)
    sessions = SessionFormation.objects.all().order_by('-date_debut')
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        session = get_object_or_404(SessionFormation, id=session_id)
        Formation.objects.get_or_create(
            stagiaire=stagiaire,
            session=session,
            defaults={
                'date_debut': session.date_debut,
                'organisme_formation': session.organisme_formation,
            }
        )
        messages.success(request, f"{stagiaire.nom} inscrit à la session {session.numero_session}.")
        return redirect('stagiaire_list')
    return render(request, 'habilitations_app/inscrire_stagiaire_session.html', {
        'stagiaire': stagiaire,
        'sessions': sessions,
    })
