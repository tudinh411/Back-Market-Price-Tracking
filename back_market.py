from bs4 import BeautifulSoup
import streamlit as st
import requests
import pandas as pd

#Customize the page with streamlit
st.set_page_config(page_title="Price Tracking", layout = "wide",page_icon=":bee:")
st.header("Price Tracking, Smart Shopping")
st.subheader("Save more with Back Market, a leading market place for refurbished electronics")

"""
Find the most affordable devices with excellent quality that fit your needs the most just by a few steps
"""

#read the input from the user
product = st.text_input("What product do you want to search for? ")

"""
The process may take some time
"""

# Send an HTTP GET request to the Back Market search URL with the 'product' query
url = requests.get(f"https://www.backmarket.com/en-us/search?q={product}")

# Parse the HTML content of the response using BeautifulSoup
soup = BeautifulSoup(url.text, "html.parser")

# Find all HTML elements with the class 'body-2-bold' (assuming this contains page information),
# and select the last one in the list ([-1])
page = soup.find_all('span',class_='body-2-bold')[-1]

# Extract the text content from the selected element and convert it to an integer
# it is the total number of pages
page_text = int(page.text.strip())

product_names = []
prices = []
rates = []
links = []

# Traverse all the pages and all products of each page
for page in range(1,page_text+1):
    url = requests.get(f"https://www.backmarket.com/en-us/search?q={product}&page={page}")
    soup = BeautifulSoup(url.text,"html.parser")
    relative = soup.find_all('div',class_='productCard')

    # Access each product on the current page
    # Extract the name, price, rating, and the url link of each product
    # Add the info into the proper lists
    for i in relative:
        items = i.find_all('h2')
        for item in items:
            product_name = str(items).splitlines()[-2].strip()
            product_names.append(product_name)
            print(f"Product name: {product_name}")

            price = i.find(attrs={'data-qa':'prices'}).text.replace(",","").replace("$","").strip()
            prices.append(price)
            print(f"The price: {price}")

            rate = i.find(class_="ml-1 text-primary body-2-bold")
            if rate is None:
                rates.append("None")
                print(f"No rate")
            else:
                rates.append(str(rate.text.strip()))
                print("Rate: " + rate.text.strip())


            link = "backmarket.com" + i.a['href']
            links.append(link)
            print(f"Link: {link}")
            print('')

# Create a dictionary to store the data
data = {'Product name':product_names,
        'Price ($)':prices,
        'Rate':rates,
        'Link':links}

# Create a DataFrame 'df' using the 'data' dictionary
df = pd.DataFrame(data)

# Convert the 'Price ($)' column to a float data type
df['Price ($)'] = df['Price ($)'].astype(float)

# Sort the DataFrame 'df' by the price in ascending order,
# and reset the index to ensure it's displayed in the correct order
df_sorted = df.sort_values(by=["Price ($)"], ignore_index=True)

# Display the data
st.dataframe(df_sorted)


