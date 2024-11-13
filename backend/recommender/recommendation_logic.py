# import pymongo
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.feature_extraction.text import TfidfVectorizer
# import numpy as np
# from bson import ObjectId
# from pymongo import MongoClient

# # MongoDB setup
# client = MongoClient("mongodb://localhost:27017/")
# db = client['AITubeDatabase']
# tools_collection = db['AITools']
# users_collection = db['Users']
# interactions_collection = db['UserToolInteractions']


# # Cache setup (using dictionary for demonstration, replace with Redis in production)
# cache = {}

# # Utility function to generate a TagsVector at runtime
# def generate_tags_vector(category, minidesc):
#     text = f"{category} {minidesc}"
#     vectorizer = TfidfVectorizer(stop_words='english')
#     tfidf_matrix = vectorizer.fit_transform([text])
#     return tfidf_matrix.toarray()

# # Content-based filtering with similarity matching
# def content_based_recommendations(user):
#     # Get user's preferred category and tool interaction history
#     preferred_categories = [cat.lower() for cat in user['Preferences'].get('PreferredCategory', [])]
    
#     # Fetch all tools
#     all_tools = list(tools_collection.find())
#     if not all_tools:
#         print("No tools available for recommendation.")
#         return []
    
#     # Generate the tags vector for all tools
#     tools_data = []
#     for tool in all_tools:
#         tool_tags_vector = generate_tags_vector(tool['Category'], tool['Minidesc'])
#         tools_data.append({
#             'ToolID': tool['ToolID'],
#             'Title': tool['Title'],
#             'Category': tool['Category'],
#             'TagsVector': tool_tags_vector,
#             'PopularityScore': tool['PopularityScore']
#         })
    
#     # Compute cosine similarity for the tools based on the TagsVector and preferred categories
#     best_tools = []
#     for tool in tools_data:
#         # Loose matching by checking partial category matches
#         if any(pref in tool['Category'].lower() for pref in preferred_categories):
#             best_tools.append(tool)
    
#     # Sort best tools by similarity score (popularity or category similarity)
#     best_tools_sorted = sorted(best_tools, key=lambda x: x['PopularityScore'], reverse=True)
    
#     return best_tools_sorted[:10]  # Return top 10 tools

# # Collaborative filtering based on user interactions (User-User Collaborative Filtering)
# def collaborative_filtering(user):
#     # Get the user's interaction history (Tools they liked/viewed/shared)
#     user_history = user['InteractionHistory']
    
#     # Find users with similar interaction histories
#     all_users = list(users_collection.find())
#     similar_users = []
    
#     for other_user in all_users:
#         if other_user['UserID'] != user['UserID']:
#             # Simple similarity check based on overlapping interactions
#             common_tools = set(tool['ToolID'] for tool in user_history).intersection(
#                 set(tool['ToolID'] for tool in other_user['InteractionHistory']))
#             if common_tools:
#                 similar_users.append(other_user)
    
#     # Get tools interacted by similar users but not by the target user
#     recommended_tools = set()
#     for similar_user in similar_users:
#         for interaction in similar_user['InteractionHistory']:
#             if interaction['ToolID'] not in set(tool['ToolID'] for tool in user_history):
#                 recommended_tools.add(interaction['ToolID'])
    
#     # Fetch tool details for recommendations
#     recommendations = []
#     for tool_id in recommended_tools:
#         tool = tools_collection.find_one({"ToolID": tool_id})
#         if tool:
#             recommendations.append(tool)
    
#     return recommendations[:10]  # Return top 10 tools

# # Caching mechanism to store recommendations
# def get_cached_recommendations(user_id):
#     cache_key = f"recommendations_{user_id}"
#     return cache.get(cache_key, None)

# def set_cached_recommendations(user_id, recommendations):
#     cache_key = f"recommendations_{user_id}"
#     cache[cache_key] = recommendations

# # Final function to get recommendations
# def get_final_recommendations(user_id, top_n=10):
#     # Check if recommendations are cached
#     cached_recommendations = get_cached_recommendations(user_id)
#     if cached_recommendations:
#         print(f"Returning cached recommendations for user {user_id}.")
#         return cached_recommendations
    
#     # Get user details
#     user = users_collection.find_one({"UserID": user_id})
#     if not user:
#         print(f"User {user_id} not found.")
#         return []
    
