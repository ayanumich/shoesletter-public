# 👟 Shoesletter

**Shoesletter** is an automated email service that sends weekly Nike shoe roundups to your friends — fully hands-off, powered by **GitHub Actions**, **Google Sheets**, and **Selenium**.

People can sign up here:  
👉 https://shoesletter.github.io/join/

> ⚠️ **Important**  
> This repository is **NOT** the live production repo.  
> It is a **reference implementation** intended for learning, extending, or building your own version of Shoesletter.

---

## ✨ What Shoesletter Does

- Collects signups via a Google Form  
- Stores user preferences in Google Sheets  
- Scrapes new Nike shoe releases (Men’s, Women’s, Unisex)  
- Selects affordable shoes automatically  
- Generates clean HTML emails with images, prices, and buy links  
- Sends personalized weekly emails  
- Runs entirely on **GitHub Actions** (no server required)

---

## 🧠 How It Works

1. Users sign up through the Shoesletter form  
2. Responses are stored in Google Sheets  
3. A GitHub Action runs on a schedule  
4. The script:
   - Reads users from Google Sheets  
   - Scrapes Nike’s website using Selenium  
   - Builds a custom HTML email per user  
   - Sends the email via Gmail SMTP  

No backend server. No database. Just automation.

---

## 🧱 Tech Stack

- Python  
- Selenium (Headless Chrome)  
- Google Sheets API  
- Gmail SMTP  
- GitHub Actions  
- HTML + CSS (Email Templates)

---

## Running 

If you want to try this out yourself you'll need to edit the config.json to use your own Sheets API as well as a Gmail App Password to allow the code to send emails. Best of luck!

