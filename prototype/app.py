from flask import Flask, request, render_template, jsonify, session
import json
import requests
from flaskext.mysql import MySQL
import flask_login
import re

# Enter into terminal to install framework & libraries:
# python3 -m venv venv
# source venv/bin/activate
# pip install flask
# pip install requests
# pip install flask-mysqldb
# pip install flask-login

app = Flask(__name__)

mysql = MySQL()
app.secret_key = 'your secret key'

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'FurrySpaniel3651761' # ENTER YOUR DATABASE PASSWORD HERE
app.config['MYSQL_DATABASE_DB'] = 'userprofile'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

# conn = mysql.connect()
# cursor = conn.cursor()
# cursor.execute("SELECT email from Users")
# users = cursor.fetchall()

def get_value_related_info(value):
    return (value)

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
        "X-RapidAPI-Key": "0d56b851c9msh6f98a10ad6a3725p123f86jsnaefb33f76036",
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
        "X-RapidAPI-Key": "a4d544596bmshbf04d2448a8ada5p1fec1cjsn12b17682f845",
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
        cursor.execute('SELECT * FROM users WHERE email = % s', (email, ))
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
