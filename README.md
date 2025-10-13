# Twitter Scraper - @IndoPopBase

Scraping data dari akun Twitter **@IndoPopBase** untuk analisis engagement dan sentiment.

## 🎯 Tujuan
- Scrape tweets dari akun @IndoPopBase
- Scrape mentions (@IndoPopBase)
- Analisis engagement (likes, retweets, replies)
- Sentiment analysis
- Dashboard visualisasi

---

## 🚀 Quick Start (Termudah)

### 1. Install Dependencies
```bash
pip install ntscraper pandas
```

### 2. Run Scraper
```bash
python quick_scraper.py
```

### 3. Check Results
Data akan tersimpan di folder `data/` dalam format CSV.

---

## 📦 Installation (Complete)

### Opsi 1: Install Minimal (Recommended)
```bash
pip install -r requirements.txt
```

### Opsi 2: Install Semua Tools
```bash
# Install all scraping methods
pip install ntscraper twscrape tweety-ns pandas tqdm
```

### Opsi 3: Manual Install
```bash
pip install ntscraper pandas tqdm
```

---

## 🔧 Available Methods

### Method 1: ntscraper (RECOMMENDED - PALING MUDAH)
✅ **Kelebihan:**
- Tidak perlu login Twitter
- Simple & cepat
- Free & no rate limit
- Ready to use

❌ **Kekurangan:**
- Terbatas data yang bisa di-scrape
- Kadang instance Nitter down

**Usage:**
```python
from ntscraper import Nitter

scraper = Nitter()
tweets = scraper.get_tweets("IndoPopBase", mode='user', number=500)
```

### Method 2: twscrape (PALING STABIL)
✅ **Kelebihan:**
- Paling stabil & reliable
- Bisa scrape data banyak
- Support async

❌ **Kekurangan:**
- Perlu setup dummy Twitter account
- Setup lebih kompleks

**Setup:**
```bash
pip install twscrape

# Add dummy Twitter account
twscrape add_accounts accounts.txt  # username:password:email:email_password
twscrape login_accounts
```

### Method 3: tweety-ns (BALANCE)
✅ **Kelebihan:**
- Balance antara mudah & powerful
- Dokumentasi bagus

❌ **Kekurangan:**
- Perlu install dependencies tambahan

### Method 4: Selenium (FALLBACK)
✅ **Kelebihan:**
- Selalu work (selama Twitter website accessible)
- Bisa scrape semua yang visible

❌ **Kekurangan:**
- SANGAT lambat
- Perlu browser driver
- Resource intensive

---

## 📊 Data Output

### Struktur CSV - Tweets
```csv
date, username, content, likes, retweets, replies, url
```

### Struktur CSV - Mentions
```csv
date, username, content, likes, retweets, replies, url
```

### Example Output Location
```
data/
├── IndoPopBase_tweets_20241002_120000.csv
└── IndoPopBase_mentions_20241002_120100.csv
```

---

## 💡 Tips & Best Practices

### 1. Scraping Strategy
```python
# Start small untuk testing
scraper.scrape_tweets(num_tweets=100)

# Gradually increase
scraper.scrape_tweets(num_tweets=500)

# For production
scraper.scrape_tweets(num_tweets=3000)
```

### 2. Error Handling
Jika satu method gagal, coba method lain:
```
ntscraper → tweety-ns → twscrape → selenium
```

### 3. Rate Limiting
- ntscraper: Biasanya no limit, tapi tergantung Nitter instance
- twscrape: Gunakan multiple accounts untuk avoid limit
- Selenium: Add delays antara requests

### 4. Data Validation
```python
# Check missing values
df.isnull().sum()

# Remove duplicates
df.drop_duplicates(subset=['url'], inplace=True)

# Validate dates
df['date'] = pd.to_datetime(df['date'])
```

---

## 🐛 Troubleshooting

### Error: "ntscraper not found"
```bash
pip install --upgrade ntscraper
```

### Error: "No Nitter instance available"
```python
# Nitter instances kadang down, tunggu beberapa menit dan retry
# Atau gunakan method alternatif
```

### Error: "Rate limit exceeded"
- Tunggu beberapa menit
- Gunakan method lain
- Setup multiple accounts (untuk twscrape)

### Error: "No tweets found"
- Check username spelling
- Check akun tidak private
- Try dengan query berbeda

---

## 🎓 Next Steps

### 1. Data Cleaning & Preprocessing
```bash
# Coming soon: preprocessing script
python preprocess_data.py
```

### 2. Sentiment Analysis
```bash
# Coming soon: sentiment analysis
python sentiment_analysis.py
```

### 3. Engagement Analysis
```bash
# Coming soon: engagement metrics
python engagement_analysis.py
```

### 4. Dashboard
```bash
# Coming soon: interactive dashboard
streamlit run dashboard.py
```

---

## 📚 Resources

### Twitter Scraping
- [ntscraper documentation](https://github.com/bocchilorenzo/ntscraper)
- [twscrape documentation](https://github.com/vladkens/twscrape)
- [tweety-ns documentation](https://github.com/mahrtayyab/tweety)

### Data Analysis
- [Pandas documentation](https://pandas.pydata.org/)
- [Sentiment Analysis Guide](https://huggingface.co/docs/transformers/)

---

## ⚖️ Legal & Ethical Considerations

⚠️ **PENTING:**
- Scraping untuk **research/academic purposes** adalah legal
- **Jangan** scrape untuk spam atau harassment
- **Respect** Twitter Terms of Service
- **Jangan** overload servers dengan requests berlebihan
- **Pertimbangkan** privacy users dalam analisis

### Recommendations:
1. Gunakan data hanya untuk analisis agregat
2. Jangan publish data pribadi users
3. Add delays antara requests
4. Use rate limiting
5. Respect robots.txt

---

## 🤝 Contributing

Jika Anda menemukan bug atau punya improvement:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push dan create Pull Request

---

## 📧 Contact

Untuk pertanyaan atau diskusi proyek, silakan buat issue di repository.

---

## 📝 License

MIT License - Feel free to use for academic/research purposes.

---

**Happy Scraping! 🚀**