from flask import Flask, request, render_template, jsonify,url_for,redirect,session

import json
import requests
from flaskext.mysql import MySQL
import flask_login
import re
from authlib.integrations.flask_client import OAuth

# Enter into terminal to install framework & libraries:
# python3 -m venv venv
# source venv/bin/activate
# pip install flask
# pip install Authlib requests
# pip install requests
# pip install flask-mysqldb
# pip install flask-login

app = Flask(__name__)

mysql = MySQL()
app.secret_key = 'your secret key'

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'your password' # ENTER YOUR DATABASE PASSWORD HERE
app.config['MYSQL_DATABASE_DB'] = 'userprofile'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

# conn = mysql.connect()
# cursor = conn.cursor()
# cursor.execute("SELECT email from Users")
# users = cursor.fetchall()

#oauth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=("872397603918-5m0upqbbck7eesob44d9atv81247dku4.apps.googleusercontent.com"),
    client_secret=("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"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs",
)

def get_value_related_info(value):
    return (value)

# Authentication
@app.route('/googlelogin')
def google_login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def getvalue():
    if request.method == "POST":
        HTML_info = request.form['search']
        return get_value_related_info(HTML_info)
    return render_template('index.html', text="")

@app.route('/search', methods=['POST'])
def get_recipe_ingredients():
    # param: still need to implement recipe url link passed from front-end. hardcoded it for now
    # return: list of ingredients in the recipe
    url = "https://mycookbook-io1.p.rapidapi.com/recipes/rapidapi"
    payload = getvalue().encode()
    headers = {
        "content-type": "text/plain",
        "X-RapidAPI-Key": "",
        "X-RapidAPI-Host": "mycookbook-io1.p.rapidapi.com"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    # print(response.text)
    recipe_dict = json.loads(response.text)
    # return recipe_dict[0]["ingredients"]
    return_string = ""
    for ingredient in recipe_dict[0]["ingredients"]:
        return_string = return_string + ingredient + "\n"
    return(call_target_api(parse_ingredients(return_string)))
    #return (parse_ingredients(return_string))


def parse_ingredients(recipe_ingredients):  
    # param: still need to implement recipe url link passed from front-end. hardcoded it for now
    # return: list of ingredients in the recipe
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/parseIngredients"

    payload = "ingredientList=" + recipe_ingredients + "&servings=2"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "a4e2fc244bmshd6877fd389df594p162eb8jsn5b123867a7d7",
        "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    ingredient_dict = json.loads(response.text)
    ingredients = []
    for ingredient in ingredient_dict:
        ingredients.append(ingredient["name"])
    return ingredients

def call_target_api(ingredients):
    return_string = ""
    for ingredient in ingredients:
        return_string = return_string + ingredient + "<br/>" + get_target_products(ingredient) + "<br/>"
    return return_string

def get_target_products(ingredient):
    # param: still need to implement product keyword passed from front-end
    # returns: dictionary of 2 top products from target {product name: url, price}
    url = "https://target-com-store-product-reviews-locations-data.p.rapidapi.com/product/search"
    querystring = {"store_id":"3991","keyword":ingredient,"offset":"0","limit":"2","sponsored":"1","rating":"0"}
    headers = {
        "X-RapidAPI-Key": "0d56b851c9msh6f98a10ad6a3725p123f86jsnaefb33f76036",
        "X-RapidAPI-Host": "target-com-store-product-reviews-locations-data.p.rapidapi.com"
    }
    response = requests.request('GET', url, headers=headers, params=querystring)
    products_dict = json.loads(response.text)
    return_dict = {}
    for item in products_dict["products"]:
        return_dict[item["item"]["product_description"]["title"]] = (item["item"]["enrichment"]["buy_url"], item["price"]["formatted_current_price"])
    return_string = ""
    for item in return_dict:
        return_string = return_string + item + ":<br/>" + "price:" + return_dict[item][1] + "<br/>" + "url: " + return_dict[item][0] + "<br/>"
    return return_string



@app.route('/signup', methods =['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'password' in request.form and 'email' in request.form :
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        email = request.form['email']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not first_name or not last_name or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO users (email, password, first_name, last_name) VALUES (%s, %s, %s, %s)', (email, password, first_name, last_name, ))
            conn.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('signup.html', msg = msg)


@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['email'] = email
            msg = 'Logged in successfully!'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username or password!'
    return render_template('login.html', msg = msg)


if __name__ == '__main__':
    app.run()
