import secrets
from flask import Flask, render_template, g, request, session, redirect

from service.user_service import validate_registration, add_user, authenticate_user, get_current_user

app = Flask(__name__)

app.secret_key = secrets.token_hex()


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def home():
    user = get_current_user()
    return render_template('home.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    errors = validate_registration(request.form)
    if any(len(errors[key]) > 0 for key in errors.keys()):
        return render_template('register.html', has_errors=True, errors=errors, form_values=request.form)
    add_user(request.form)
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == 'GET':
        return render_template('login.html')
    is_authenticated = authenticate_user(request.form)
    if not is_authenticated:
        return render_template('login.html', has_errors=True)
    session['username'] = request.form['username']
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


if __name__ == '__main__':
    app.run()
