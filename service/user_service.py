from flask import session
import bcrypt

from db import get_db


def validate_field_not_empty(field, field_name):
    if len(field) == 0:
        return [f'{field_name} cannot be empty']
    return []


def validate_username(username):
    empty_username = validate_field_not_empty(username, 'Username')
    if len(empty_username) > 0:
        return empty_username
    if len(username) < 3 :
        return ['Username must be at least 3 characters long']
    db = get_db()
    cur = db.execute("SELECT * FROM user WHERE username=?", [username])
    results = cur.fetchall()
    if len(results) > 0:
        print(cur.rowcount)
        return ['User with this username already exists']
    return []


def validate_passwords(password, confirm_password):
    errors = []
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long.')
    if not any(char.isupper() for char in password) or \
            not any(char.isdigit() for char in password) or \
            not any(char.islower() for char in password):
        errors.append('Password must contain at least one uppercase character, one lowercase character and one digit.')
    if password != confirm_password:
        errors.append('Passwords must match')
    return errors


def validate_registration(user_form_falues):
    first_name = user_form_falues['first_name']
    surname = user_form_falues['surname']
    username = user_form_falues['username']
    password = user_form_falues['password']
    confirm_password = user_form_falues['confirm_password']
    errors = {
        'first_name': validate_field_not_empty(first_name, "First name"),
        'surname': validate_field_not_empty(surname, 'Surname'),
        'username': validate_username(username),
        'password': validate_passwords(password, confirm_password)
    }
    return errors


def add_user(user_form_falues):
    first_name = user_form_falues['first_name']
    surname = user_form_falues['surname']
    username = user_form_falues['username']
    password = user_form_falues['password']
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(str.encode(password), salt)
    db = get_db()
    db.execute('INSERT INTO user (first_name, surname, username, password) VALUES (?, ?, ?, ?)',
               (first_name, surname, username, hashed))
    db.commit()


def authenticate_user(uservalues):
    username = uservalues['username']
    password = uservalues['password']
    db = get_db()
    cur = db.execute('SELECT * FROM user WHERE username = ?', [username])
    result = cur.fetchone()
    if not result:
        return False
    password_correct = bcrypt.checkpw(str.encode(password), result['password'])
    return password_correct


def get_current_user():
    user_result = None
    if 'username' in session:
        username = session['username']
        db = get_db()
        user_cur = db.execute('SELECT id, first_name, surname, username FROM user WHERE username = ?', [username])
        user_result = user_cur.fetchone()
    return user_result
