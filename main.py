import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from googleapiclient.discovery import build
from google.cloud import language

import requests
import json

import smtplib
from email.message import EmailMessage

import concurrent.futures

from datetime import date

# https://shoesletter.github.io/join/


today = date.today()


with open('config.json') as config_file:
    config = json.load(config_file)

# Spreadsheet ID
APP_PASSWORD = config.get('APP_PASSWORD')
SPREADSHEET_ID = config.get('GOOGLE_SPREADSHEET_ID')
if not SPREADSHEET_ID:
    raise ValueError("Google Spreadsheet ID not found in config.json")
API_KEY = config.get('GOOGLE_SHEETS_API_KEY')
if not API_KEY:
    raise ValueError("API key not found in config.json.")

def authenticate_sheets(api_key):
    return build('sheets', 'v4', developerKey=api_key).spreadsheets()

class Person():
    def __init__(self, name, email, brand, size, sex):
        self.name = name
        self.email = email
        self.brand = brand
        self.size = size
        self.sex = sex

def get_emails():
    sheets = authenticate_sheets(API_KEY)
    
    # Fetch all data from the first sheet
    result = sheets.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Form Responses 1'
    ).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return []

    # The first row is typically headers, so skip it
    data = []
    for row in values[1:]:
        # Safely extract each column; use None if not present or blank
        email = row[1] if len(row) > 1 and row[1] else None
        first_name = row[2] if len(row) > 2 and row[2] else None
        shoe_size = row[3] if len(row) > 3 and row[3] else None
        favorite_brand = row[4] if len(row) > 4 and row[4] else None
        shoe_sex = row[5] if len(row) > 5 and row[5] else None
        
        data.append(Person(first_name, email, favorite_brand, shoe_size, shoe_sex))

    return data

class Email:
    def __init__(self, sender, password, recipients, subject, html_body):
        self.sender = sender
        self.password = password  # app password

        # Accept either a single recipient as string or multiple recipients as a list.
        if isinstance(recipients, str):
            self.recipients = [recipients]
        else:
            self.recipients = recipients

        self.subject = subject
        self.html_body = html_body  # The full HTML content

        self.message = EmailMessage()
        self.message["From"] = self.sender
        # Join multiple recipients with a comma-separated string
        self.message["To"] = ", ".join(self.recipients)
        self.message["Subject"] = self.subject

        # Plain text fallback
        self.message.set_content("This email contains HTML content. Please view it in an HTML-compatible email client.")

        # HTML email body
        self.message.add_alternative(html_body, subtype='html')

        self.smtp_server = "smtp.gmail.com"
        self.port = 587 

    def send(self):
        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(self.message)
            return f"Email sent successfully to {self.recipients}"
        except Exception as e:
            return f"Error: {e}"


# Shoe() datatype that holds all info about any one shoe
class Shoe():
    def __init__(self, image_link, name, price, buy_link):
        self.image_link = image_link
        self.name = name
        self.price = price
        self.buy_link = buy_link
    def __str__(self):
        return f"{self.name:<50} ${self.price:<4}"


