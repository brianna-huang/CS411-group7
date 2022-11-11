from flask import Flask, request, render_template, jsonify
import json
import requests

# Enter into terminal to install framework & libraries:
# python3 -m venv venv
# source venv/bin/activate
# pip install flask
# pip install requests

app = Flask(__name__)


def get_value_related_info(value):
    return {value}


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
    payload = "https://www.jamieoliver.com/recipes/vegetables-recipes/superfood-salad/"
    headers = {
        "content-type": "text/plain",
        "X-RapidAPI-Key": "0d56b851c9msh6f98a10ad6a3725p123f86jsnaefb33f76036",
        "X-RapidAPI-Host": "mycookbook-io1.p.rapidapi.com"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    # print(response.text)
    recipe_dict = json.loads(response.text)
    return recipe_dict[0]["ingredients"]


# # FOR LATER USAGE
# def get_target_products():
#     # param: still need to implement product keyword passed from front-end, hardcoded "apples" for now
#     # returns: dictionary of 3 top products from target {product name: url, price}
#     url = "https://target-com-store-product-reviews-locations-data.p.rapidapi.com/product/search"
#     querystring = {"store_id":"3991","keyword":"apples","offset":"0","limit":"3","sponsored":"1","rating":"0"}
#     headers = {
#         "X-RapidAPI-Key": "a4e2fc244bmshd6877fd389df594p162eb8jsn5b123867a7d7",
#         "X-RapidAPI-Host": "target-com-store-product-reviews-locations-data.p.rapidapi.com"
#     }
#     response = requests.request('GET', url, headers=headers, params=querystring)
#     products_dict = json.loads(response.text)
#     return_dict = {}
#     for item in products_dict["products"]:
#         return_dict[item["item"]["product_description"]["title"]] = (item["item"]["enrichment"]["buy_url"], item["price"]["formatted_current_price"])
#     return (return_dict)


if __name__ == '__main__':
    app.run()
