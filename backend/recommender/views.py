# from django.shortcuts import render
# from django.http import JsonResponse
# from pymongo import MongoClient
# from .recommendation_logic import get_final_recommendations  # Import recommendation functions

# # MongoDB setup
# client = MongoClient("mongodb://localhost:27017/")
# db = client["AITubeDatabase"]
# # Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from pymongo import MongoClient
from .recommendation_logic import get_final_recommendations  # Import recommendation function

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["AITubeDatabase"]

# View to get recommendations for a user
def get_recommendations(request, user_id):
    """
    Django view to get AI tool recommendations for a specific user based on their preferences and interaction history.
    
    Args:
        request (HttpRequest): The HTTP request object.
        user_id (str): The ID of the user for whom to generate recommendations.
    
    Returns:
        JsonResponse: JSON response containing the recommended tools.
    """
    try:
        # Fetch recommendations using the final recommendation function
        recommendations = get_final_recommendations(user_id, top_n=10)

        # Format response
        response_data = {
            "status": "success",
            "user_id": user_id,
            "recommendations": [
                {
                    "ToolID": tool.get("ToolID"),
                    "Title": tool.get("Title"),
                    "Category": tool.get("Category"),
                    "PopularityScore": tool.get("PopularityScore"),
                    "Minidesc": tool.get("Minidesc")
                }
                for tool in recommendations
            ]
        }

        # Return recommendations in JSON format
        return JsonResponse(response_data, status=200)

    except Exception as e:
        # Handle errors and provide feedback
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
