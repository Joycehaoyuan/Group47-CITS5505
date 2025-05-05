from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
import csv
import io
import json
from datetime import datetime, timedelta
import os

from app import db
from models import User, Food, MealPlan, UserDietaryData, SharedData, Recipe, RecipeIngredient


bp = Blueprint('routes', __name__)

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/meal-plan')
def meal_plan():
    return render_template('meal_plan.html')

@bp.route('/upload-data')
def upload_data():
    return render_template('upload_data.html')

@bp.route('/visualize-data')
def visualize_data():
    return render_template('visualize_data.html')

@bp.route('/share-data', methods=['GET', 'POST'])
@login_required
def share_data():
    """Page to share data with other users and view shared data."""
    form = ShareDataForm()
    
    if form.validate_on_submit():
        recipient = User.query.filter_by(username=form.recipient_username.data).first()
        
        if not recipient:
            flash('User not found.', 'danger')
            return redirect(url_for('routes.share_data'))
            
        if recipient.id == current_user.id:
            flash('You cannot share data with yourself.', 'warning')
            return redirect(url_for('routes.share_data'))
            
        # Validate that the data exists and belongs to the current user
        data_type = form.data_type.data
        data_id = form.data_id.data
        
        if data_type == 'meal_plan':
            data = MealPlan.query.get(data_id)
        else:  # dietary_data
            data = UserDietaryData.query.get(data_id)
            
        if not data or data.user_id != current_user.id:
            flash('Invalid data selected or you do not own this data.', 'danger')
            return redirect(url_for('routes.share_data'))
            
        # Check if already shared
        existing_share = SharedData.query.filter_by(
            owner_id=current_user.id,
            recipient_id=recipient.id,
            data_type=data_type,
            data_id=data_id
        ).first()
        
        if existing_share:
            flash(f'You have already shared this {data_type.replace("_", " ")} with {recipient.username}.', 'info')
            return redirect(url_for('routes.share_data'))
            
        # Create new share
        share = SharedData(
            owner_id=current_user.id,
            recipient_id=recipient.id,
            data_type=data_type,
            data_id=data_id
        )
        
        db.session.add(share)
        db.session.commit()
        
        flash(f'Successfully shared your {data_type.replace("_", " ")} with {recipient.username}!', 'success')
        return redirect(url_for('routes.share_data'))
    
    # Get user's data for sharing options
    meal_plans = MealPlan.query.filter_by(user_id=current_user.id).order_by(MealPlan.date_created.desc()).all()
    dietary_data = UserDietaryData.query.filter_by(user_id=current_user.id).order_by(UserDietaryData.date.desc()).all()
    
    # Get existing shares
    my_shares = SharedData.query.filter_by(owner_id=current_user.id).all()
    
    # Get data shared with the current user
    shared_data = SharedData.query.filter_by(recipient_id=current_user.id).all()
    
    # Fetch actual data objects for data shared with me
    shared_items = []
    for share in shared_data:
        if share.data_type == 'meal_plan':
            data_obj = MealPlan.query.get(share.data_id)
            if data_obj:
                shared_items.append({
                    'share': share,
                    'data': data_obj,
                    'owner': User.query.get(share.owner_id),
                    'meals': data_obj.get_meals()
                })
        else:  # dietary_data
            data_obj = UserDietaryData.query.get(share.data_id)
            if data_obj:
                shared_items.append({
                    'share': share,
                    'data': data_obj,
                    'owner': User.query.get(share.owner_id)
                })
    
    # Get all registered users for autocomplete (excluding current user)
    all_users = User.query.filter(User.id != current_user.id).all()
    
    return render_template(
        'share_data.html',
        form=form,
        meal_plans=meal_plans,
        dietary_data=dietary_data,
        my_shares=my_shares,
        shared_items=shared_items,
        all_users=all_users
    )

@bp.route('/shared-with-me')
@login_required
def shared_with_me():
    """Redirect to consolidated share page."""
    return redirect(url_for('routes.share_data'))

@bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    meal_plan_count = MealPlan.query.filter_by(user_id=current_user.id).count()
    data_entry_count = UserDietaryData.query.filter_by(user_id=current_user.id).count()
    
    return render_template(
        'profile.html',
        meal_plan_count=meal_plan_count,
        data_entry_count=data_entry_count
    )

@bp.route('/delete-share/<int:share_id>', methods=['POST'])
@login_required
def delete_share(share_id):
    """Delete a data share."""
    share = SharedData.query.get_or_404(share_id)
    
    # Only the owner can delete a share
    if share.owner_id != current_user.id:
        abort(403)
        
    db.session.delete(share)
    db.session.commit()
    
    flash('Share has been removed.', 'success')
    return redirect(url_for('routes.share_data'))



@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/register')
def register():
    return render_template('register.html')
