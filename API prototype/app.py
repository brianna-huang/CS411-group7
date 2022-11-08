from flask import Flask
import json
import requests

# Enter following into terminal to install framework & libraries:
# python3 -m venv venv
# source venv/bin/activate
# pip install flask
# pip install requests

app = Flask(__name__)

@app.route('/')
def get_recipe_ingredients():  
    # param: recipe url link. hardcoded it for now
    # return: list of ingredients in the recipe
    url = "https://mycookbook-io1.p.rapidapi.com/recipes/rapidapi"
    payload = "https://www.jamieoliver.com/recipes/vegetables-recipes/superfood-salad/"
    headers = {
        "content-type": "text/plain",
        "X-RapidAPI-Key": "a4e2fc244bmshd6877fd389df594p162eb8jsn5b123867a7d7",
        "X-RapidAPI-Host": "mycookbook-io1.p.rapidapi.com"
    }
    # API subscription is not complete, so the requests won't go through yet
    response = requests.request("POST", url, data=payload, headers=headers)
    parse_response = json.loads(response)
    return(parse_response["ingredients"])
def get_target_products():
    # param: product keyword, hardcoded "apples" for now
    # returns: list of 3 top products from target as a dictionary {product name, url, price}
    url = "https://target-com-store-product-reviews-locations-data.p.rapidapi.com/product/search"
    querystring = {"store_id":"3991","keyword":"apples","offset":"0","limit":"3","sponsored":"1","rating":"0"}
    headers = {
        "X-RapidAPI-Key": "a4e2fc244bmshd6877fd389df594p162eb8jsn5b123867a7d7",
        "X-RapidAPI-Host": "target-com-store-product-reviews-locations-data.p.rapidapi.com"
    }
    response = requests.request('GET', url, headers=headers, params=querystring)
    products_dict = json.loads(response.text)
    return_dict = {}
    for item in products_dict["products"]:
        return_dict[item["item"]["product_description"]["title"]] = (item["item"]["enrichment"]["buy_url"], item["price"]["formatted_current_price"])
    return (return_dict)

if __name__ == '__main__':
    app.run()
