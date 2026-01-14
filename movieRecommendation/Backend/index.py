import pandas as pd
import requests
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from auth import AuthService
from db import users_collection

class MovieRecommendationSystem:
    def __init__(self, imdb_dataset_path, user_history_path, user_searches_path):
        # Load datasets
        self.imdb_dataset = pd.read_csv(imdb_dataset_path)
        self.user_history = pd.read_csv(user_history_path, encoding="latin1")
        self.user_searches = pd.read_csv(user_searches_path, encoding="latin1")
        self.logged_in_user = None
        self.tf_idf = TfidfVectorizer()

    # ================= AUTH =================
    def login(self, username, password):
        # Call the AuthService to handle hashed password checking
        result = AuthService.login_user(username, password)
        if "message" in result:
            self.logged_in_user = username
        return result

    # ================= RECOMMENDATION LOGIC =================
    def top_rated_movies(self):
        top_movies = self.imdb_dataset.sort_values(
            by="imdb_score", ascending=False
        ).head(10)
        
        results = {}
        for i, (_, movie) in enumerate(top_movies.iterrows()):
            data = movie.to_dict()
            data["poster_url"] = self.get_poster_url_from_title(data["movie_title"])
            results[i] = data
        return results

    def get_poster_url_from_title(self, movie_title):
        api_key = "ad45e532"
        row = self.imdb_dataset[self.imdb_dataset["movie_title"].str.contains(movie_title, case=False, na=False)]
        if row.empty: return None
        try:
            imdb_url = row.iloc[0]["movie_imdb_link"]
            imdb_id = imdb_url.split("/")[4]
            url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}"
            response = requests.get(url)
            return response.json().get("Poster")
        except:
            return None

# ================= MAIN EXECUTION =================
if __name__ == "__main__":
    # Ensure these file names match your folder exactly
    dataset_file = "movie_dataset.csv" 
    
    try:
        bot = MovieRecommendationSystem(dataset_file, "User_history.csv", "User_searches.csv")
        print("--- Movie System Initialized ---")
        
        print("1. Login\n2. Register")
        choice = input("Select: ")
        u = input("Username: ")
        p = input("Password: ")

        if choice == "2":
            print(AuthService.register_user(u, p))
        
        # Now try to login
        login_res = bot.login(u, p)
        print(login_res)

        if "message" in login_res:
            print(f"\nWelcome, {u}! Top Movies for you:")
            movies = bot.top_rated_movies()
            for i in movies:
                print(f"- {movies[i]['movie_title']} (Rating: {movies[i]['imdb_score']})")

    except Exception as e:
        print(f"Startup Error: {e}")