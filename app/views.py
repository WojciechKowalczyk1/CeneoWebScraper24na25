import os
import json
import requests
from datetime import datetime
from app import app
from flask import render_template, redirect, url_for, request, send_from_directory
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from config import headers

def list_to_html(l):
    return "<ul>"+"".join([f"<li>{e}</li>" for e in l])+"</ul>" if l else ""

def extract(ancestor, selector=None, attribute=None, multiple=False):
    if selector:
        if multiple:
            if attribute:
                return [tag[attribute].strip() for tag in ancestor.select(selector)]
            return [tag.text.strip() for tag in ancestor.select(selector)]
        if attribute:
            try:
                return ancestor.select_one(selector)[attribute].strip()
            except TypeError:
                return None
        try:
            return ancestor.select_one(selector).text.strip()
        except AttributeError:
            return None
    if attribute:
        return ancestor[attribute].strip()
    return None

selectors = {
    "opinion_id": (None, "data-entry-id"),
    "author": ("span.user-post__author-name",),
    "recommendation": ("span.user-post__author-recomendation > em",),
    "stars": ("span.user-post__score-count",),
    "content": ("div.user-post__text",),
    "pros": ("div.review-feature__item--positive", None, True),
    "cons": ("div.review-feature__item--negative", None, True),
    "useful": ("button.vote-yes", "data-total-vote"),
    "useless": ("button.vote-no","data-total-vote"),
    "post_date": ("span.user-post__published > time:nth-child(1)","datetime"),
    "purchase_date": ("span.user-post__published > time:nth-child(2)","datetime")
}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/extract', methods=['post'])
def extract_data():
    product_id = request.form.get('product_id')
    url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
    print(url)
    response = requests.get(url, headers=headers)
    if response.status_code==200:
        page_dom = BeautifulSoup(response.text, "html.parser")
        product_name = extract(page_dom, "h1")
        opinions_count = extract(page_dom, "a.product-review__link > span")
        if not opinions_count:
            error = "Dla produktu o podanym kodzie nie ma opinii"
            return render_template("extract.html", error=error)
    else:
        error = "Podana wartość nie jest poprawnym kodem produktu"
        return render_template("extract.html", error=error)  
    all_opinions = []
    while url:
        print(url)
        response = requests.get(url, headers=headers)
        if response.status_code==200:
            page_dom = BeautifulSoup(response.text, "html.parser")
            opinions = page_dom.select("div.js_product-review:not(.user-post--highlight)")
            print(len(opinions))
            for opinion in opinions:
                single_opinion = {
                    key: extract(opinion, *value) for key, value in selectors.items()
                }
                all_opinions.append(single_opinion)
            try:
                url = "https://www.ceneo.pl"+extract(page_dom, "a.pagination__next", "href")
            except TypeError:
                url = None         
         
    if not os.path.exists("./app/data"):
        os.mkdir("./app/data")
    if not os.path.exists("./app/data/opinions"):
        os.mkdir("./app/data/opinions") 
    with open(f"./app/data/opinions/{product_id}.json", "w", encoding="UTF-8") as jf:
        json.dump(all_opinions, jf, indent=4, ensure_ascii=False)
    opinions = pd.DataFrame.from_dict(all_opinions)
    opinions.stars = opinions.stars.apply(lambda s: s.split("/")[0].replace(",",".")).astype(float)
    pros_count = int(opinions.pros.astype(bool).sum())
    cons_count = int(opinions.cons.astype(bool).sum())
    average_stars = float(opinions.stars.mean())
    stars_distr = opinions.stars.value_counts().reindex(list(np.arange(0, 5.5, 0.5)), fill_value=0)
    recommendation_distr = opinions.recommendation.value_counts(dropna=False).reindex(["Nie polecam", "Polecam", None], fill_value=0)
    product_info = {
        "product_id": product_id,
        "product_name": product_name,
        "opinions_count": opinions_count,
        "pros_count": pros_count,
        "cons_count": cons_count,
        "average_stars": average_stars,
        "stars_distr": stars_distr.to_dict(),
        "recommendation_distr": recommendation_distr.to_dict()
    }
    if not os.path.exists("./app/data/products"):
        os.mkdir("./app/data/products") 
    with open(f"./app/data/products/{product_id}.json", "w", encoding="UTF-8") as jf:
        json.dump(product_info, jf, indent=4, ensure_ascii=False)
    return redirect(url_for('product', product_id=product_id))

@app.route('/extract', methods=['get'])
def display_form():
    return render_template("extract.html")

@app.route('/products')
def products():
    products = []
    for file in os.listdir("./app/data/products"):
        if file.endswith(".json"):
            with open(os.path.join("./app/data/products", file), "r", encoding="utf-8") as f:
                data = json.load(f)
                products.append(data)
    return render_template("products.html", products=products)

@app.route('/author')
def author():
    return render_template("author.html")

def parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None
    return None

@app.route('/product/<product_id>', methods=['GET', 'POST'])
def product(product_id):
    product_path = os.path.join("./app/data/products", f"{product_id}.json")
    if not os.path.exists(product_path):
        return f"Produkt o ID {product_id} nie istnieje.", 404
    with open(product_path, "r", encoding="utf-8") as f:
        product_data = json.load(f)
    
    opinions_path = os.path.join("./app/data/opinions", f"{product_id}.json")
    if os.path.exists(opinions_path):
        with open(opinions_path, "r", encoding="utf-8") as f:
            opinions_data = json.load(f)
    else:
        opinions_data = []

    sort_by = request.args.get('sort_by', 'opinion_id')
    reverse = request.args.get('reverse', 'false') == 'true'

    if sort_by == 'purchase_date':
        opinions_data = sorted(
            opinions_data,
            key=lambda x: parse_date(x.get('purchase_date')) if parse_date(x.get('purchase_date')) else datetime.min,
            reverse=reverse
        )
    elif sort_by == 'pros':
        opinions_data = sorted(
            opinions_data,
            key=lambda x: len(x.get('pros', [])),
            reverse=reverse
        )
    elif sort_by == 'cons':
        opinions_data = sorted(
            opinions_data,
            key=lambda x: len(x.get('cons', [])),
            reverse=reverse
        )
    else:
        opinions_data = sorted(opinions_data, key=lambda x: x.get(sort_by), reverse=reverse)

    filter_by = request.args.get('filter_by', '').strip().lower()
    if filter_by:
        opinions_data = [
            op for op in opinions_data if any(
                filter_by in str(op.get(key, '')).lower() for key in ['opinion_id', 'content', 'author', 'recommendation', 'stars', 'pros', 'cons']
            )
        ]

    return render_template("product.html", product=product_data, opinions=opinions_data)

@app.route('/download_json/<product_id>')
def download_json(product_id):
    opinions_directory = os.path.abspath("./app/data/opinions")
    opinion_file_name = f"{product_id}.json"
    opinion_file_path = os.path.join(opinions_directory, opinion_file_name)
    if not os.path.exists(opinion_file_path):
        return f"Plik z opiniami dla produktu {product_id} nie istnieje.", 404
    return send_from_directory(directory=opinions_directory, path=opinion_file_name, as_attachment=True)

@app.route('/charts/<product_id>')
def charts(product_id):
    product_path = os.path.join("./app/data/products", f"{product_id}.json")
    if not os.path.exists(product_path):
        return f"Produkt o ID {product_id} nie istnieje.", 404
    with open(product_path, "r", encoding="utf-8") as f:
        product_data = json.load(f)
    return render_template("charts.html", product=product_data)