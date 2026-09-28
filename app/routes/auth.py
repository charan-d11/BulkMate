from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app import db, bcrypt
from app.models import User
import os
from app.common.logger import logger
from app.common.custom_exception import CustomException
import random
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

bp = Blueprint('auth', __name__)

# ─── Helper: Calculate goal calories ───
def calculate_goal_calories(weight, height, age, activity_level, goal):
    bmr  = 10 * weight + 6.25 * height - 5 * age + 5
    tdee = bmr * activity_level

    if goal == "gain":
        return int(tdee + 450)
    elif goal == "lose":
        return int(tdee - 450)
    else:
        return int(tdee)

# ─── Helper: Send OTP via SendGrid ───
def send_otp_email(to_email, otp_code, user_name):
    try:
        message = Mail(
            from_email = os.environ.get("SENDER_EMAIL"),
            to_emails  = to_email,
            subject    = "BulkMate — Your OTP Code",
            html_content = f"""
                <div style="font-family:Arial,sans-serif;max-width:400px;margin:auto;background:#0a0a0a;padding:30px;border-radius:12px;border:1px solid #222;">
                    <h2 style="color:#4ade80;margin-bottom:8px;">BulkMate 💪</h2>
                    <p style="color:#aaa;">Hey {user_name}! Here is your OTP to reset your password:</p>
                    <div style="background:#111;border:1px solid #333;border-radius:8px;padding:20px;text-align:center;margin:20px 0;">
                        <h1 style="color:#4ade80;letter-spacing:10px;margin:0;">{otp_code}</h1>
                    </div>
                    <p style="color:#666;font-size:12px;">This OTP is valid for <strong style="color:#aaa;">10 minutes</strong> only.</p>
                    <p style="color:#666;font-size:12px;">If you did not request this, ignore this email.</p>
                </div>
            """
        )
        sg  = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        sg.send(message)
        logger.info(f"OTP email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"SendGrid error: {e}")
        return False

# ─── Register ───
@bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            name     = request.form.get('name')       # ✅ fetched here
            email    = request.form.get('email')      # ✅ fetched here
            password = request.form.get('password')   # ✅ fetched here
            logger.info(f"Attempting to register user: {name} with email: {email}")
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                logger.warning(f"Register attempt with existing email: {email}")
                flash('Email already registered!', 'danger')
                return redirect(url_for('auth.register'))
            
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

            new_user = User(name=name, email=email, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            logger.info(f"New user registered: {name} (id={new_user.id})")
            flash('Account created! Complete your profile.', 'success')
            logger.info(f"Redirecting user {name} to onboarding page.")
            return redirect(url_for('auth.onboarding'))
    

        return render_template('register.html')
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise CustomException("An error occurred during registration.", e)
    # if request.method == 'POST':
    #     name     = request.form.get('name')       # ✅ fetched here
    #     email    = request.form.get('email')      # ✅ fetched here
    #     password = request.form.get('password')   # ✅ fetched here

    #     existing_user = User.query.filter_by(email=email).first()
    #     if existing_user:
    #         logger.warning(f"Register attempt with existing email: {email}")
    #         flash('Email already registered!', 'danger')
    #         return redirect(url_for('auth.register'))

    #     hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    #     new_user = User(name=name, email=email, password=hashed_pw)
    #     db.session.add(new_user)
    #     db.session.commit()

    #     session['user_id'] = new_user.id
    #     logger.info(f"New user registered: {name} (id={new_user.id})")
    #     flash('Account created! Complete your profile.', 'success')
    #     return redirect(url_for('auth.onboarding'))

    # return render_template('register.html')


# ─── Onboarding ───
@bp.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    try:
        user_id = session.get('user_id')    # ✅ fetched here
        if not user_id:
            logger.warning("Onboarding accessed without user_id in session.")
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            age      = int(request.form.get('age'))
            weight   = float(request.form.get('weight'))
            height   = float(request.form.get('height'))
            goal     = request.form.get('goal')
            activity = float(request.form.get('activity'))

            goal_calories = calculate_goal_calories(weight, height, age, activity, goal)

            user = User.query.get(user_id)
            user.age           = age
            user.weight        = weight
            user.height        = height
            user.goal          = goal
            user.activity_level = activity
            user.goal_calories = goal_calories
            db.session.commit()

            logger.info(f"Onboarding complete for user_id={user_id}, goal={goal}, target={goal_calories}kcal")
            flash(f'Profile set! Your daily target is {goal_calories} kcal.', 'success')
            logger.info(f"Redirecting user_id={user_id} to dashboard.")
            return redirect(url_for('dashboard.index'))
        logger.info(f"Rendering onboarding page for user_id={user_id}.")
        return render_template('onboarding.html')

    except Exception as e:
        logger.error(f"Error during onboarding: {e}")
        raise CustomException("An error occurred during onboarding.", e)


# ─── Login ───
@bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email    = request.form.get('email')      # ✅ fetched here
            password = request.form.get('password')   # ✅ fetched here

            user = User.query.filter_by(email=email).first()

            if not user or not bcrypt.check_password_hash(user.password, password):
                logger.warning(f"Failed login for email: {email}")
                flash('Invalid email or password!', 'danger')
                return redirect(url_for('auth.login'))

            session['user_id'] = user.id
            logger.info(f"User logged in: {user.name} (id={user.id})")
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard.index'))

        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise CustomException("An error occurred during login.", e)

# ─── Logout ───
@bp.route('/logout')
def logout():
    try:
        user_id = session.get('user_id')
        logger.info(f"User logged out: user_id={user_id}")
        session.clear()
        flash('Logged out successfully!', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise CustomException("An error occurred during logout.", e)

# ─── Forgot Password ───
@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user  = User.query.filter_by(email=email).first()

        if not user:
            flash('No account found with this email!', 'danger')
            return redirect(url_for('auth.forgot_password'))

        # Generate 6 digit OTP
        otp_code   = str(random.randint(100000, 999999))
        otp_expiry = datetime.now() + timedelta(minutes=10)

        # Save OTP to DB
        user.otp_code     = otp_code
        user.otp_expiry   = otp_expiry
        user.otp_verified = False
        db.session.commit()

        # Send email
        sent = send_otp_email(email, otp_code, user.name)
        if not sent:
            flash('Failed to send OTP. Try again!', 'danger')
            return redirect(url_for('auth.forgot_password'))

        # Store email in session for next steps
        session['reset_email'] = email
        logger.info(f"OTP generated for {email}")
        flash('OTP sent to your email!', 'success')
        return redirect(url_for('auth.verify_otp'))

    return render_template('forgot_password.html')


# ─── Verify OTP ───
@bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        user        = User.query.filter_by(email=email).first()

        if not user:
            flash('Session expired. Try again!', 'danger')
            return redirect(url_for('auth.forgot_password'))

        # Check OTP expiry
        if datetime.now() > user.otp_expiry:
            flash('OTP expired! Request a new one.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        # Check OTP match
        if entered_otp != user.otp_code:
            flash('Wrong OTP! Please try again.', 'danger')
            return redirect(url_for('auth.verify_otp'))

        # OTP verified!
        user.otp_verified = True
        db.session.commit()
        logger.info(f"OTP verified for {email}")
        return redirect(url_for('auth.reset_password'))

    return render_template('verify_otp.html')


# ─── Reset Password ───
@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()

    # Block if OTP not verified
    if not user or not user.otp_verified:
        flash('Please verify OTP first!', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password     = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.reset_password'))

        # Update password
        user.password     = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.otp_code     = None
        user.otp_expiry   = None
        user.otp_verified = False
        db.session.commit()

        # Clear session
        session.pop('reset_email', None)
        logger.info(f"Password reset successful for {email}")
        flash('Password reset successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')