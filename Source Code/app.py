from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Your actual AI model endpoint (GET-based)
AI_API_URL = 'http://127.0.0.1:5000/recommend'
OMDB_API_KEY = '[REDACTED]'

@app.route('/')
def home():
    return render_template('index2.html')


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

    # Step 2: Extract IMDb IDs from AI response
    ai_data = ai_response.json()
    print(ai_data)
    imdb_ids = [movie.get("imdb_id") for movie in ai_data if movie.get("imdb_id")]
    print(imdb_ids)

    # Step 3: Get posters from OMDb
    posters = []
    for imdb_id in imdb_ids:
        omdb_resp = requests.get(f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}")
        data = omdb_resp.json()
        print(data)
        poster_url = data.get("Poster", "")
        title = data.get("Title", imdb_id)
        posters.append({
            "title": title,
            "poster": poster_url if poster_url != "N/A" else ""
        })
    print(posters)

    return jsonify(posters)


if __name__ == '__main__':
    app.run(debug=True,port=8080)
