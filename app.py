from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
CORS(app)

@app.route("/", methods=['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route('/scrap', methods=['POST'])
def index():
    if request.method == 'POST':
        searchString = request.form['container'].replace(" ", "")
        try:
            # Scraping Flipkart search results
            flipkart_url = f"https://www.flipkart.com/search?q={searchString}"
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")

            bigboxes = flipkart_html.find_all("div", {"class": "cPHDOP col-12-12"})  
            if len(bigboxes) < 3:  # If less than 3 products, return error
                return render_template('error.html', error_message="Not enough products found. Try a different search.")

            all_reviews = []  # List to store all reviews

            # Iterate through products starting from the 3rd product (index 2)
            for box in bigboxes[2:10]:
                try:
                    productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                    prodRes = requests.get(productLink)
                    prod_html = bs(prodRes.text, "html.parser")

                    commentboxes = prod_html.find_all('div', {'class': "RcXBOT"})  
                    if not commentboxes:
                        continue  # Skip if no reviews found

                    for commentbox in commentboxes:
                        try:
                            name = commentbox.find('p', {'class': '_2NsDsF AwS1CA'}).text.strip()
                        except:
                            name = 'No Name'

                        try:
                            rating = commentbox.find('div', {'class': 'XQDdHH Ga3i8K'}).text.strip()
                        except:
                            rating = 'No Rating'

                        try:
                            commentHead = commentbox.find('p', {'class': 'z9E0IG'}).text.strip()
                        except:
                            commentHead = 'No Comment Heading'

                        try:
                            custComment = commentbox.find('div', {'class': 'ZmyHeo'}).div.text.strip()
                        except:
                            custComment = 'No Customer Comment'

                        mydict = {
                            "Product": searchString,
                            "Product Link": productLink,
                            "Name": name,
                            "Rating": rating,
                            "CommentHead": commentHead,
                            "Comment": custComment
                        }
                        all_reviews.append(mydict)

                except Exception as e:
                    print(f"Error scraping product: {e}")
                    continue  # Skip to next product if an error occurs

            if not all_reviews:  # If no reviews were collected
                return render_template('error.html', error_message="No reviews found for any product.")

            return render_template('results.html', reviews=all_reviews)

        except Exception as e:
            print("Error:", e)
            return render_template('error.html', error_message="Something went wrong. Please try again later.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)

