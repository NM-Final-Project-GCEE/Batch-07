from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MultiLabelBinarizer

# Load your dataset
df = pd.read_csv('dataset.csv')

# Prepare the data
df['genres_list'] = df['genres'].str.lower().str.split('|')
df['cast_size'] = df['cast'].apply(lambda x: len(x.split('|')) if isinstance(x, str) else 0)

# Features and encoding
features = ['popularity', 'budget', 'revenue', 'runtime', 'vote_count', 'cast_size']
X = df[features].copy()

mlb = MultiLabelBinarizer()
genres_encoded = mlb.fit_transform(df['genres_list'])
genres_df = pd.DataFrame(genres_encoded, columns=mlb.classes_)
X = pd.concat([X.reset_index(drop=True), genres_df.reset_index(drop=True)], axis=1)

# Target variable
y = df['vote_average']

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Predict ratings
df['predicted_rating'] = model.predict(X)

# Flask app
app = Flask(__name__)

@app.route('/recommend', methods=['GET'])
def recommend():
    genre = request.args.get('genre', '').lower()
    min_rating = float(request.args.get('min_rating', 0))

    if genre not in mlb.classes_:
        return jsonify({"error": f"Genre '{genre}' not found in model."}), 400

    # Filter by genre
    genre_mask = genres_df[genre] == 1
    filtered = df[genre_mask]

    # Filter by rating
    filtered = filtered[filtered['predicted_rating'] >= min_rating]

    # Return top 10
    top_movies = filtered[['original_title', 'predicted_rating']] \
        .sort_values(by='predicted_rating', ascending=False) \
        .head(10)

    return jsonify(top_movies.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
