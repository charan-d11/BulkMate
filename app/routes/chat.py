from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app import db
from app.models import User, Meal, ChatHistory
from app.common.logger import logger
from datetime import date
from google import genai
from google.genai import types
import os
from app.common.custom_exception import CustomException

bp = Blueprint('chat', __name__)


# ─── Helper: Build system prompt ───
def build_system_prompt(user, today_calories, today_protein):
    goal_map = {
        "gain":     "Help the user gain weight with high calorie, high protein meal advice.",
        "maintain": "Help the user maintain weight with balanced nutrition advice.",
        "lose":     "Help the user lose weight with low calorie, high protein meal advice."
    }
    return f"""
    You are BulkMate AI, a smart and friendly nutrition assistant.

    User Profile:
    - Name: {user.name}
    - Goal: {user.goal} weight
    - Daily Calorie Target: {user.goal_calories} kcal
    - Age: {user.age} | Weight: {user.weight}kg | Height: {user.height}cm

    Today's Progress:
    - Calories consumed: {today_calories} kcal
    - Protein consumed: {today_protein}g
    - Calories remaining: {(user.goal_calories or 2000) - today_calories} kcal

    Your behavior: {goal_map.get(user.goal, '')}
    Keep responses concise, friendly and practical.
    """


# ─── Chat Page ───  ✅ NOW passes user to template
@bp.route('/chat')
def chat_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    # ✅ Fetch user from DB
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    # ✅ Redirect if onboarding not done
    if not user.goal or not user.goal_calories:
        return redirect(url_for('auth.onboarding'))

    # ✅ Fetch chat history
    history = ChatHistory.query.filter_by(user_id=user_id)\
                .order_by(ChatHistory.timestamp.asc()).all()

    logger.info(f"Chat page loaded for user_id={user_id}")

    # ✅ Pass BOTH user and history to template
    return render_template('chat.html', user=user, history=history)


# ─── Chat API ───
@bp.route('/api/chat', methods=['POST'])
def chat():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Message required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Today's totals
    today_meals    = Meal.query.filter_by(user_id=user_id, date=date.today()).all()
    today_calories = sum(m.calories or 0 for m in today_meals)
    today_protein  = sum(m.protein  or 0 for m in today_meals)

    # Past chat history for context
    past_chats = ChatHistory.query.filter_by(user_id=user_id)\
                    .order_by(ChatHistory.timestamp.asc()).all()

    # Build Gemini contents
    contents = []
    for c in past_chats:
        role = "user" if c.role == "user" else "model"
        contents.append(types.Content(
            role=role,
            parts=[types.Part(text=c.message)]
        ))

    contents.append(types.Content(
        role="user",
        parts=[types.Part(text=user_message)]
    ))

    try:
        client   = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=build_system_prompt(user, today_calories, today_protein)
            )
        )
        #logger.info(f"Chat: user_id={user_id} → AI replied successfully")
        ai_reply = response.text.strip()
    except Exception as e:
        logger.error(f"Gemini chat error: {e}")
        return jsonify({"error": f"AI error: {str(e)}"}), 500

    # Save to DB
    db.session.add(ChatHistory(user_id=user_id, role="user",      message=user_message))
    db.session.add(ChatHistory(user_id=user_id, role="assistant", message=ai_reply))
    db.session.commit()
    logger.info(f"Chat: user_id={user_id} → Messages saved to DB")
    logger.info(f"Chat: user_id={user_id} → AI replied successfully")
    return jsonify({"reply": ai_reply}), 200


# ─── Clear Chat ───
@bp.route('/api/chat/clear', methods=['DELETE'])
def clear_chat():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    ChatHistory.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    logger.info(f"Chat history cleared for user_id={user_id}")
    return jsonify({"message": "Chat history cleared!"}), 200