# The Swoosh() Class is a wrapper for the headless web driver
class Swoosh():
    def __init__(self, gender, display=True):
        if display:
            print("Intializing...")

        if gender == "Men's":
            url_link = 'https://www.nike.com/w/new-mens-shoes-3n82yznik1zy7ok'
        elif gender == "Women's": 
            url_link = 'https://www.nike.com/w/new-womens-shoes-3n82yz5e1x6zy7ok'
        else:
            url_link = 'https://www.nike.com/w/new-unisex-shoes-3n82yz3rauvzqrpuzy7ok'
        self.url = url_link

        service = Service() 
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        if display:
            print("Added service options...")
        drive = webdriver.Chrome(service=service, options=options) 
        if display:
            print("Created WebDriver...")
        
        drive.get(self.url)
        if display:
            print("Fetching URL...")
        self.driver = drive
        if display:
            print("Setup complete...\n")
    
    # Grab a single shoe 
    def fetch_shoe(self, x, display=True):
        
        try:
            # Find all shoe elements on the page
            shoe_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.product-card__price-wrapper')
            name_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.product-card__title')
            img_elems = self.driver.find_elements(By.CSS_SELECTOR, 'img.product-card__hero-image')

            buy_link = self.driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')[x - 1].get_attribute('href')
            
            if x > len(img_elems) or x <= 0:
                print(f"Error: Shoe number {x} is out of range. Total shoes found: {len(img_elems)}")
                return
            
            # Get the x-th shoe image URL (adjusting for zero-indexing)
            img_url = img_elems[x - 1].get_attribute('src')
            price = shoe_elements[x - 1].find_element(By.CSS_SELECTOR, 'div.product-price').text
            name = name_elements[x-1].text

            # Fetch and display the image
            response = requests.get(img_url)
            if response.status_code == 200:
                return Shoe(img_url, name, float(price[1:]), buy_link)
            else:
                print(f"Error fetching image: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
    
    def get_all_listings(self, select=5): 

        shoes = []

        total=24

        for i in range(1,total+1):
            shoe = self.fetch_shoe(i, display=False)
            shoes.append(shoe)

        sorted_shoes = sorted(shoes, key=lambda shoe: shoe.price)
        
        sub_sorted_shoes = []
        for s in range(select):
            shuz = random.choice(sorted_shoes)
            sub_sorted_shoes.append(shuz)
            sorted_shoes.remove(shuz)

        return sub_sorted_shoes
    

# Takes in the user, sends that person an email
def grab_roundup(user):

    input_email = str(user.email)
    email_array = [input_email]
    input_size = str(user.size)

    input_name = str(user.name)

    input_sex = str(user.sex)

    print(f"Attempting send to {input_name} at {input_email} size {input_size} {input_sex} shoes")

    try:
        sneaker_head = Swoosh(input_sex)
        shoes = sneaker_head.get_all_listings(select=5)
    except Exception as exc:
        print(f"Unable to fetch shoes for {input_name}: {exc}")
        

    if len(shoes) > 1:
        print(f"we got shoes for {input_name}")
    

    html_body = f"""\
    <html>
        <head>
            <meta charset="UTF-8">
            <title>Shoe Deals</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f7f7f7;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 800px;
                    margin: auto;
                    background-color: #fff;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                h2 {{
                    color: #333;
                    text-align: center;
                }}
                h3 {{
                    color: #333;
                    text-align: center;
                }}
                .shoe-list {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
                    gap: 20px;
                    list-style-type: none;
                    padding: 0;
                }}
                .shoe-item {{
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                    background-color: #fafafa;
                }}
                .shoe-item img {{
                    width: 100%;
                    max-width: 200px;
                    height: auto;
                    border-radius: 4px;
                }}
                .shoe-name {{
                    font-size: 1.1rem;
                    font-weight: bold;
                    margin: 10px 0 5px;
                    color: #222;
                }}
                .shoe-price {{
                    color: #e67e22;
                    font-size: 1rem;
                    margin-bottom: 8px;
                }}
                .buy-link {{
                    text-decoration: none;
                    color: #fff;
                    background-color: #3498db;
                    padding: 8px 12px;
                    border-radius: 4px;
                    transition: background-color 0.3s;
                }}
                .buy-link:hover {{
                    background-color: #2980b9;
                }}
                .footer {{
                    margin-top: 20px;
                    text-align: center;
                    color: #777;
                    font-size: 0.9rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>{user.name}'s Weekly Shoe Roundup</h2>
                <h3>{today}</h3>
                <ul class="shoe-list">
                    {''.join([
                        f'<li class="shoe-item">'
                        f'<img src="{shoe.image_link}" alt="{shoe.name}">'
                        f'<div class="shoe-name">{shoe.name}</div>'
                        f'<div class="shoe-price">${shoe.price}</div>'
                        f'<a class="buy-link" href="{shoe.buy_link}">Cop it here</a>'
                        f'</li>'
                        for shoe in shoes
                    ])}
                </ul>
                <div class="footer">© {today} shoesletter</div>
            </div>
        </body>
    </html>
    """

    email = Email(
        sender = "example@gmail.com", # Must be an email you own!
        password = APP_PASSWORD,
        recipients = email_array,
        subject=f"[{today}] Shoesletter Weekly",
        html_body=html_body
    )

    print(email.send())

    return 0


# Main Loop that runs in GitHub Actions
if __name__ == '__main__':
    
    users = get_emails()

    # Uses threading to send all emails at once!
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(users)) as executor:
        future_to_user = {executor.submit(grab_roundup, user): user for user in users}
        
        for future in concurrent.futures.as_completed(future_to_user):
            user = future_to_user[future]
            try:
                result = future.result()
                print(f"Result for {user}: {result}")
            except Exception as exc:
                print(f"User {user} generated an exception: {exc}")


