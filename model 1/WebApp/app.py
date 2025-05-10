from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Your actual AI model endpoint (GET-based)
AI_API_URL = '[REDATED]/recommend'
OMDB_API_KEY = '[REDATED]'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_movies', methods=['POST'])
def get_movies():
    genre = request.form.get('genre')
    rating = request.form.get('rating')

    # Step 1: Call your AI API using GET
    params = {
        "genre": genre.lower(),
        "min_rating": rating
    }
    ai_response = requests.get(AI_API_URL, params=params)

    if ai_response.status_code != 200:
        return jsonify({"error": "Failed to get response from AI API"}), 500

    # Step 2: Extract movie names from AI model response
    # Expected format: [{ "original_title": "Movie Name", ... }, ...]
    ai_data = ai_response.json()
    movie_titles = [movie.get("original_title") for movie in ai_data if movie.get("original_title")]

    # Step 3: Get posters from OMDb
    posters = []
    for title in movie_titles:
        omdb_resp = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}")
        data = omdb_resp.json()
        poster_url = data.get("Poster", "")
        posters.append({
            "title": title,
            "poster": poster_url if poster_url != "N/A" else ""
        })

    return jsonify(posters)

if __name__ == '__main__':
    app.run(debug=True)
