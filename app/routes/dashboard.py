from flask import Blueprint, render_template, session, redirect, url_for
from app.models import User, Meal
from app.common.logger import logger
from datetime import date
from google import genai
import os
#import json
from app import db
from flask import request, jsonify
bp = Blueprint('dashboard', __name__)


def get_ai_tip(user, today_calories, today_protein):
    try:
        client    = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        remaining = (user.goal_calories or 2000) - today_calories

        prompt = f"""
        You are BulkMate AI, a smart nutrition assistant.
        User goal: {user.goal or 'maintain'} weight
        Daily calorie target: {user.goal_calories or 2000} kcal
        Calories consumed today: {today_calories} kcal
        Protein consumed today: {today_protein}g
        Calories remaining: {remaining} kcal
        Give a SHORT, friendly, motivating tip (2-3 sentences max).
        """
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        logger.info(f"AI tip generated for user_id={user.id}: {response.text.strip()}")
        return response.text.strip()
    except Exception as e:
        logger.error(f"AI tip error: {e}")
        return "Stay consistent with your meals and keep tracking!"


@bp.route('/dashboard')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    # ✅ Redirect to onboarding if goal not set yet
    if not user.goal or not user.goal_calories:
        return redirect(url_for('auth.onboarding'))

    # Today's meals
    today_meals = Meal.query.filter_by(
        user_id=user_id,
        date=date.today()
    ).all()

    # ✅ Safe calculation with defaults
    today_calories     = round(sum(m.calories or 0 for m in today_meals), 1)
    today_protein      = round(sum(m.protein  or 0 for m in today_meals), 1)
    today_carbs        = round(sum(m.carbs    or 0 for m in today_meals), 1)
    today_fat          = round(sum(m.fat      or 0 for m in today_meals), 1)
    remaining_calories = round((user.goal_calories or 2000) - today_calories, 1)

    ai_tip = get_ai_tip(user, today_calories, today_protein)

    logger.info(f"Dashboard loaded: user_id={user_id}, calories={today_calories}")

    return render_template('dashboard.html',
        user               = user,
        today_meals        = today_meals,
        today_calories     = today_calories,
        today_protein      = today_protein,
        today_carbs        = today_carbs,
        today_fat          = today_fat,
        remaining_calories = remaining_calories,
        ai_tip             = ai_tip
    )

# ─── Edit Profile ───
@bp.route('/api/profile/edit', methods=['POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        user     = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get form data
        name     = request.json.get('name')
        age      = int(request.json.get('age'))
        weight   = float(request.json.get('weight'))
        height   = float(request.json.get('height'))
        goal     = request.json.get('goal')
        activity = float(request.json.get('activity'))

        # Recalculate goal calories
        from app.routes.auth import calculate_goal_calories
        goal_calories = calculate_goal_calories(weight, height, age, activity, goal)

        # Update user
        user.name          = name
        user.age           = age
        user.weight        = weight
        user.height        = height
        user.goal          = goal
        user.goal_calories = goal_calories
        db.session.commit()

        logger.info(f"Profile updated for user_id={user_id}")
        return jsonify({
            "message":       "Profile updated!",
            "goal_calories": goal_calories
        }), 200

    except Exception as e:
        logger.error(f"Profile edit error: {e}")
        return jsonify({"error": str(e)}), 500