#     # Content-based filtering
#     content_based_recs = content_based_recommendations(user)
#     if content_based_recs:
#         print(f"Content-based recommendations found for user {user_id}:")
#         print([tool['Title'] for tool in content_based_recs])
#     else:
#         print(f"No content-based recommendations found for user {user_id}")
    
#     # Collaborative filtering
#     collaborative_recs = collaborative_filtering(user)
#     if collaborative_recs:
#         print(f"Collaborative filtering recommendations found for user {user_id}:")
#         print([tool['Title'] for tool in collaborative_recs])
#     else:
#         print(f"No collaborative filtering recommendations found for user {user_id}")
    
#     # Combine content-based and collaborative recommendations
#     final_recommendations = content_based_recs[:top_n] + collaborative_recs[:top_n]
#     final_recommendations = final_recommendations[:top_n]  # Limit to top N results
    
#     # Cache the results
#     set_cached_recommendations(user_id, final_recommendations)
    
#     return final_recommendations

# # # Example usage
# # user_id = "user_00024"
# # recommendations = get_final_recommendations(user_id, top_n=10)
# # if recommendations:
# #     print(f"Final recommendations for user {user_id}:")
# #     for tool in recommendations:
# #         print(f"{tool['Title']} - Popularity: {tool['PopularityScore']}")
# # else:
# #     print("No recommendations found.")
# #kaggala
# #data.gov
# #mendeley
import pymongo
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['AITubeDatabase']
tools_collection = db['AITools']
users_collection = db['Users']
interactions_collection = db['UserToolInteractions']

# Cache setup (using a dictionary for demonstration; replace with Redis in production)
cache = {}

# Utility function to generate a TagsVector based on category and description
def generate_tags_vector(category, minidesc):
    text = f"{category} {minidesc}"
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text])
    return tfidf_matrix.toarray()

# Content-based filtering for recommendations
def content_based_recommendations(user):
    preferred_categories = [cat.lower() for cat in user['Preferences'].get('PreferredCategory', [])]
    all_tools = list(tools_collection.find())
    if not all_tools:
        return []
    
    tools_data = []
    for tool in all_tools:
        tool_tags_vector = generate_tags_vector(tool['Category'], tool['Minidesc'])
        tools_data.append({
            'ToolID': tool['ToolID'],
            'Title': tool['Title'],
            'Category': tool['Category'],
            'TagsVector': tool_tags_vector,
            'PopularityScore': tool['PopularityScore']
        })

    best_tools = [tool for tool in tools_data if any(pref in tool['Category'].lower() for pref in preferred_categories)]
    best_tools_sorted = sorted(best_tools, key=lambda x: x['PopularityScore'], reverse=True)
    return best_tools_sorted[:10]

# Collaborative filtering based on user interactions
def collaborative_filtering(user):
    user_history = user['InteractionHistory']
    all_users = list(users_collection.find())
    
    similar_users = []
    for other_user in all_users:
        if other_user['UserID'] != user['UserID']:
            common_tools = set(tool['ToolID'] for tool in user_history).intersection(
                set(tool['ToolID'] for tool in other_user['InteractionHistory']))
            if common_tools:
                similar_users.append(other_user)
    
    recommended_tools = set()
    for similar_user in similar_users:
        for interaction in similar_user['InteractionHistory']:
            if interaction['ToolID'] not in set(tool['ToolID'] for tool in user_history):
                recommended_tools.add(interaction['ToolID'])
    
    recommendations = []
    for tool_id in recommended_tools:
        tool = tools_collection.find_one({"ToolID": tool_id})
        if tool:
            recommendations.append(tool)
    
    return recommendations[:10]

# Caching functions
def get_cached_recommendations(user_id):
    cache_key = f"recommendations_{user_id}"
    return cache.get(cache_key, None)

def set_cached_recommendations(user_id, recommendations):
    cache_key = f"recommendations_{user_id}"
    cache[cache_key] = recommendations

# Main function to get recommendations
def get_final_recommendations(user_id, top_n=10):
    cached_recommendations = get_cached_recommendations(user_id)
    if cached_recommendations:
        return cached_recommendations
    
    user = users_collection.find_one({"UserID": user_id})
    if not user:
        return []
    
    content_based_recs = content_based_recommendations(user)
    collaborative_recs = collaborative_filtering(user)
    
    final_recommendations = content_based_recs[:top_n] + collaborative_recs[:top_n]
    final_recommendations = final_recommendations[:top_n]
    
    set_cached_recommendations(user_id, final_recommendations)
    return final_recommendations
