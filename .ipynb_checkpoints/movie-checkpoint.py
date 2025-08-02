import pickle
import requests
import gzip
import gdown

# TMDb API Setup

import requests

TMDB_API_KEY = "26902b308d3d28621368340f24be625a"

def fetch_poster(movie_title):
    print(f"\nFetching poster for: {movie_title}")

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
        print(f"Status code: {response.status_code}")

        if response.status_code != 200:
            print(f" API Error: {response.text}")
            return "https://via.placeholder.com/200x300.png?text=API+Error"

        data = response.json()
        results = data.get("results", [])
        print(f" Results found: {len(results)}")

        # Step 1: Try exact match first (case-insensitive)
        for result in results:
            if result.get("title", "").lower() == movie_title.lower():
                poster_path = result.get("poster_path")
                if poster_path:
                    full_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    print(f" Exact match poster: {full_url}")
                    return full_url
                else:
                    print(f" Exact title match found but no poster.")

        # Step 2: Fallback to first available poster
        for i, result in enumerate(results):
            print(f"  🔹 Result {i+1}: {result.get('title')} (ID: {result.get('id')})")
            poster_path = result.get("poster_path")
            if poster_path:
                full_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                print(f" Fallback poster: {full_url}")
                return full_url
            else:
                print(f" No poster in fallback result {i+1}")

        print("All results had no poster paths.")
        return "https://via.placeholder.com/200x300.png?text=No+Poster"

    except Exception as e:
        print(f" Exception: {str(e)}")
        return "https://via.placeholder.com/200x300.png?text=Error"



# Load Preprocessed Data
with gzip.open("movies.pkl.gz", "rb") as f:
    new_df = pickle.load(f)

with gzip.open("similarity.pkl.gz", "rb") as f:
    similarity = pickle.load(f)
    

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

    # Display 5 recommendations in columns
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