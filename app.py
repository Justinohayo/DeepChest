from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Placeholder: Add authentication logic here
        username = request.form.get('username')
        password = request.form.get('password')
        # For now, just redirect to home after login
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Placeholder: Add user registration logic here
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # For now, just redirect to home after signup
        return redirect(url_for('home'))
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
