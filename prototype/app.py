from flask import Flask, request, render_template, jsonify,url_for,redirect,session
from authlib.integrations.flask_client import OAuth
import json
import requests
from flaskext.mysql import MySQL


import flask_login

# Enter into terminal to install framework & libraries:
# python3 -m venv venv
# mac -> source venv/bin/activate , windows ->.\venv\Scripts\activate
# pip install flask
# pip install requests
# pip install Authlib requests
# mac -> pip install flask-mysqldb , windows -> pip install flask-mysql
# pip install flask-login
# pip install flask flask_sqlalchemy flask_login flask_bcrypt flask_wtf wtforms email_validator

app = Flask(__name__)

mysql = MySQL()
app.secret_key = 'your secret key'
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
)

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password1' # ENTER YOUR DATABASE PASSWORD HERE
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
    return render_template('form.html', text="")

# Authentication
@app.route('/login')
def login():
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



if __name__ == '__main__':
    app.debug = True
    app.run()
