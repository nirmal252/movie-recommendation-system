import streamlit as st
import pickle
import requests
import gzip
import gdown
import os

# TMDb API Setup
TMDB_API_KEY = "26902b308d3d28621368340f24be625a"

def fetch_poster(movie_title):
    try:
        base_url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": movie_title,
            "include_adult": False,
            "language": "en-US",
            "page": 1
        }
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            return "https://via.placeholder.com/200x300.png?text=API+Error"

        data = response.json()
        results = data.get("results", [])

        # Try exact match first
        for result in results:
            if result.get("title", "").lower() == movie_title.lower():
                poster_path = result.get("poster_path")
                if poster_path:
                    return f"https://image.tmdb.org/t/p/w500{poster_path}"

        # Fallback to first poster
        for result in results:
            poster_path = result.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"

        return "https://via.placeholder.com/200x300.png?text=No+Poster"
    except Exception:
        return "https://via.placeholder.com/200x300.png?text=Error"

# ⬇️ Download .gz files from Google Drive
def download_and_load_pickle(gdrive_file_id, local_filename):
    if not os.path.exists(local_filename):
        url = f"https://drive.google.com/uc?id={gdrive_file_id}"
        gdown.download(url, local_filename, quiet=False)
    with gzip.open(local_filename, "rb") as f:
        return pickle.load(f)

# 🔁 Replace with your actual Google Drive file IDs
MOVIES_FILE_ID = "12oQkGi3_DZVxVSrfe-QVB9dbrocsQi4V"         # e.g. '1AbcXyz1234567890'
SIMILARITY_FILE_ID = "10KqR9EwpZA49J2qUnpoDLtkJFKQb8B87" # e.g. '1DefXyz9876543210'

# 📥 Load data
new_df = download_and_load_pickle(MOVIES_FILE_ID, "movies.pkl.gz")
similarity = download_and_load_pickle(SIMILARITY_FILE_ID, "similarity.pkl.gz")

# 🎯 Recommendation Logic
def recommend(movie):
    movie_index = new_df[new_df["title"] == movie].index[0]
    distances = similarity[movie_index]
    movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_indices:
        title = new_df.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))

    return recommended_movies, recommended_posters

# 🎬 Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System")

movie_list = new_df["title"].values
selected_movie = st.selectbox("Choose a movie to get similar recommendations", movie_list)

if st.button("Show Recommendations"):
    names, posters = recommend(selected_movie)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])
