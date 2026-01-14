import pandas as pd
import requests
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor

class MovieRecommendationSystem:
    def __init__(self, imdb_dataset_path, user_history_path, user_searches_path, db_collection):
        self.users_collection = db_collection
        
        # Load Data
        self.imdb_dataset = pd.read_csv(imdb_dataset_path)
        self.user_history = pd.read_csv(user_history_path, encoding="latin1")
        self.user_searches = pd.read_csv(user_searches_path, encoding="latin1")
        self.logged_in_user = None
        
        # --- SPEED SETUP: Pre-calculate TF-IDF Matrix ---
        self.tf_idf = TfidfVectorizer(stop_words='english')
        self.imdb_dataset['features'] = (
            self.imdb_dataset['director_name'].fillna('') + ' ' +
            self.imdb_dataset['genres'].fillna('') + ' ' +
            self.imdb_dataset['plot_keywords'].fillna('')
        ).str.lower()
        self.tfidf_matrix = self.tf_idf.fit_transform(self.imdb_dataset['features'])

    # ================= AUTH =================
    def login(self, username, password):
        user = self.users_collection.find_one({"username": username})
        if user and user["password"] == password:
            self.logged_in_user = username
            return {"message": "Login successful", "user": username}
        return {"error": "Invalid username or password"}

    # ================= RECOMMENDATIONS (The "recommend" route fix) =================
    def recommend_movies(self):
        """Standard recommendation based on user history or top rated."""
        if not self.logged_in_user:
            return {"error": "Please login first"}

        user_history = self.user_history[self.user_history["Username"] == self.logged_in_user]
        
        if user_history.empty:
            return self.top_rated_movies()
        
        # Recommend based on the last movie they watched
        last_movie = user_history.iloc[-1]["movie_title"]
        return self.recommend_movies_based_on_movie_name(last_movie)

    def recommend_movies_based_on_movie_name(self, movie_name):
        """Fast content-based filtering."""
        titles = self.imdb_dataset["movie_title"].str.lower().str.strip()
        query = movie_name.lower().strip()
        
        if query not in titles.values:
            return {"error": "Movie not found"}

        idx = titles[titles == query].index[0]
        # Calculate similarity instantly using pre-computed matrix
        sim_scores = cosine_similarity(self.tfidf_matrix[idx], self.tfidf_matrix).flatten()
        related_indices = sim_scores.argsort()[-11:-1][::-1]
   

        # ... (Keep your existing __init__ and recommendation code)

    # ================= HISTORY =================
    def record_user_history(self, movie_name):
        """Records a movie click into the CSV for personalized recommendations."""
        if not self.logged_in_user:
            return "Please login first"

        # Find the movie in the dataset
        movie = self.imdb_dataset[
            self.imdb_dataset["movie_title"].str.contains(movie_name, case=False, na=False)
        ]

        if movie.empty:
            return "Movie not found"

        data = movie.iloc[0].to_dict()
        data["Username"] = self.logged_in_user

        # Prevent duplicate history entries
        user_hist = self.user_history[self.user_history["Username"] == self.logged_in_user]
        if movie_name.lower().strip() in user_hist["movie_title"].str.lower().str.strip().values:
            return "Movie already exists in history"

        # Append to DataFrame and save
        self.user_history = pd.concat([self.user_history, pd.DataFrame([data])], ignore_index=True)
        self.user_history.to_csv("User_history.csv", index=False, encoding="latin1")
        return "Movie added to history"

    def get_user_history(self):
        """Fetches the watch history for the currently logged-in user."""
        if not self.logged_in_user:
            return {"error": "No user logged in"}

        history = self.user_history[
            self.user_history["Username"] == self.logged_in_user
        ].tail(10) # Get last 10 watched

        return self._get_movie_details_batch(history.index)

    # ================= SEARCH =================
    def get_user_searches(self, username):
        """Fixes the AttributeError by providing the correct method name."""
        searches = self.user_searches[
            self.user_searches["Username"] == username
        ]

        if searches.empty:
            return []

        # Return a unique list of movie titles searched by the user
        return searches["movie_title"].unique().tolist()

    # (Ensure your _get_movie_details_batch and other helper methods are below)
        return self._get_movie_details_batch(related_indices)

    # ================= UTILS =================
    def top_rated_movies(self):
        top_indices = self.imdb_dataset.sort_values(by="imdb_score", ascending=False).head(10).index
        return self._get_movie_details_batch(top_indices)

    def movie_category_filter(self, category):
        filtered_indices = self.imdb_dataset[
            self.imdb_dataset["genres"].str.contains(category, case=False, na=False)
        ].head(10).index
        return self._get_movie_details_batch(filtered_indices)

    def _get_movie_details_batch(self, indices):
        """Internal helper to fetch movie data and posters in parallel."""
        results = {}
        movies_list = [self.imdb_dataset.iloc[i].to_dict() for i in indices]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            posters = list(executor.map(lambda m: self.get_poster_url(m), movies_list))

        for i, movie in enumerate(movies_list):
            movie["poster_url"] = posters[i]
            results[i] = movie
        return results

    def get_poster_url(self, movie_data):
        api_key = "ad45e532"
        try:
            imdb_id = movie_data["movie_imdb_link"].split("/")[4]
            url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}"
            return requests.get(url, timeout=1).json().get("Poster")
        except:
            return None

    # ... keep your other methods, but ensure they use self.tfidf_matrix logic

    # ================= UTILS =================
    @staticmethod
    def clean_movie_title(title):
        return re.sub(r"[^\x00-\x7F]+", "", title).strip()
