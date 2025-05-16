from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Replace with your actual endpoints and keys
AI_API_URL = 'http://www.omdbapi.com/'
OMDB_API_KEY = "[REDACTED]"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_movies', methods=['POST'])
def get_movies():
    genre = request.form.get('genre')
    rating = request.form.get('rating')

    if not genre or not rating:
        return jsonify({"error": "Genre and rating are required."}), 400

    # Step 1: Query AI API
    params = {
        "genre": genre.lower(),
        "min_rating": rating
    }

    try:
        ai_response = requests.get(AI_API_URL, params=params, timeout=5)
        ai_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to get response from AI API"}), 500

    ai_data = ai_response.json()

    posters = []

    # Step 2: Fetch posters using IMDb ID
    for movie in ai_data:
        imdb_id = movie.get("tt3796198")
        title = movie.get("original_title")

        if not imdb_id:
            continue

        try:
            omdb_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
            omdb_resp = requests.get(omdb_url, timeout=5)
            omdb_resp.raise_for_status()
            data = omdb_resp.json()

            poster_url = data.get("Poster", "")
            posters.append({
                "title": title,
                "poster": poster_url if poster_url != "N/A" else ""
            })

        except requests.exceptions.RequestException:
            posters.append({
                "title": title,
                "poster": ""
            })

    return jsonify(posters)

if __name__ == '__main__':
    app.run(debug=True)
