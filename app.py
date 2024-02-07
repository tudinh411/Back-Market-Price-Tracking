from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    product = request.args.get('product')

    url = requests.get(f"https://www.backmarket.com/en-us/search?q={product}")
    soup = BeautifulSoup(url.content, "html.parser")

    page_element = soup.find('span', class_='pagination-count')
    page_text = int(page_element.text.split()[-1]) if page_element else 1

    product_names, prices, rates, links = [], [], [], []

    for page in range(1, page_text + 1):
        url = requests.get(f"https://www.backmarket.com/en-us/search?q={product}&page={page}")
        soup = BeautifulSoup(url.content, "html.parser")
        relative = soup.find_all('div', class_='productCard')

        for i in relative:
            items = i.find_all('h2')
            for item in items:
                product_name = str(items).splitlines()[-2].strip()
                product_names.append(product_name)

                price = i.find(attrs={'data-qa': 'prices'}).text.replace(",", "").replace("$", "").strip()
                prices.append(price)

                rate = i.find(class_="ml-1 text-primary body-2-bold")
                rates.append("None" if rate is None else str(rate.text.strip()))

                link = "backmarket.com" + i.a['href']
                links.append(link)

    data = {'Product name': product_names,
            'Price ($)': prices,
            'Rate': rates,
            'Link': links}

    df = pd.DataFrame(data)
    df['Price ($)'] = df['Price ($)'].astype(float)
    df_sorted = df.sort_values(by=["Price ($)"], ignore_index=True)

    return render_template('results.html', data=df_sorted.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
