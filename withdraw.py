# withdraw.py

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
import mysql.connector

def create_withdraw_blueprint(db_config, add_points):
    withdraw_bp = Blueprint('withdraw', __name__)

    @withdraw_bp.route('/withdraw', methods=['GET', 'POST'])
    def withdraw():
        if request.method == 'POST':
            receiving_account = request.form.get('receiving_account')
            token = request.form.get('token')
            amount = request.form.get('amount')
            user_id = session.get('user_id')
            
            if not user_id:
                flash('You need to login first.', 'danger')
                return redirect(url_for('login'))

            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()

                # Check if user has enough points
                cursor.execute("SELECT points FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                if user and user[0] >= int(amount):
                    # Deduct points
                    
                    cursor.execute("UPDATE users SET points = points - %s WHERE id = %s", (amount, user_id))
                    conn.commit()

                    # Insert into payments table
                    cursor.execute("""
                        INSERT INTO payments (user_id, receiving_account, token, amount)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, receiving_account, token, amount))
                    conn.commit()

                    flash('Withdrawal successful!', 'success')
                    return jsonify({"success": True})
                else:
                    flash('Not enough points for withdrawal.', 'danger')
                    return jsonify({"error": "Not enough points for withdrawal"}), 400

                cursor.close()
                conn.close()
            except mysql.connector.Error as err:
                flash(f"Error: {err}", 'danger')
                return jsonify({"error": str(err)}), 500

        return render_template('withdraw.html')

    return withdraw_bp
