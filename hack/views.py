from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse

from spotipy import oauth2
import spotipy

CLIENT_ID = 'bb101bf3987840f79cdc0c11a819b8c5'
CLIENT_SECRET = '2acb736cc399427382570f1e47996c48'
redirect_uri = 'http://localhost:8000'
scope = 'user-top-read'
AUTH_TOKEN = {}

sp_oauth = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, redirect_uri, scope=scope)


def callback(request):
    req_code = request.GET.get('code')
    TOKEN = sp_oauth.get_access_token(req_code)
    if TOKEN:
        # return HttpResponse(content='Login feito com sucesso', status=200)
        # return render_to_response(template_name='hack/login.html', context={'response': 'Login feito com sucesso'})
        return render(request, 'hack/login.html', {'response': 'Login feito com sucesso'})

    else:
        return HttpResponse(content='Falha ao fazer o login', status=400)


def redirect_url(request):
    auth_url = sp_oauth.get_authorize_url()

    return redirect(auth_url)


def home(request):
    return render(request, 'hack/home.html')


def search(request):
    return render(request, 'hack/searchdestiny.html')
