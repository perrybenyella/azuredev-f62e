
import json
import os
import base64
import random
from openai import AzureOpenAI

endpoint = os.getenv("ENDPOINT_URL", "https://perrybenyella-1685-resource.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o-mini")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "REPLACE_WITH_YOUR_KEY_VALUE_HERE")

# Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2025-01-01-preview",
)

# IMAGE_PATH = "YOUR_IMAGE_PATH"
# encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')

def get_completion_from_messages(messages, model="gpt-4o", temperature=0.7):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message.content 

# Generate a list of 30 movies across genres with random ratings
genres = ["Action", "Drama", "Comedy", "Sci-Fi", "Horror"]

movie_titles = {
    "Action": ["Mad Max", "John Wick", "Die Hard", "Gladiator", "Inception", "The Dark Knight"],
    "Drama": ["The Shawshank Redemption", "Forrest Gump", "The Godfather", "Fight Club", "12 Angry Men", "The Green Mile"],
    "Comedy": ["Superbad", "Step Brothers", "The Hangover", "Anchorman", "Bridesmaids", "The Grand Budapest Hotel"],
    "Sci-Fi": ["Interstellar", "The Matrix", "Blade Runner", "Arrival", "Dune", "Ex Machina"],
    "Horror": ["The Conjuring", "Get Out", "A Quiet Place", "Hereditary", "It", "The Babadook"]
}


movie_db = {}
for genre in genres:
    movie_db[genre] = [{"title": title, "rating": round(random.uniform(1, 10), 1)} for title in movie_titles[genre]]


# Initialize conversation
messages = [{'role': 'system', 'content': 'You are a helpful movie recommendation assistant.'}]
watchlist = []


# Start chat loop
print("Welcome to MovieBot! Type 'done' to finish and see your watchlist.\n")



# messages =  [  
# {'role':'system', 'content':'You are friendly chatbot.'},
# {'role':'user', 'content':'Hi, my name is Isa'},
# {'role':'assistant', 'content': "Hi Isa! It's nice to meet you. \
# Is there anything I can help you with today?"},
# {'role':'user', 'content':'Yes, you can remind me, What is my name?'}  ]
# response = get_completion_from_messages(messages, temperature=1)
# print(response)   
    
try:
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['done', 'exit', 'quit']:
            break

        messages.append({'role': 'user', 'content': user_input})
        assistant_reply = get_completion_from_messages(messages)
        print(f"Bot: {assistant_reply}")
        messages.append({'role': 'assistant', 'content': assistant_reply})

        # Try to extract genre and rating from user input
        for genre in genres:
            if genre.lower() in user_input.lower():
                try:
                    rating = float([word for word in user_input.split() if word.replace('.', '', 1).isdigit()][0])
                except IndexError:
                    rating = 0
                recommended = [m for m in movie_db[genre] if m["rating"] >= rating]
                if recommended:
                    print(f"\nRecommended {genre} movies with rating >= {rating}:")
                    for idx, movie in enumerate(recommended):
                        print(f"{idx+1}. {movie['title']} (Rating: {movie['rating']})")
                    selection = input("Enter the number of the movie to add to your watchlist (or press Enter to skip): ")
                    if selection.isdigit():
                        selected_movie = recommended[int(selection)-1]
                        selected_movie["genre"] = genre
                        watchlist.append(selected_movie)
                        print(f"'{selected_movie['title']}' added to your watchlist.\n")
                else:
                    print(f"No {genre} movies found with rating >= {rating}.\n")
except KeyboardInterrupt:
    print("\nExiting MovieBot...")

# Finalize watchlist
final_output = {
    "watchlist": watchlist,
    "total_movies": len(watchlist)
}

print("\n🎬 Your Final Watchlist:")
print(json.dumps(final_output, indent=2))
