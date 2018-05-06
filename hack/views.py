from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
import pandas as pd
import pymongo

from spotipy import oauth2
import spotipy
from sklearn.neighbors import NearestNeighbors

CLIENT_ID = 'bb101bf3987840f79cdc0c11a819b8c5'
CLIENT_SECRET = '2acb736cc399427382570f1e47996c48'
redirect_uri = 'http://localhost:8000'
scope = 'user-top-read'
TOKEN = {}
DATA = {}

mg_client = pymongo.MongoClient('localhost', 27017)
mongo_db = mg_client['db']
collection = mongo_db['collection']

sp_oauth = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, redirect_uri, scope=scope)


def save_info(token):
    sp = spotipy.Spotify(auth=token['access_token'])
    results = sp.current_user_top_artists(42)
    aux = pd.DataFrame()

    for r in results['items']:
        aux = pd.concat([aux, pd.DataFrame(r['genres'], columns=['genero'])], axis=0, ignore_index=True)

    aux = aux.drop_duplicates(['genero']).reset_index(drop=True)

    current_user = sp.current_user()
    import ipdb;ipdb.set_trace()

    DATA = {
            'userid': current_user['id'],
            'generos': aux['genero'].tolist()

    }

    collection.insert(DATA)


def callback(request):
    req_code = request.GET.get('code')
    token = sp_oauth.get_access_token(req_code)
    if token['access_token']:
        # return HttpResponse(content='Login feito com sucesso', status=200)
        # return render_to_response(template_name='hack/login.html', context={'response': 'Login feito com sucesso'})
        save_info(token)
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


def df_comp():
    df = pd.DataFrame(list(collection.find()))
    op = pd.concat([df, pd.get_dummies(pd.DataFrame(df['generos'].tolist()).stack().drop_duplicates()).sum(level=0)],axis=1)
    op.fillna(0, inplace=True)
    return op


def search_knn_index(indexes=[]):
    op = df_comp()
    return op[op.index.isin(indexes)]


def get_my_index(user_id=None, user_email=None):
    op = df_comp()
    if user_id:
        response = op[op['userid'] == user_id].index[0]
    elif user_email:
        response = op[op['email'] == user_email].index[0]
    else:
        response = 'Passe um email ou userid'

    return response


def create_matrix():
    op = df_comp()
    x = op.drop(['_id', 'generos', 'userid'], axis=1)
    knn = NearestNeighbors(n_neighbors=3)
    knn.fit(x)
    arr = knn.kneighbors(x, return_distance=False)
    matches = search_knn_index(arr[get_my_index(user_id=DATA['userid'])]).to_dict(orient='records')

    return matches


def get_matches(request):
    matches = create_matrix()
    sp = spotipy.Spotify(auth=TOKEN)
    users = []

    for obj in matches:
        users.append(sp.user(obj['userid']))

    return render(request, template_name='matches.html', context=users)

