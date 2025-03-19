import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request
from googlesearch import search
import random

app = Flask(__name__)

def search_google(query, num_results=15):
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for url in search(query, num_results=num_results):
        if "/search?" in url:  # 過濾掉 Google 自己的搜尋頁面
            continue
        try:
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            results.append(f"🔹 Google: {title} - {url}")
        except Exception:
            results.append(f"🔹 Google: [無法獲取標題] - {url}")

    return results[:10]

def search_bing(query):
    url = f"https://www.bing.com/search?q={query}"
    response = requests.get(url)
    if response.status_code != 200:
        return ["Bing search failed."]

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for b in soup.find_all('li', class_='b_algo'):
        title_tag = b.find('h2')
        link_tag = b.find('a')
        if title_tag and link_tag:
            title = title_tag.text.strip()
            link = link_tag['href']
            results.append(f"🔹 Bing: {title} - {link}")

    return results[:10]

def search_yahoo(query):
    url = f"https://search.yahoo.com/search?p={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return ["Yahoo search failed."]

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for y in soup.select('ol.searchCenterMiddle li div.compTitle h3 a'):
        title = y.text.strip()
        href = y['href']
        results.append(f"🔹 Yahoo: {title} - {href}")

    return results[:10]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form['query']  # 獲取用戶輸入的搜尋關鍵字
        google_results = search_google(query)
        bing_results = search_bing(query)
        yahoo_results = search_yahoo(query)

        all_results = google_results + ['\n'] + bing_results + ['\n'] + yahoo_results  # 合併所有搜尋結果
        images = ['1.jpg', '2.jpg', '3.jpg','4.jpg','5.jpg','6.jpg','7.jpg','8.jpg']
        random_image = random.choice(images)  # 隨機選擇一張圖片

        return render_template_string("""
        <html>
            <head>
                <title>Meta Search Results</title>
                <style>
                    body {
                        background: url("{{ url_for('static', filename='video.gif') }}") no-repeat center center fixed;
                        background-size: cover;
                        color: white; /* 讓文字不被GIF蓋住 */
                        text-align: center; /* 讓標題、表單、圖片置中 */
                    }
                    .container {
                        padding: 50px;
                        background: rgba(0, 0, 0, 0.5); /* 讓內容區域半透明 */
                        width: 60%;
                        margin: auto;
                        border-radius: 10px;
                    }
                    .results {
                        text-align: left; /* 讓搜尋結果靠左 */
                        margin-top: 20px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>搜尋結果</h1>
                    <form method="POST">
                        <input type="text" name="query" placeholder="輸入搜尋關鍵字" required>
                        <button type="submit">搜尋</button>
                    </form>
                    <h3>搜尋關鍵字: {{ query }}</h3>
                    <img src="{{ url_for('static', filename=random_image) }}" alt="隨機圖片" style="width:100%; max-width: 600px;">
                    <div class="results">
                        <ul>
                            {% for result in results %}
                                {% set parts = result.split(" - ") %}
                                {% if parts|length > 1 %}
                                    <li> <a href="{{ parts[1] }}" target="_blank" style="color: yellow;">{{ parts[0] }}</a></li>
                                {% else %}
                                    <li>{{ result }}</li>
                                {% endif %}
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </body>
        </html>
        """, results=all_results, query=query, random_image=random_image)


    return render_template_string("""
    <html>
        <head>
            <title>Meta Search</title>
        </head>
        <body>
            <h1>請輸入搜尋關鍵字</h1>
            <form method="POST">
                <input type="text" name="query" placeholder="輸入搜尋關鍵字" required>
                <button type="submit">搜尋</button>
            </form>
            <img src="{{ url_for('static', filename='start.jpg') }}" style="width:100%; max-width: 600px;">
        </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(debug=True)