import pickle
import streamlit as st
import requests
import time
import base64
from streamlit_lottie import st_lottie
import json

# Page configuration
st.set_page_config(
    page_title="FilmFinder - Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to enhance the UI
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 28px;
        font-weight: bold;
        color: #1E88E5;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .movie-title {
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        height: 40px;
    }
    .movie-score {
        font-size: 14px;
        text-align: center;
        color: #4CAF50;
        margin-top: 5px;
    }
    .movie-card {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 10px;
        text-align: center;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .movie-card:hover {
        transform: scale(1.03);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 20px;
        padding: 10px 24px;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #E53935;
        border: none;
    }
    .stSelectbox>div>div {
        background-color: #f9f9f9;
        border-radius: 20px;
        padding: 5px;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        font-size: 14px;
        color: #666;
        border-top: 1px solid #eee;
    }
    .sidebar .css-1d391kg {
        background-color: #f5f5f5;
    }
    .recommended-section {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Function to load and display Lottie animations
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Function to fetch movie poster and details
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=e37412bf776f29cb3da34a9645c47a3e&language=en-US"
        data = requests.get(url, timeout=10)
        data.raise_for_status()
        data = data.json()
        
        details = {
            'title': data['title'],
            'poster_path': f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data['poster_path'] else "https://via.placeholder.com/500x750?text=Poster+Not+Found",
            'vote_average': data['vote_average'],
            'release_date': data.get('release_date', 'N/A')[:4] if data.get('release_date') else 'N/A',
            'overview': data.get('overview', 'No overview available.')
        }
        return details
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for movie ID {movie_id}: {e}")
        return {
            'title': 'Data Not Available',
            'poster_path': "https://via.placeholder.com/500x750?text=Poster+Not+Found",
            'vote_average': 'N/A',
            'release_date': 'N/A',
            'overview': 'No overview available.'
        }

# Function to recommend similar movies
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movies = []
        
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movie_id
            similarity_score = round(i[1] * 100, 1)  # Convert similarity to percentage
            movie_details = fetch_movie_details(movie_id)
            movie_details['similarity'] = similarity_score
            recommended_movies.append(movie_details)
            time.sleep(0.5)  # Reduced sleep time a bit
            
        return recommended_movies
    except Exception as e:
        st.error(f"Error in recommendation process: {e}")
        return []

# Load movie list and similarity data
@st.cache_data
def load_data():
    try:
        movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
        similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))
        return movies, similarity
    except Exception as e:
        st.error(f"Error loading data files: {e}")
        return None, None

movies, similarity = load_data()

# Sidebar content
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/film-reel.png", width=100)
    st.markdown("<h2 style='text-align: center;'>FilmFinder</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Add a lottie animation to the sidebar
    lottie_movie = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_khzniaya.json")
    st_lottie(lottie_movie, height=200, key="movie_animation")
    
    st.markdown("### About")
    st.info("FilmFinder uses machine learning to recommend movies based on your preferences. Simply select a movie you like, and our system will suggest similar films you might enjoy!")
    
    st.markdown("### How it works")
    st.markdown("""
    1. Select a movie you enjoy
    2. Click 'Find Similar Movies'
    3. Discover new films to watch!
    """)
    
    st.markdown("---")
    st.markdown("### Created with")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://img.icons8.com/color/48/000000/python.png", width=40)
    with col2:
        st.image("https://img.icons8.com/color/48/000000/machine-learning.png", width=40)
    with col3:
        st.image("https://img.icons8.com/color/48/000000/movie.png", width=40)

# Main Content
st.markdown("<h1 class='main-header'>🎬 FilmFinder: Movie Recommendation System</h1>", unsafe_allow_html=True)

# Show information about selected movie
if movies is not None:
    # Search box with larger width
    col1, col2 = st.columns([3, 1])
    with col1:
        movie_list = movies['title'].values
        selected_movie = st.selectbox("🔍 Search for a movie you like:", movie_list)
    with col2:
        find_button = st.button('🔍 Find Similar Movies')
    
    # Display selected movie info
    if selected_movie:
        try:
            selected_movie_index = movies[movies['title'] == selected_movie].index[0]
            selected_movie_id = movies.iloc[selected_movie_index].movie_id
            selected_movie_details = fetch_movie_details(selected_movie_id)
            
            st.markdown("---")
            st.markdown("<h2 class='sub-header'>Selected Movie</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(selected_movie_details['poster_path'], width=230, caption=f"Rating: ⭐ {selected_movie_details['vote_average']}/10")
            with col2:
                st.markdown(f"### {selected_movie_details['title']} ({selected_movie_details['release_date']})")
                st.markdown(f"**Rating:** ⭐ {selected_movie_details['vote_average']}/10")
                st.markdown("### Overview")
                st.markdown(selected_movie_details['overview'])
        except Exception as e:
            st.error(f"Error displaying selected movie: {e}")

    # Show recommendations when button is clicked
    if find_button:
        with st.spinner('Finding your perfect movie matches...'):
            recommended_movies = recommend(selected_movie)
            
            if recommended_movies:
                st.markdown("---")
                st.markdown("<div class='recommended-section'><h2 class='sub-header'>📋 Recommended Movies For You</h2>", unsafe_allow_html=True)
                
                cols = st.columns(5)
                for i, movie in enumerate(recommended_movies):
                    with cols[i]:
                        st.markdown(f"<div class='movie-card'>", unsafe_allow_html=True)
                        st.image(movie['poster_path'], use_column_width=True)
                        st.markdown(f"<div class='movie-title'>{movie['title']} ({movie['release_date']})</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='movie-score'>⭐ {movie['vote_average']}/10</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='movie-score'>Match: {movie['similarity']}%</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("Failed to load movie data. Please check if the data files exist in the 'artifacts' directory.")

# Footer
st.markdown("---")
st.markdown("<div class='footer'>© 2025 FilmFinder - AI-Powered Movie Recommendation System | Icons by Icons8</div>", unsafe_allow_html=True)