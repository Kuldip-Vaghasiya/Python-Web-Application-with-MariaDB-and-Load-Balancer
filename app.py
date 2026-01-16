from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# -------------------------------
# MariaDB Connection
# -------------------------------
db = mysql.connector.connect(
    host="localhost",
    user="flaskuser",
    password="",
    database="flask_app"
)

cursor = db.cursor(dictionary=True)

# -------------------------------
# Home Page (Form Page)
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        country = request.form['country']

        query = "INSERT INTO users (name, email, country) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, email, country))
        db.commit()

        # ✅ Redirect to THANK YOU page
        return redirect(url_for('thank_you'))

    return render_template('index.html')

# -------------------------------
# Thank You Page
# -------------------------------
@app.route('/thank-you')
def thank_you():
    return render_template('thankyou.html')

# -------------------------------
# Optional: View Data Page
# -------------------------------
@app.route('/view')
def view_data():
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    return render_template('view.html', users=data)

# -------------------------------
# Run App
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
