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
redirect_uri = 'http://localhost:8000/home'
scope = 'user-top-read'
TOKEN = {}
DATA = {}

mg_client = pymongo.MongoClient('localhost', 27017)
mongo_db = mg_client['db']
collection = mongo_db['collection']

sp_oauth = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, redirect_uri, scope=scope)


def login(request):
    return render(request, 'hack/login.html')


def save_info():
    sp = spotipy.Spotify(auth=TOKEN['access_token'])
    results = sp.current_user_top_artists(42)
    aux = pd.DataFrame()

    for r in results['items']:
        aux = pd.concat([aux, pd.DataFrame(r['genres'], columns=['genero'])], axis=0, ignore_index=True)

    aux = aux.drop_duplicates(['genero']).reset_index(drop=True)

    current_user = sp.current_user()
    global DATA
    DATA = {
            'id': current_user['id'],
            'generos': aux['genero'].tolist()

    }
    if collection.find({'id': DATA['id']}).count() == 0:
        collection.insert(DATA)

    return DATA


def get_token(request):
    global TOKEN
    req_code = request.GET.get('code')
    TOKEN = sp_oauth.get_access_token(req_code)

    return TOKEN


def redirect_url(request):
    auth_url = sp_oauth.get_authorize_url()

    return redirect(auth_url)


def loading(request):
    return render(request, 'hack/loading.html')


def home(request):
    get_token(request)
    save_info()
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
        response = op[op['id'] == user_id].index[0]
    elif user_email:
        response = op[op['email'] == user_email].index[0]
    else:
        response = 'Passe um email ou id'

    return response


def create_matrix():
    op = df_comp()
    x = op.drop(['_id','generos','id'], axis=1)
    knn = NearestNeighbors(n_neighbors=4)
    knn.fit(x)
    arr = knn.kneighbors(x, return_distance=False)
    matches = search_knn_index(arr[get_my_index(user_id=DATA['id'])]).to_dict(orient='records')

    return matches


def get_matches(request):
    matches = create_matrix()
    sp = spotipy.Spotify(auth=TOKEN['access_token'])
    users = []

    for obj in matches:
        if obj['id'] == DATA['id']:
            continue
        users.append(sp.user(obj['id']))

    return render(request, template_name='hack/matches.html', context={'users': users})

