from flask import Flask, render_template
import urllib.request, json
import requests

app = Flask(__name__)

@app.route('/')
def get_ingredients():  
    # param: recipe url link
    # return: list of ingredients in the recipe
    url = "https://mycookbook-io1.p.rapidapi.com/recipes/rapidapi"
    payload = "https://www.jamieoliver.com/recipes/vegetables-recipes/superfood-salad/"
    headers = {
        "content-type": "text/plain",
        "X-RapidAPI-Key": "a4e2fc244bmshd6877fd389df594p162eb8jsn5b123867a7d7",
        "X-RapidAPI-Host": "mycookbook-io1.p.rapidapi.com"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    parse_response = json.loads(response)
    return(parse_response["ingredients"])

if __name__ == '__main__':
    app.run()
