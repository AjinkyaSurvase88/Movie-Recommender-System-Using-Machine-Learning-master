import pickle
import streamlit as st
import requests
import time

# Function to fetch movie poster with retries
def fetch_poster(movie_id, retries=3):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=e37412bf776f29cb3da34a9645c47a3e&language=en-US"
    attempt = 0
    while attempt < retries:
        try:
            data = requests.get(url, timeout=10)
            data.raise_for_status()
            data = data.json()
            poster_path = data.get('poster_path', None)
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500/{poster_path}"
            else:
                raise ValueError("Poster not found")
        except (requests.exceptions.RequestException, ValueError):
            time.sleep(1)
            attempt += 1

    # Return stylish placeholder if all attempts fail
    return "https://i.imgur.com/Z2MYNbj.png"


# Recommend similar movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        time.sleep(1)
    return recommended_movie_names, recommended_movie_posters

# Load data
movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.markdown("""
    <style>
        .main-title {
            font-size: 3em;
            color: #00adb5;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .movie-title {
            text-align: center;
            font-size: 1.1em;
            font-weight: bold;
            margin-top: 10px;
        }
        .stButton > button {
            background-color: #00adb5;
            color: white;
            border: none;
            padding: 0.5em 2em;
            border-radius: 8px;
            font-size: 1em;
        }
        .stSelectbox > div {
            font-size: 1.1em;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🎬 Movie Recommender System</div>", unsafe_allow_html=True)

selected_movie = st.selectbox("🎥 Type or select a movie from the dropdown", movies['title'].values)

if st.button('🔍 Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(recommended_movie_posters[i], use_container_width=True)
            st.markdown(f"<div class='movie-title'>{recommended_movie_names[i]}</div>", unsafe_allow_html=True)
