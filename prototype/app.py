from flask import Flask, request, render_template, jsonify, session
import json
import requests
from flaskext.mysql import MySQL
import flask_login

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
app.config['MYSQL_DATABASE_PASSWORD'] = 'your_password' # ENTER YOUR DATABASE PASSWORD HERE
app.config['MYSQL_DATABASE_DB'] = 'userprofile'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()


def get_value_related_info(value):
    return (value)


@app.route('/', methods=['POST', 'GET'])
def getvalue():
    if request.method == "POST":
        HTML_info = request.form['search']
        return get_value_related_info(HTML_info)
    return render_template('form.html', text="")

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

    # return return_string

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

@app.route('/signup', methods=['GET','POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQL.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/login', methods=['POST', 'GET'])
def login():
    # login code goes here
    print("login")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    # sign up code goes here
    print("signup")


if __name__ == '__main__':
    app.run()
