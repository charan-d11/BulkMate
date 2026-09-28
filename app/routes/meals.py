from flask import Blueprint, request, jsonify, session
from app import db
from app.models import Meal
from app.common.logger import logger
from datetime import date
from google import genai
import requests as http_req
import os
import json
from app.common.custom_exception import CustomException

bp = Blueprint('meals', __name__)


# ─── Helper: USDA API ───
# def fetch_from_usda(food_name):        # ✅ food_name comes as parameter
#     api_key    = os.environ.get("USDA_API_KEY")
#     search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
#     params     = {
#         "query":    food_name,
#         "api_key":  api_key,
#         "pageSize": 1,
#         "dataType": "Foundation,SR Legacy"
#     }
#     try:
#         res = http_req.get(search_url, params=params, timeout=5)
#         if res.status_code == 200:
#             foods = res.json().get("foods", [])
#             if not foods:
#                 return None
#             food      = foods[0]
#             nutrients = {n["nutrientName"]: n["value"]
#                         for n in food.get("foodNutrients", [])}
#             logger.info(f"USDA API success for '{food_name}': {nutrients}")
#             return {
#                 "calories": round(nutrients.get("Energy", 0), 1),
#                 "protein":  round(nutrients.get("Protein", 0), 1),
#                 "carbs":    round(nutrients.get("Carbohydrate, by difference", 0), 1),
#                 "fat":      round(nutrients.get("Total lipids (fat)", 0), 1),
#                 "source":   "usda"
#             }
        
#     except Exception as e:
#         logger.error(f"USDA API error for '{food_name}': {e}")
#     return None


# ─── Helper: Gemini Fallback ───
# def fetch_from_gemini(food_name):      # ✅ food_name comes as parameter
#     try:
#         client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
#         prompt = f"""
#         Estimate the nutritional values for: "{food_name}"
#         Respond ONLY in this exact JSON format, no extra text:
#         {{
#             "calories": 000,
#             "protein": 00,
#             "carbs": 00,
#             "fat": 00
#         }}
#         """
#         response = client.models.generate_content(
#             model="gemini-3.6-flash",
#             contents=prompt
#         )
#         text = response.text.strip().replace("```json", "").replace("```", "")
#         data = json.loads(text)
#         data["source"] = "gemini"
#         logger.warning(f"Used Gemini fallback for '{food_name}'")
#         return data
#     except Exception as e:
#         logger.error(f"Gemini fallback error for '{food_name}': {e}")
#     return None

def fetch_from_gemini(food_name):
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        prompt = f"""
        You are a precise nutrition calculator.
        
        Calculate the TOTAL nutritional values for: "{food_name}"
        
        IMPORTANT RULES:
        - Consider the EXACT quantity mentioned (e.g. 250g, 3 eggs, 1 cup)
        - Return TOTAL values, NOT per 100g values
        - Use standard cooked values unless raw is specified
        - Be as accurate as possible like a professional dietitian
        
        Respond ONLY in this exact JSON format, no extra text, no markdown:
        {{
            "calories": 000,
            "protein": 00.0,
            "carbs": 00.0,
            "fat": 00.0
        }}
        """
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        text = response.text.strip()
        # Clean any accidental markdown
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        data["source"] = "gemini"
        logger.info(f"Gemini nutrition fetched for '{food_name}': {data}")
        return data
    except Exception as e:
        logger.error(f"Gemini fetch error for '{food_name}': {e}")
        return None

# ─── Add Meal ───
@bp.route('/api/meal/add', methods=['POST'])
# def add_meal():
#     try:
#         user_id   = session.get('user_id')          # ✅ fetched from session
#         if not user_id:
#             return jsonify({"error": "Unauthorized"}), 401

#         food_name = request.json.get('food_name')   # ✅ fetched from request body
#         if not food_name:
#             return jsonify({"error": "Food name required"}), 400

#         nutrition = fetch_from_usda(food_name) or fetch_from_gemini(food_name)

#         if not nutrition:
#             return jsonify({"error": "Could not fetch nutrition data"}), 500

#         meal = Meal(
#             user_id   = user_id,
#             date      = date.today(),
#             food_name = food_name,
#             calories  = nutrition['calories'],
#             protein   = nutrition['protein'],
#             carbs     = nutrition['carbs'],
#             fat       = nutrition['fat']
#         )
#         db.session.add(meal)
#         db.session.commit()

#         logger.info(f"Meal added: user_id={user_id}, food={food_name}, cal={nutrition['calories']}, source={nutrition['source']}")
#         return jsonify({"message": "Meal added!", "food_name": food_name, "nutrition": nutrition}), 201
#     except Exception as e:
#         logger.error(f"Error adding meal: {e}")
#         raise CustomException("An error occurred while adding the meal.", e)


@bp.route('/api/meal/add', methods=['POST'])
def add_meal():
    user_id   = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    food_name = request.json.get('food_name')
    if not food_name:
        return jsonify({"error": "Food name required"}), 400

    # ✅ Gemini only — most accurate for natural language + quantities
    nutrition = fetch_from_gemini(food_name)

    if not nutrition:
        return jsonify({"error": "Could not calculate nutrition. Please try again!"}), 500

    meal = Meal(
        user_id   = user_id,
        date      = date.today(),
        food_name = food_name,
        calories  = nutrition['calories'],
        protein   = nutrition['protein'],
        carbs     = nutrition['carbs'],
        fat       = nutrition['fat']
    )
    db.session.add(meal)
    db.session.commit()

    logger.info(f"Meal added: user_id={user_id}, food={food_name}, cal={nutrition['calories']}")
    return jsonify({
        "message":   "Meal added!",
        "food_name": food_name,
        "nutrition": nutrition
    }), 201
# ─── Get Today's Meals ───
@bp.route('/api/meal/today', methods=['GET'])
def get_today_meals():
    try:
        user_id = session.get('user_id')            # ✅ fetched from session
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        meals = Meal.query.filter_by(user_id=user_id, date=date.today()).all()
        result = [{
            "id":        m.id,
            "food_name": m.food_name,
            "calories":  m.calories,
            "protein":   m.protein,
            "carbs":     m.carbs,
            "fat":       m.fat
        } for m in meals]
        logger.info(f"Fetched today's meals for user_id={user_id}: {len(result)} meals")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error fetching today's meals: {e}")
        raise CustomException("An error occurred while fetching today's meals.", e)


# ─── Delete Meal ───
@bp.route('/api/meal/delete/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    try:
        user_id = session.get('user_id')            # ✅ fetched from session
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        meal = Meal.query.filter_by(id=meal_id, user_id=user_id).first()
        if not meal:
            return jsonify({"error": "Meal not found"}), 404

        db.session.delete(meal)
        db.session.commit()
        logger.info(f"Meal deleted: id={meal_id} by user_id={user_id}")
        return jsonify({"message": "Meal deleted!"}), 200
    except Exception as e:
        logger.error(f"Error deleting meal id={meal_id}: {e}")
        raise CustomException("An error occurred while deleting the meal.", e)


# ─── Meal History ───
@bp.route('/api/meal/history', methods=['GET'])
def get_history():
    user_id = session.get('user_id')            # ✅ fetched from session
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    meals   = Meal.query.filter_by(user_id=user_id).order_by(Meal.date.desc()).all()
    history = {}
    for m in meals:
        key = str(m.date)
        if key not in history:
            history[key] = {"meals": [], "total_calories": 0, "total_protein": 0}
        history[key]["meals"].append(m.food_name)
        history[key]["total_calories"] += m.calories
        history[key]["total_protein"]  += m.protein

    return jsonify(history), 200