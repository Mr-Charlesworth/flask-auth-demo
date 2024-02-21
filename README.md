# Authentication Demo

This repository is a demonstration of a basic app with user registration and authentication with a username and
password.

Basic registration and logging in has been implemented for you, your job is to read the code, understand it and ask
questions about anything you do not understand.

## Forking / Environment stuff

- If you are in GitHub click 'Fork' to copy the repository to your own GitHub
- 'Forking' creates a copy of the repository in your own GitHub repositories space, so you are free to make your own
  changes and push them.
- Once you can see your new copy of the repository in GitHub, click 'Code > SSH > Copy the URL to clipboard'
- Use git-bash to clone your copy of the repository

```bash
git clone [the-url-you-copied]
```

- Now open the cloned directory in PyCharm
- To ensure we are working in an environment that is not using global python packages, and we can install what we want,
  we need to use a virtual environment
- Click
  the [python interpreter selector](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#widget) (
  bottom right corner in PyCharm)
- Choose "Add New Interpreter" > "Add Local Interpreter"
- In the left-hand pane of the Add Python Interpreter dialog, select Virtualenv Environment.
- The default location should be a folder called "venv" inside your project folder
- Now when we install packages, we install them in an isolated environment, which is good.
- Use the terminal in PyCharm as this will use the environment we just created.
- If you already have a terminal open, open a new one to be sure it is using the environment.
- Install flask

```bash
pip install flask
```

## Setting up the Database

- You need the database to be named "messages.db" and placed in the project root.
- The Sqlite database file is not included in this repository, but you can create your own using the SQL
  in [initdb.sql](./initdb.sql)
- You can use the commandline tool to import the database using the sql file:

```bash
sqlite3 message.db < initdb.sql
```

- Note that you will need to enter the path your sqlite3.exe if you do not already have it on your PATH:

```bash
[path-to-sqlite.exe] message.db < initdb.sql
```

## Registration form

- There are some new concepts used in this form, the most significant is the use
  of [macros](https://jinja.palletsprojects.com/en/3.1.x/templates/#macros).
- Macros are part of the templating engine included with Flask which is
  called [Jinja](https://palletsprojects.com/p/jinja/)
- We can use them like functions (and they are defined very much in the same way) where we have lots of repeated HTML in
  which we can pass some parameters
- Here is the definition of the input field macro used in [register.html](./templates/register.html)

```html
{% macro input(name, label, type='text') -%}
    <div class="form-group">
        <label for="{{ name }}">{{ label }}</label>
        <input
                type="{{ type }}"
                class="form-control{{ ' is-invalid' if has_errors and errors[name]|length > 0 }}"
                name="{{ name }}"
                id="{{ name }}"
                placeholder="{{ label }}"
                {% if has_errors %}
                value="{{ form_values[name] }}"
                {% endif %}
        >
        {% if has_errors and errors[name]|length > 0 %}
            {% for error in errors[name] %}
                <div class="invalid-feedback">
                    {{ error }}
                </div>
            {% endfor %}
        {% endif %}
    </div>
{% endmacro %}
```

- "name", "label" and "type" are the parameters which are defined at the top where "type" has a default of "text"
- Here, I'm using the macro to represent a form field that may need to display feedback errors where some validation
  from the flask server has failed (e.g. password is too short, etc.)
- It is also being used to pre-populate the fields if there are any errors to prevent users needing to retype the full
  input.
- To use a macro, its very much like calling a function, we just need to call it where we want the HTML to be output:

```html
<form method="POST" action="/register">
    {{ input('first_name', 'First Name') }}
    {{ input('surname', 'Surname') }}
    {{ input('username', 'Username') }}
    {{ input('password', 'Password', 'password') }}
    <div class="form-group">
        <label for="confirm_password">Password</label>
        <input type="password" class="form-control" name="confirm_password" id="confirm_password"
               placeholder="Re-enter Password">
    </div>
    <button type="submit" class="btn btn-primary mt-1">Submit</button>
</form>
```

- The template is aware of errors via parameters "has_errors" which is a bool and the "errors" dictionary object.
- The "errors" dictionary object has a list of error messages under each field which is empty if there are no messages
- For example "errors['password']" contains all error messages for the password field or is am empty list if there are none.

## Validation

- Validation is handled in [service/user_service.py](./service/user_service.py)
- Maintaining a service layer allows us to separate our concerns so that all our code is not in [app.py](./app.py)
- Validating a registration means creating an "errors" dictionary object as described above
- If all the lists in the object are empty, then there are no errors and we can add the user to the database and redirect to the home ('/') route where the user can login (we're not automatically logging in here though this is something we could do).
- If there are errors, the user is returned to the registration page with "has_errors" set to "True", the errors dictionary object is passed to the template along with the entered form values (for repopulating the fields)

## Storing The Password

- We don't store plain-text passwords in databases, we use hashes. Read both:
  - [Here is a description of the basic principles](https://delinea.com/blog/how-do-passwords-work)
  - [Here is a description of the implementation of hashing using bcrypt in python](https://www.tutorialspoint.com/hashing-passwords-in-python-with-bcrypt)

## Logging in

- Right at the top of [app.py](./app.py) where we instantiate the flask app, we configure the app with a secret:

```python
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex()
```

- secrets.token_hex() generates a random 32bit hexadecimal string
- This string is used to cryptographically sign cookies that are used to store key value pairs, e.g. what is the username of the logged-in user.
- Signing means that the Flask server will know if they have been tampered with and will throw out requests where this is the case.
- A '/login' route handles showing the login page and taking login credentials from the form.
- Authentication is handled in the [user service](./service/user_service.py)

```python
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
```

- If the entered credentials both:
  - Match a user of the entered username
  - Matches the password of the matched user in the database (i.e. it produces the same hash stored in the database)
- Then we add the username of the logged-in user to the session object, which is imported from Flask

```python
session['username'] = request.form['username']
```

## Checking if a user is logged in

- For any request, we have access to the session object which is imported from flask
- We can use it to check for presence of a username key-value pair and use it to get the user from the database
- This is done in the [user service](./service/user_service.py)

```python
def get_current_user():
    user_result = None
    if 'username' in session:
        username = session['username']
        db = get_db()
        user_cur = db.execute('SELECT id, first_name, surname, username FROM user WHERE username = ?', [username])
        user_result = user_cur.fetchone()
    return user_result
```

- If the returned item is 'None' then the user is not logged in.
- Otherwise, the returned item is a dictionary containing the user's information
- This can be used wherever we need to check for a logged-in user and is used on the home route ('/'):

```python
@app.route('/')
def home():
    user = get_current_user()
    return render_template('home.html', user=user)
```

- Have a look at the navbar in [base.html](./templates/base.html) to see how the user is used to show the logged in state and to show/hide specific navbar items

## Big Brain Task

The main 'big brain' task is to understand this code, but here are something other things to do:

- Have a look at [initdb.sql](./initdb.sql) which was used to create the database.
- You will see that there is a table for messages.
- Each message is from a user to a user.

### Tasks

- Implement a 'Send Message' page for logged-in users to
  - Select from a list of users using their first name and surname to send a message to
  - Type a message and submit it to the selected user.
- Implement a 'View Messages' page for a loggin-in user to see any messages sent to them.