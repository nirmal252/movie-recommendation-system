import streamlit as st
import pickle
import requests
import gzip
import os
import gdown

# Google Drive file IDs
MOVIES_FILE_ID = "10KqR9EwpZA49J2qUnpoDLtkJFKQb8B87"
SIMILARITY_FILE_ID = "12oQkGi3_DZVxVSrfe-QVB9dbrocsQi4V"

# Download files if not present
def download_file_from_drive(file_id, output_path):
    if not os.path.exists(output_path):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_path, quiet=False)

download_file_from_drive(MOVIES_FILE_ID, "movies.pkl.gz")
download_file_from_drive(SIMILARITY_FILE_ID, "similarity.pkl.gz")

# Load Preprocessed Data
with gzip.open("movies.pkl.gz", "rb") as f:
    new_df = pickle.load(f)

with gzip.open("similarity.pkl.gz", "rb") as f:
    similarity = pickle.load(f)

# TMDB API
TMDB_API_KEY = "26902b308d3d28621368340f24be625a"

def fetch_poster(movie_title):
    base_url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_title,
        "include_adult": False,
        "language": "en-US",
        "page": 1
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        results = data.get("results", [])

        for result in results:
            if result.get("title", "").lower() == movie_title.lower():
                poster_path = result.get("poster_path")
                if poster_path:
                    return f"https://image.tmdb.org/t/p/w500{poster_path}"

        for result in results:
            poster_path = result.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"

        return "https://via.placeholder.com/200x300.png?text=No+Poster"
    except:
        return "https://via.placeholder.com/200x300.png?text=Error"

# Recommendation Logic
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

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System")

movie_list = new_df["title"].values
selected_movie = st.selectbox("Choose a movie to get similar recommendations", movie_list)

if st.button("Show Recommendations"):
    names, posters = recommend(selected_movie)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
