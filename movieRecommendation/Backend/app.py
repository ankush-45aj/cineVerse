from flask import Flask, request, jsonify
from flask_cors import CORS
from backend import MovieRecommendationSystem
from db import users_collection

app = Flask(__name__)
CORS(app) # Crucial for connecting to a frontend

# 1. Initialize your Brain
bot = MovieRecommendationSystem(
    imdb_dataset_path="movie_dataset.csv", 
    user_history_path="User_history.csv", 
    user_searches_path="User_searches.csv",
    db_collection=users_collection
)

# 2. Define the "Ears" (Routes) that match your 404 errors

@app.route('/top_rated_movies', methods=['GET'])
def top_rated():
    return jsonify(bot.top_rated_movies())

@app.route('/recommend_movies', methods=['GET'])
def recommend():
    # Calling the recommendation logic
    return jsonify(bot.recommend_movies())

@app.route('/movie_filter_by_category', methods=['GET'])
def filter_category():
    category = request.args.get('category')
    if not category:
        return jsonify({"error": "No category provided"}), 400
    return jsonify(bot.movie_category_filter(category))
# Add these inside app.py



@app.route('/recommendMoviesByname', methods=['GET'])
def recommend_by_name():
    movie_name = request.args.get('movie_name')
    if not movie_name:
        return jsonify({"error": "Movie name is required"}), 400
    # Calls the logic in your backend.py
    return jsonify(bot.recommend_movies_based_on_movie_name(movie_name))

@app.route('/record_user_history', methods=['POST'])
def record_history():
    data = request.json
    movie_name = data.get('movie_name')
    return jsonify({"message": bot.record_user_history(movie_name)})

@app.route('/user_history', methods=['GET'])
def get_history():
    return jsonify(bot.get_user_history())
@app.route('/user_searches', methods=['GET'])
def get_searches_route(): # Change the function name to avoid the conflict
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400
    return jsonify(bot.get_user_searches(username))
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    return jsonify(bot.login(data.get('username'), data.get('password')))

if __name__ == '__main__':
    app.run(debug=True, port=5000)