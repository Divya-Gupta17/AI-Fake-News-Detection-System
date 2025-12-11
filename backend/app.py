# # # app.py
# # import os
# # import json
# # import nltk
# # nltk.download('punkt', quiet=True)

# # from flask import Flask, request, jsonify, render_template, session, redirect, url_for
# # from flask_cors import CORS
# # from bson.objectid import ObjectId
# # from datetime import datetime
# # import requests
# # from bs4 import BeautifulSoup
# # from newspaper import Article
# # import tldextract
# # from werkzeug.security import generate_password_hash

# # from config import Config
# # from db import users, user_preferences, news, reports, saved_articles
# # from auth import (
# #     register_user, login_user, logout_user,
# #     get_user_preferences, update_user_preferences, login_required
# # )
# # # Import loaders available in your model_utils.py
# # from model_utils import (
# #     classify_topic, predict_authenticity, summarize_text,
# #     fact_check_with_google, predict_hf, init_hf_model,
# #     load_bert_model, load_summarizer
# # )
# # from multi_news_api import fetch_all_sources

# # app = Flask(__name__, template_folder="../templates", static_folder="../static")
# # app.config.from_object(Config)
# # app.secret_key = Config.SECRET_KEY

# # # CORS
# # CORS(app, supports_credentials=True)
# # app.config["CORS_HEADERS"] = "Content-Type"

# # # preload HF if desired
# # try:
# #     init_hf_model()
# # except Exception:
# #     pass

# # # Pre-warm local BERT and summarizer by calling the loader functions available
# # try:
# #     load_bert_model()
# # except Exception as e:
# #     print("⚠️ load_bert_model() failed at startup:", e)

# # try:
# #     load_summarizer()
# # except Exception as e:
# #     print("⚠️ load_summarizer() failed at startup:", e)

# # print("✅ Model warm-up attempted at startup.")

# # # Debug listing of model path (remove in production if desired)
# # try:
# #     mp = getattr(Config, "MODEL_PATH", None)
# #     if mp and os.path.isdir(mp):
# #         print("Model path contents:", os.listdir(mp))
# #     else:
# #         print("Config.MODEL_PATH not set or not a directory:", mp)
# # except Exception as e:
# #     print("Model path debug error:", e)


# # @app.after_request
# # def add_no_cache(response):
# #     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
# #     response.headers["Pragma"] = "no-cache"
# #     response.headers["Expires"] = "0"
# #     return response

# # # default admin creation
# # def create_default_admin():
# #     try:
# #         admin = users.find_one({"username": "Admin17"})
# #         if not admin:
# #             users.insert_one({
# #                 "username": "Admin17",
# #                 "password": generate_password_hash("Divya830@1789"),
# #                 "is_admin": True,
# #                 "created_at": datetime.utcnow()
# #             })
# #             print("✔ Default admin created")
# #         else:
# #             print("✔ Admin already exists")
# #     except Exception as e:
# #         print("Error creating default admin:", e)

# # create_default_admin()

# # # --------------------------
# # # Compatibility wrapper
# # # --------------------------
# # def predict_auth_compat(text):
# #     """
# #     Call predict_authenticity() and normalize to (label_str, float_conf).
# #     label_str: 'Real' | 'Fake' | 'Unknown'
# #     """
# #     try:
# #         res = predict_authenticity(text)
# #         if isinstance(res, tuple) and len(res) == 2:
# #             lab, conf = res
# #             # old style: integer label (0 or 1)
# #             if isinstance(lab, int):
# #                 label = "Real" if lab == 1 else "Fake"
# #                 conf = float(conf or 0.0)
# #                 return label, conf
# #             # new style: string label
# #             if isinstance(lab, str):
# #                 lab_u = lab.strip().lower()
# #                 if lab_u in ("real", "true", "legit", "1"):
# #                     return "Real", float(conf or 0.0)
# #                 if lab_u in ("fake", "false", "misinformation", "0"):
# #                     return "Fake", float(conf or 0.0)
# #                 # otherwise return raw label w/ confidence
# #                 return lab, float(conf or 0.0)
# #         # fallback
# #         return "Unknown", 0.0
# #     except Exception as e:
# #         print("predict_auth_compat error:", e)
# #         return "Unknown", 0.0


# # # Pages
# # @app.get("/")
# # def home_page():
# #     # Always show home page, even if logged in
# #     return render_template(
# #         "index.html",
# #         username=session.get("username"),
# #         is_admin=session.get("is_admin", False)
# #     )

# # @app.get("/features")
# # def features_page():
# #     return render_template("features.html")

# # @app.get("/login")
# # def login_page():
# #     # If already logged in, send to home instead of dashboard
# #     if session.get("user_id"):
# #         return redirect(url_for("home_page"))
# #     return render_template("login.html")

# # @app.get("/register")
# # def register_page():
# #     if session.get("user_id"):
# #         return redirect(url_for("dashboard_page"))
# #     return render_template("register.html")

# # @app.get("/dashboard")
# # @login_required
# # def dashboard_page():
# #     return render_template("dashboard.html", username=session.get("username"))

# # @app.get("/admin/dashboard")
# # @login_required
# # def admin_dashboard_page():
# #     if not session.get("is_admin"):
# #         return redirect(url_for("dashboard_page"))
# #     return render_template("admin.html", username=session.get("username"))

# # @app.get("/about")
# # def about_page():
# #     return render_template("about.html")

# # @app.get("/contact")
# # def contact_page():
# #     return render_template("contact.html")

# # # Auth routes
# # @app.post("/register")
# # def route_register():
# #     data = request.json or {}
# #     ok, msg = register_user(data.get("username"), data.get("password"))
# #     return (jsonify({"message": "User registered", "user_id": msg}), 201) if ok else (jsonify({"message": msg}), 409)

# # @app.post("/login")
# # def route_login():
# #     data = request.json or {}
# #     username = data.get("username")
# #     password = data.get("password")

# #     ok, user = login_user(username, password)
# #     if not ok:
# #         return jsonify({"message": user}), 401

# #     session["user_id"] = str(user["_id"])
# #     session["username"] = user["username"]
# #     session["logged_in"] = True
# #     session["is_admin"] = user.get("is_admin", False)

# #     # ✅ After login, go to HOME for both admin and normal user
# #     return jsonify({"redirect": "/"}), 200

# # @app.get("/logout")
# # @login_required
# # def route_logout_get():
# #     logout_user()
# #     session.clear()
# #     return redirect(url_for("home_page"))

# # @app.post("/logout")
# # @login_required
# # def route_logout():
# #     logout_user()
# #     session.clear()
# #     return jsonify({"message": "Logged out"})

# # # Preferences
# # @app.get("/user/preferences")
# # @login_required
# # def route_get_prefs():
# #     prefs = get_user_preferences(session["user_id"])
# #     if not prefs:
# #         prefs = {"topics": [], "sources": [], "type": "all", "username": session.get("username", "User")}
# #     return jsonify(prefs)

# # @app.put("/user/preferences")
# # @login_required
# # def route_put_prefs():
# #     prefs = request.json or {}
# #     ok = update_user_preferences(session["user_id"], prefs)
# #     return jsonify({"message": "Preferences updated."}), 200

# # @app.get("/privacy")
# # def privacy_page():
# #     return render_template("privacy.html")

# # # URL extraction helper (improved headers + timeouts)
# # def extract_text_from_url(url):
# #     headers = {
# #         "User-Agent": "Mozilla/5.0",
# #     }

# #     # 1) Newspaper3k
# #     try:
# #         art = Article(url)
# #         art.download()
# #         art.parse()
# #         if art.text and len(art.text.strip()) > 50:
# #             return art.text
# #     except Exception:
# #         pass

# #     # 2) Readability
# #     try:
# #         r = requests.get(url, headers=headers, timeout=10)
# #         from readability import Document
# #         doc = Document(r.text)
# #         soup = BeautifulSoup(doc.summary(), "html.parser")
# #         text = soup.get_text(separator="\n")
# #         if len(text.strip()) > 50:
# #             return text
# #     except Exception:
# #         pass

# #     # 3) Basic HTML parsing
# #     try:
# #         r = requests.get(url, headers=headers, timeout=10)
# #         soup = BeautifulSoup(r.text, "html.parser")
# #         p_tags = soup.find_all("p")
# #         text = "\n".join([p.get_text() for p in p_tags])
# #         if len(text.strip()) > 50:
# #             return text
# #     except Exception:
# #         pass

# #     return None

# # # Credibility helpers (unchanged)
# # TRUSTED_DOMAINS = {
# #     "bbc.co.uk": 0.96, "bbc.com": 0.96, "reuters.com": 0.97, "apnews.com": 0.96,
# #     "cnn.com": 0.90, "nytimes.com": 0.94, "theguardian.com": 0.92, "bloomberg.com": 0.93
# # }
# # def domain_reputation_score(url):
# #     try:
# #         dom = tldextract.extract(url).registered_domain
# #         return TRUSTED_DOMAINS.get(dom, 0.40)
# #     except Exception:
# #         return 0.40

# # def compute_credibility(hf_conf, domain_score, fact_present, reported_fake_count):
# #     """
# #     New credibility function:
# #     HF Fake → negative confidence
# #     HF Real → positive confidence
# #     Domain + fact check + user reports support final score
# #     """

# #     # -----------------------------
# #     # 1️⃣ Signed HF confidence
# #     # -----------------------------
# #     signed_hf = hf_conf   # Real stays +, Fake stays - (handled in predict_hf)

# #     # -----------------------------
# #     # 2️⃣ Fact-check score
# #     # -----------------------------
# #     fact_score = 1.0 if fact_present else 0.20

# #     # -----------------------------
# #     # 3️⃣ User reports
# #     # -----------------------------
# #     if reported_fake_count >= 3:
# #         user_score = -0.50
# #     elif reported_fake_count == 2:
# #         user_score = -0.20
# #     else:
# #         user_score = 0

# #     # 4️⃣ Weighted Final Score
# #     cred_score = (
# #         (signed_hf * 0.55) +
# #         (domain_score * 0.20) +
# #         (fact_score * 0.15) +
# #         (user_score * 0.10)
# #     )

# #     # Normalize -1 → +1 to 0 → 1
# #     final = max(min((cred_score + 1) / 2, 1), 0)
# #     # 5️⃣ Final Labels
# #     if final >= 0.70:
# #         label = "High (Real)"
# #     elif final >= 0.40:
# #         label = "Medium (Uncertain)"
# #     else:
# #         label = "Low (Fake)"

# #     return round(final, 3), label

# # # News endpoints
# # @app.get("/news")
# # @login_required
# # def route_news():
# #     prefs = get_user_preferences(session["user_id"]) or {}
# #     topics = prefs.get("topics", [])
# #     sources_pref = prefs.get("sources", [])
# #     view_type = prefs.get("type", "all")

# #     try:
# #         query = " OR ".join(topics) if topics else "breaking news"
# #         fresh_articles = fetch_all_sources(query=query, limit=20)
# #         for art in fresh_articles:
# #             try:
# #                 insert_article(art)
# #             except Exception:
# #                 continue
# #     except Exception:
# #         pass

# #     pipeline = []
# #     match = {}
# #     if topics:
# #         match["topic"] = {"$in": topics}
# #     if sources_pref:
# #         match["source"] = {"$in": sources_pref}
# #     if view_type == "verified":
# #         match["prediction"] = "Real"
# #     if match:
# #         pipeline.append({"$match": match})

# #     pipeline += [
# #         {"$group": {"_id": "$url", "doc": {"$first": "$$ROOT"}}},
# #         {"$replaceRoot": {"newRoot": "$doc"}},
# #         {"$addFields": {"_sortDate": {"$cond":[
# #             {"$regexMatch":{"input":"$published_at","regex":"^[0-9]{4}-[0-9]{2}-[0-9]{2}" }},
# #             {"$toDate":"$published_at"},
# #             {"$toDate":{"$toString":"$_id"}}
# #         ]}}}, 
# #         {"$sort": {"_sortDate": -1}},
# #         {"$project":{"_sortDate":0}},
# #         {"$limit": 50}
# #     ]

# #     saved_news = list(news.aggregate(pipeline))
# #     final = []
# #     for a in saved_news:
# #         rpt_count = reports.count_documents({"url": a.get("url")})
# #         rpt_fake = reports.count_documents({"url": a.get("url"), "label":"Fake"})
# #         user_reported = False
# #         try:
# #             uid = ObjectId(session["user_id"])
# #             user_reported = reports.find_one({"url": a.get("url"), "user_id": uid}) is not None
# #         except Exception:
# #             user_reported = False

# #         text_for_pred = (a.get("title","") + " " + (a.get("description") or ""))
# #         hf_label, hf_conf = predict_hf(text_for_pred)
# #         hf_conf = float(hf_conf or 0.0)

# #         domain_score = domain_reputation_score(a.get("url") or "")
# #         fact_present = True if a.get("fact_check") else False
# #         cred_score, cred_label = compute_credibility(hf_conf, domain_score, fact_present, rpt_fake)

# #         if view_type == "verified" and hf_label != "Real":
# #             continue

# #         final.append({
# #             "title": a.get("title",""),
# #             "description": a.get("description",""),
# #             "summary": a.get("summary",""),
# #             "content": a.get("content",""),
# #             "url": a.get("url", "#"),
# #             "image_url": a.get("image_url"),
# #             "source": a.get("source", "Unknown"),
# #             "topic": a.get("topic", "General"),
# #             "prediction": hf_label,
# #             "confidence": hf_conf,
# #             "published_at": a.get("published_at"),
# #             "fact_check": a.get("fact_check"),
# #             "reported_count": rpt_count,
# #             "reported_fake_count": rpt_fake,
# #             "user_reported": user_reported,
# #             "credibility_score": cred_score,
# #             "credibility_label": cred_label
# #         })
# #     return jsonify(final)

# # # admin news
# # @app.get("/admin/news")
# # @login_required
# # def route_admin_news():
# #     if not session.get("is_admin"):
# #         return jsonify([]), 403

# #     prefs = get_user_preferences(session["user_id"]) or {}
# #     topics = prefs.get("topics", [])
# #     sources_pref = prefs.get("sources", [])
# #     view_type = prefs.get("type", "all")

# #     pipeline = []
# #     match = {}
# #     if topics: match["topic"] = {"$in": topics}
# #     if sources_pref: match["source"] = {"$in": sources_pref}
# #     if view_type == "verified": match["prediction"] = "Real"
# #     if match: pipeline.append({"$match": match})

# #     pipeline += [
# #         {"$group": {"_id": "$url", "doc": {"$first": "$$ROOT"}}},
# #         {"$replaceRoot": {"newRoot": "$doc"}},
# #         {"$addFields": {"_sortDate": {"$cond":[
# #             {"$regexMatch":{"input":"$published_at","regex":"^[0-9]{4}-[0-9]{2}-[0-9]{2}" }},
# #             {"$toDate":"$published_at"},
# #             {"$toDate":{"$toString":"$_id"}}
# #         ]}}}, 
# #         {"$sort": {"_sortDate": -1}},
# #         {"$project":{"_sortDate":0}},
# #         {"$limit": 100}
# #     ]

# #     saved_news = list(news.aggregate(pipeline))
# #     final = []
# #     for a in saved_news:
# #         rpt_count = reports.count_documents({"url": a.get("url")})
# #         rpt_fake = reports.count_documents({"url": a.get("url"), "label":"Fake"})

# #         text_for_pred = (a.get("title","") + " " + (a.get("description") or ""))

# #         try:
# #             bert_label, bert_conf = predict_auth_compat(text_for_pred)
# #             bert_conf = float(bert_conf or 0.0)
# #         except Exception:
# #             bert_label, bert_conf = "Unknown", 0.0

# #         hf_label, hf_conf = predict_hf(text_for_pred)
# #         hf_conf = float(hf_conf or 0.0)

# #         domain_score = domain_reputation_score(a.get("url") or "")
# #         fact_present = True if a.get("fact_check") else False
# #         cred_score, cred_label = compute_credibility(hf_conf, domain_score, fact_present, rpt_fake)

# #         final.append({
# #             "title": a.get("title",""),
# #             "description": a.get("description",""),
# #             "summary": a.get("summary",""),
# #             "content": a.get("content",""),
# #             "url": a.get("url", "#"),
# #             "image_url": a.get("image_url"),
# #             "source": a.get("source", "Unknown"),
# #             "topic": a.get("topic", "General"),
# #             "prediction_hf": hf_label,
# #             "confidence_hf": hf_conf,
# #             "prediction_bert": bert_label,
# #             "confidence_bert": bert_conf,
# #             "published_at": a.get("published_at"),
# #             "fact_check": a.get("fact_check"),
# #             "reported_count": rpt_count,
# #             "reported_fake_count": rpt_fake,
# #             "credibility_score": cred_score,
# #             "credibility_label": cred_label
# #         })
# #     return jsonify(final)

# # # insert_article (uses predict_auth_compat)
# # def insert_article(a):
# #     url = a.get("url")
# #     if not url:
# #         return
# #     try:
# #         if news.count_documents({"url": url}, limit=1) > 0:
# #             return
# #     except Exception:
# #         pass

# #     title = a.get("title","") or ""
# #     desc = a.get("description","") or ""
# #     text = f"{title} {desc}"

# #     topic = classify_topic(text)
# #     try:
# #         lab, conf = predict_auth_compat(text)
# #         prediction = lab if lab in ("Real", "Fake") else "Unknown"
# #         conf = float(conf or 0.0)
# #     except Exception:
# #         hf_lab, hf_conf = predict_hf(text)
# #         prediction = hf_lab
# #         conf = float(hf_conf or 0.0)

# #     summary = summarize_text(a.get("content") or desc)

# #     raw_date = a.get("published_at") or a.get("publishedAt") or a.get("pubDate")
# #     try:
# #         pub_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).isoformat()
# #     except Exception:
# #         pub_at = datetime.utcnow().isoformat()

# #     fc = None
# #     if prediction == "Real":
# #         try:
# #             fact = fact_check_with_google(title)
# #             if fact:
# #                 fc = {"link": fact.get("url") if isinstance(fact, dict) else fact.get("link"),
# #                       "publisher": fact.get("title") if isinstance(fact, dict) else None,
# #                       "snippet": fact.get("snippet") if isinstance(fact, dict) else None}
# #         except Exception:
# #             fc = None

# #     try:
# #         news.insert_one({
# #             "title": title,
# #             "description": desc,
# #             "content": a.get("content"),
# #             "url": url,
# #             "image_url": a.get("image_url"),
# #             "source": a.get("source"),
# #             "topic": topic,
# #             "prediction": prediction,
# #             "confidence": float(conf),
# #             "summary": summary,
# #             "published_at": pub_at,
# #             "fact_check": fc,
# #             "reported_count": 0,
# #             "reported_fake_count": 0,
# #             "last_reported_at": None,
# #             "user_reports": 0
# #         })
# #     except Exception:
# #         return

# # # check_url endpoint
# # @app.post("/check_url")
# # @login_required
# # def check_url():
# #     data = request.json or {}
# #     url = data.get("url")
# #     if not url:
# #         return jsonify({"message":"URL missing"}), 400

# #     text = extract_text_from_url(url)
# #     if not text or len(text.strip()) < 30:
# #         return jsonify({"message":"Could not extract content from URL"}), 400

# #     hf_label, hf_conf = predict_hf(text)
# #     hf_conf = float(hf_conf or 0.0)

# #     if session.get("is_admin"):
# #         try:
# #             bert_label, bert_conf = predict_auth_compat(text)
# #         except Exception:
# #             bert_label, bert_conf = "Unknown", 0.0

# #         dom_score = domain_reputation_score(url)
# #         fact_present = False
# #         try:
# #             fc = fact_check_with_google(text.split("\n",1)[0][:200])
# #             fact_present = True if fc else False
# #         except Exception:
# #             fact_present = False
# #         cred_score, cred_label = compute_credibility(hf_conf, dom_score, fact_present, reports.count_documents({"url":url,"label":"Fake"}))
# #         return jsonify({
# #             "url": url,
# #             "prediction_hf": hf_label,
# #             "hf_confidence": hf_conf,
# #             "prediction_bert": bert_label,
# #             "bert_confidence": float(bert_conf or 0.0),
# #             "credibility_score": cred_score,
# #             "credibility_label": cred_label
# #         })
# #     else:
# #         dom_score = domain_reputation_score(url)
# #         cred_score, cred_label = compute_credibility(hf_conf, dom_score, False, reports.count_documents({"url":url,"label":"Fake"}))
# #         return jsonify({
# #             "url": url,
# #             "prediction": hf_label,
# #             "confidence": hf_conf,
# #             "credibility_score": cred_score,
# #             "credibility_label": cred_label
# #         })

# # # report endpoints
# # # ---------------- SAVE ARTICLE ----------------
# # @app.post("/save_article")
# # @login_required
# # def save_article_api():
# #     data = request.get_json() or {}
# #     url = data.get("url")

# #     if not url:
# #         return jsonify({"message": "Missing URL"}), 400

# #     # parse user id
# #     try:
# #         uid = ObjectId(session["user_id"])
# #     except Exception:
# #         return jsonify({"message": "Invalid user"}), 400

# #     # check if already saved for this user
# #     existing = saved_articles.find_one({"user_id": uid, "url": url})
# #     if existing:
# #         return jsonify({"message": "Already saved"}), 200

# #     doc = {
# #         "user_id": uid,
# #         "username": session.get("username"),
# #         "url": url,
# #         "title": data.get("title"),
# #         "source": data.get("source"),
# #         "published_at": data.get("published_at"),
# #         "prediction": data.get("prediction"),
# #         "confidence": data.get("confidence"),
# #         "saved_at": datetime.utcnow(),
# #     }

# #     try:
# #         saved_articles.insert_one(doc)
# #         return jsonify({"message": "Article saved to your profile"}), 201
# #     except Exception as e:
# #         print("Error saving article:", e)
# #         return jsonify({"message": "Error saving article"}), 500

# # @app.post("/report")
# # @login_required
# # def report_article():
# #     data = request.json or {}
# #     url = data.get("url")
# #     label = data.get("label")
# #     reason = data.get("reason", "")
# #     if not url or label not in ("Fake","Real"):
# #         return jsonify({"message":"Invalid payload"}), 400

# #     try:
# #         uid = ObjectId(session["user_id"])
# #     except Exception:
# #         return jsonify({"message":"Invalid user"}), 400

# #     existing = reports.find_one({"url": url, "user_id": uid})
# #     if existing:
# #         return jsonify({"message":"You already reported this article."}), 409

# #     rep = {
# #         "url": url,
# #         "label": label,
# #         "reason": reason,
# #         "user_id": uid,
# #         "username": session.get("username"),
# #         "timestamp": datetime.utcnow()
# #     }
# #     reports.insert_one(rep)
# #     news.update_one({"url": url}, {"$inc":{"reported_count":1,"reported_fake_count": (1 if label=="Fake" else 0)}, "$set":{"last_reported_at": datetime.utcnow()}}, upsert=False)
# #     return jsonify({"message":"Report saved."}), 201

# # @app.get("/user/reports")
# # @login_required
# # def get_user_reports():
# #     try:
# #         uid = ObjectId(session["user_id"])
# #     except Exception:
# #         return jsonify([])
# #     docs = list(reports.find({"user_id": uid}).sort("timestamp",-1).limit(50))
# #     out = []
# #     for r in docs:
# #         out.append({
# #             "url": r.get("url"),
# #             "label": r.get("label"),
# #             "reason": r.get("reason"),
# #             "timestamp": r.get("timestamp").isoformat() if r.get("timestamp") else None,
# #             "username": r.get("username")
# #         })
# #     return jsonify(out)

# # @app.get("/user/saved")
# # @login_required
# # def get_user_saved_articles():
# #     try:
# #         uid = ObjectId(session["user_id"])
# #     except Exception:
# #         return jsonify([])

# #     docs = list(saved_articles.find({"user_id": uid}).sort("saved_at", -1))
# #     out = []
# #     for d in docs:
# #         out.append({
# #             "url": d.get("url"),
# #             "title": d.get("title"),
# #             "source": d.get("source"),
# #             "published_at": d.get("published_at"),
# #             "image_url": d.get("image_url"),
# #         })
# #     return jsonify(out)

# # @app.get("/insert-news")
# # @login_required
# # def insert_news_to_db():
# #     if not session.get("is_admin"):
# #         return jsonify({"message":"forbidden"}), 403
# #     articles = fetch_all_sources(query="latest news", limit=30)
# #     inserted = 0
# #     for a in articles:
# #         try:
# #             insert_article(a)
# #             inserted += 1
# #         except Exception:
# #             continue
# #     return jsonify({"inserted": inserted})

# # @app.get("/profile")
# # @login_required
# # def profile_page():
# #     try:
# #         uid = ObjectId(session["user_id"])
# #     except Exception:
# #         uid = None

# #     saved = []
# #     if uid:
# #         saved = list(
# #             saved_articles.find({"user_id": uid}).sort("saved_at", -1)
# #         )

# #     return render_template(
# #         "profile.html",
# #         username=session.get("username"),
# #         saved_articles=saved,
# #     )

# # @app.get("/terms")
# # def terms_page():
# #     return render_template("terms.html")

# # if __name__ == "__main__":
# #     app.run(debug=Config.DEBUG, port=int(os.environ.get("PORT", 5000)))




# # app.py
# import os
# import json
# import nltk
# nltk.download('punkt', quiet=True)

# from flask import Flask, request, jsonify, render_template, session, redirect, url_for
# from flask_cors import CORS
# from bson.objectid import ObjectId
# from datetime import datetime
# import requests
# from bs4 import BeautifulSoup
# from newspaper import Article
# import tldextract
# from werkzeug.security import generate_password_hash

# from concurrent.futures import ThreadPoolExecutor
# import threading

# # Project imports (make sure these modules exist in your project)
# from config import Config
# from db import users, user_preferences, news, reports, saved_articles
# from auth import (
#     register_user, login_user, logout_user,
#     get_user_preferences, update_user_preferences, login_required
# )
# # Use the loader/predictor functions that exist in your model_utils.py
# from model_utils import (
#     classify_topic, predict_authenticity, summarize_text,
#     fact_check_with_google, predict_hf, init_hf_model,
#     load_bert_model, load_summarizer
# )
# from multi_news_api import fetch_all_sources

# # Flask app
# app = Flask(__name__, template_folder="../templates", static_folder="../static")
# app.config.from_object(Config)
# app.secret_key = Config.SECRET_KEY

# # CORS
# CORS(app, supports_credentials=True)
# app.config["CORS_HEADERS"] = "Content-Type"

# # Background thread pool for non-blocking tasks (tune max_workers for your machine)
# _BG_EXECUTOR = ThreadPoolExecutor(max_workers=4)
# _db_lock = threading.Lock()

# # How many articles to run BERT synchronously for admin requests (small number)
# SYNC_BERT_FOR_ADMIN = 3

# # Preload models at startup (best-effort)
# try:
#     init_hf_model()
# except Exception as e:
#     print("init_hf_model() failed:", e)

# try:
#     load_bert_model()
# except Exception as e:
#     print("load_bert_model() failed:", e)

# try:
#     load_summarizer()
# except Exception as e:
#     print("load_summarizer() failed:", e)

# print("✅ Model warm-up attempted at startup.")


# # -----------------------
# # Utility functions
# # -----------------------
# def predict_auth_compat(text: str):
#     """
#     Normalize predict_authenticity outputs to (label_str, float_conf)
#     Accepts older style (int_label, conf) or (str_label, conf).
#     """
#     try:
#         res = predict_authenticity(text)
#         if isinstance(res, tuple) and len(res) == 2:
#             lab, conf = res
#             if isinstance(lab, int):
#                 return ("Real" if lab == 1 else "Fake"), float(conf or 0.0)
#             if isinstance(lab, str):
#                 lab_u = lab.strip().lower()
#                 if lab_u in ("real", "true", "1"):
#                     return "Real", float(conf or 0.0)
#                 if lab_u in ("fake", "false", "0"):
#                     return "Fake", float(conf or 0.0)
#                 return lab, float(conf or 0.0)
#         return "Unknown", 0.0
#     except Exception as e:
#         print("predict_auth_compat error:", e)
#         return "Unknown", 0.0


# def run_bert_for_article(url: str, text: str):
#     """
#     Run local BERT (predict_authenticity) and update the article document.
#     Safe to call from background executor or synchronously for admin.
#     """
#     try:
#         lab, conf = predict_auth_compat(text)
#     except Exception as e:
#         print("run_bert_for_article: predict_auth_compat failed:", e)
#         lab, conf = "Unknown", 0.0

#     try:
#         with _db_lock:
#             news.update_one(
#                 {"url": url},
#                 {"$set": {
#                     "bert_prediction": lab,
#                     "bert_confidence": float(conf),
#                     "bert_pending": False,
#                     "bert_computed_at": datetime.utcnow().isoformat()
#                 }}
#             )
#     except Exception as e:
#         print("run_bert_for_article: DB update failed:", e)


# # Credibility computation that includes HF and BERT
# def compute_credibility(hf_conf, domain_score, fact_present, reported_fake_count, bert_label=None, bert_conf=0.0):
#     """
#     Returns: (score [0..1], label_str)
#     Combines HF signed/conf, BERT signed/conf, domain reputation, fact presence, and user reports.
#     """
#     try:
#         signed_hf = float(hf_conf or 0.0)
#     except Exception:
#         signed_hf = 0.0

#     signed_bert = 0.0
#     if bert_label:
#         if bert_label.lower() == "real":
#             signed_bert = float(bert_conf or 0.0)
#         elif bert_label.lower() == "fake":
#             signed_bert = -float(bert_conf or 0.0)

#     fact_score = 1.0 if fact_present else 0.20

#     if reported_fake_count >= 3:
#         user_score = -0.50
#     elif reported_fake_count == 2:
#         user_score = -0.20
#     else:
#         user_score = 0.0

#     # Tunable weights (HF more weight than BERT by default)
#     w_hf = 0.40
#     w_bert = 0.30
#     w_domain = 0.15
#     w_fact = 0.10
#     w_user = 0.05

#     domain_signed = (domain_score * 2.0) - 1.0

#     combined_signed = (
#         (signed_hf * w_hf) +
#         (signed_bert * w_bert) +
#         (domain_signed * w_domain) +
#         (fact_score * w_fact) +
#         (user_score * w_user)
#     )

#     final = max(min((combined_signed + 1.0) / 2.0, 1.0), 0.0)

#     if final >= 0.70:
#         label = "High (Real)"
#     elif final >= 0.40:
#         label = "Medium (Uncertain)"
#     else:
#         label = "Low (Fake)"

#     return round(final, 3), label


# # Domain reputation helper
# TRUSTED_DOMAINS = {
#     "bbc.co.uk": 0.96, "bbc.com": 0.96, "reuters.com": 0.97, "apnews.com": 0.96,
#     "cnn.com": 0.90, "nytimes.com": 0.94, "theguardian.com": 0.92, "bloomberg.com": 0.93
# }
# def domain_reputation_score(url):
#     try:
#         dom = tldextract.extract(url).registered_domain
#         return TRUSTED_DOMAINS.get(dom, 0.40)
#     except Exception:
#         return 0.40


# # -----------------------
# # Fast insert_article (no heavy local BERT by default)
# # -----------------------
# def insert_article(a, schedule_bert: bool = False):
#     """
#     Insert quickly using HF for a fast label. Optionally schedule local BERT in background.
#     """
#     url = a.get("url")
#     if not url:
#         return
#     try:
#         if news.count_documents({"url": url}, limit=1) > 0:
#             return
#     except Exception:
#         pass

#     title = a.get("title") or ""
#     desc = a.get("description") or ""
#     text = f"{title} {desc}"

#     topic = classify_topic(text)
#     try:
#         hf_label, hf_conf = predict_hf(text)
#         hf_conf = float(hf_conf or 0.0)
#     except Exception:
#         hf_label, hf_conf = "Unknown", 0.0

#     summary = summarize_text(a.get("content") or desc)

#     raw_date = a.get("published_at") or a.get("publishedAt") or a.get("pubDate")
#     try:
#         pub_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).isoformat()
#     except Exception:
#         pub_at = datetime.utcnow().isoformat()

#     fc = None
#     if hf_label == "Real":
#         try:
#             fact = fact_check_with_google(title)
#             if fact:
#                 fc = {"link": fact.get("url") if isinstance(fact, dict) else fact.get("link"),
#                       "publisher": fact.get("title") if isinstance(fact, dict) else None,
#                       "snippet": fact.get("snippet") if isinstance(fact, dict) else None}
#         except Exception:
#             fc = None

#     doc = {
#         "title": title,
#         "description": desc,
#         "content": a.get("content"),
#         "url": url,
#         "image_url": a.get("image_url"),
#         "source": a.get("source"),
#         "topic": topic,
#         "prediction": hf_label,
#         "confidence": hf_conf,
#         "summary": summary,
#         "published_at": pub_at,
#         "fact_check": fc,
#         "reported_count": 0,
#         "reported_fake_count": 0,
#         "last_reported_at": None,
#         "user_reports": 0,
#         # BERT metadata
#         "bert_prediction": None,
#         "bert_confidence": None,
#         "bert_pending": bool(schedule_bert)
#     }

#     try:
#         news.insert_one(doc)
#     except Exception as e:
#         print("insert_article: DB insert failed:", e)
#         return

#     if schedule_bert:
#         try:
#             _BG_EXECUTOR.submit(run_bert_for_article, url, title + " " + (a.get("content") or desc))
#         except Exception as e:
#             print("insert_article: failed to schedule bert:", e)


# # -----------------------
# # HTML pages & routes
# # -----------------------
# @app.after_request
# def add_no_cache(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Pragma"] = "no-cache"
#     response.headers["Expires"] = "0"
#     return response

# def create_default_admin():
#     try:
#         admin = users.find_one({"username": "Admin17"})
#         if not admin:
#             users.insert_one({
#                 "username": "Admin17",
#                 "password": generate_password_hash("Divya830@1789"),
#                 "is_admin": True,
#                 "created_at": datetime.utcnow()
#             })
#             print("✔ Default admin created")
#         else:
#             print("✔ Admin already exists")
#     except Exception as e:
#         print("Error creating default admin:", e)

# create_default_admin()

# @app.get("/")
# def home_page():
#     return render_template("index.html", username=session.get("username"), is_admin=session.get("is_admin", False))

# @app.get("/features")
# def features_page():
#     return render_template("features.html")

# @app.get("/login")
# def login_page():
#     if session.get("user_id"):
#         return redirect(url_for("home_page"))
#     return render_template("login.html")

# @app.get("/register")
# def register_page():
#     if session.get("user_id"):
#         return redirect(url_for("dashboard_page"))
#     return render_template("register.html")

# @app.get("/dashboard")
# @login_required
# def dashboard_page():
#     return render_template("dashboard.html", username=session.get("username"))

# @app.get("/admin/dashboard")
# @login_required
# def admin_dashboard_page():
#     if not session.get("is_admin"):
#         return redirect(url_for("dashboard_page"))
#     return render_template("admin.html", username=session.get("username"))


# # Auth endpoints
# @app.post("/register")
# def route_register():
#     data = request.json or {}
#     ok, msg = register_user(data.get("username"), data.get("password"))
#     return (jsonify({"message": "User registered", "user_id": msg}), 201) if ok else (jsonify({"message": msg}), 409)

# @app.post("/login")
# def route_login():
#     data = request.json or {}
#     username = data.get("username")
#     password = data.get("password")

#     ok, user = login_user(username, password)
#     if not ok:
#         return jsonify({"message": user}), 401

#     session["user_id"] = str(user["_id"])
#     session["username"] = user["username"]
#     session["logged_in"] = True
#     session["is_admin"] = user.get("is_admin", False)
#     return jsonify({"redirect": "/"}), 200

# @app.get("/logout")
# @login_required
# def route_logout_get():
#     logout_user()
#     session.clear()
#     return redirect(url_for("home_page"))

# @app.post("/logout")
# @login_required
# def route_logout():
#     logout_user()
#     session.clear()
#     return jsonify({"message": "Logged out"})


# # Preferences
# @app.get("/user/preferences")
# @login_required
# def route_get_prefs():
#     prefs = get_user_preferences(session["user_id"])
#     if not prefs:
#         prefs = {"topics": [], "sources": [], "type": "all", "username": session.get("username", "User")}
#     return jsonify(prefs)

# @app.put("/user/preferences")
# @login_required
# def route_put_prefs():
#     prefs = request.json or {}
#     ok = update_user_preferences(session["user_id"], prefs)
#     return jsonify({"message": "Preferences updated."}), 200

# @app.get("/privacy")
# def privacy_page():
#     return render_template("privacy.html")


# # Helper to extract readable text from a URL
# def extract_text_from_url(url):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     try:
#         art = Article(url)
#         art.download()
#         art.parse()
#         if art.text and len(art.text.strip()) > 50:
#             return art.text
#     except Exception:
#         pass

#     try:
#         r = requests.get(url, headers=headers, timeout=10)
#         from readability import Document
#         doc = Document(r.text)
#         soup = BeautifulSoup(doc.summary(), "html.parser")
#         text = soup.get_text(separator="\n")
#         if len(text.strip()) > 50:
#             return text
#     except Exception:
#         pass

#     try:
#         r = requests.get(url, headers=headers, timeout=10)
#         soup = BeautifulSoup(r.text, "html.parser")
#         p_tags = soup.find_all("p")
#         text = "\n".join([p.get_text() for p in p_tags])
#         if len(text.strip()) > 50:
#             return text
#     except Exception:
#         pass

#     return None


# # News endpoint for regular users (fast)
# @app.get("/news")
# @login_required
# def route_news():
#     prefs = get_user_preferences(session["user_id"]) or {}
#     topics = prefs.get("topics", [])
#     sources_pref = prefs.get("sources", [])
#     view_type = prefs.get("type", "all")

#     try:
#         query = " OR ".join(topics) if topics else "breaking news"
#         fresh_articles = fetch_all_sources(query=query, limit=20)
#         for art in fresh_articles:
#             try:
#                 # Insert quickly in background to keep /news responsive
#                 _BG_EXECUTOR.submit(insert_article, art, False)
#             except Exception:
#                 continue
#     except Exception:
#         pass

#     pipeline = []
#     match = {}
#     if topics:
#         match["topic"] = {"$in": topics}
#     if sources_pref:
#         match["source"] = {"$in": sources_pref}
#     if view_type == "verified":
#         match["prediction"] = "Real"
#     if match:
#         pipeline.append({"$match": match})

#     pipeline += [
#         {"$group": {"_id": "$url", "doc": {"$first": "$$ROOT"}}},
#         {"$replaceRoot": {"newRoot": "$doc"}},
#         {"$addFields": {"_sortDate": {"$cond":[
#             {"$regexMatch":{"input":"$published_at","regex":"^[0-9]{4}-[0-9]{2}-[0-9]{2}" }},
#             {"$toDate":"$published_at"},
#             {"$toDate":{"$toString":"$_id"}}
#         ]}}}, 
#         {"$sort": {"_sortDate": -1}},
#         {"$project":{"_sortDate":0}},
#         {"$limit": 50}
#     ]

#     saved_news = list(news.aggregate(pipeline))
#     final = []
#     for a in saved_news:
#         rpt_count = reports.count_documents({"url": a.get("url")})
#         rpt_fake = reports.count_documents({"url": a.get("url"), "label":"Fake"})
#         user_reported = False
#         try:
#             uid = ObjectId(session["user_id"])
#             user_reported = reports.find_one({"url": a.get("url"), "user_id": uid}) is not None
#         except Exception:
#             user_reported = False

#         text_for_pred = (a.get("title","") + " " + (a.get("description") or ""))
#         hf_label, hf_conf = predict_hf(text_for_pred)
#         hf_conf = float(hf_conf or 0.0)

#         domain_score = domain_reputation_score(a.get("url") or "")
#         fact_present = True if a.get("fact_check") else False
#         cred_score, cred_label = compute_credibility(hf_conf, domain_score, fact_present, rpt_fake,
#                                                     bert_label=a.get("bert_prediction"), bert_conf=a.get("bert_confidence") or 0.0)

#         if view_type == "verified" and hf_label != "Real":
#             continue

#         final.append({
#             "title": a.get("title",""),
#             "description": a.get("description",""),
#             "summary": a.get("summary",""),
#             "content": a.get("content",""),
#             "url": a.get("url", "#"),
#             "image_url": a.get("image_url"),
#             "source": a.get("source", "Unknown"),
#             "topic": a.get("topic", "General"),
#             "prediction": hf_label,
#             "confidence": hf_conf,
#             "published_at": a.get("published_at"),
#             "fact_check": a.get("fact_check"),
#             "reported_count": rpt_count,
#             "reported_fake_count": rpt_fake,
#             "user_reported": user_reported,
#             "credibility_score": cred_score,
#             "credibility_label": cred_label
#         })
#     return jsonify(final)


# # Admin news: HF vs BERT comparison
# @app.get("/admin/news")
# @login_required
# def route_admin_news():
#     if not session.get("is_admin"):
#         return jsonify([]), 403

#     prefs = get_user_preferences(session["user_id"]) or {}
#     topics = prefs.get("topics", [])
#     sources_pref = prefs.get("sources", [])
#     view_type = prefs.get("type", "all")

#     pipeline = []
#     match = {}
#     if topics:
#         match["topic"] = {"$in": topics}
#     if sources_pref:
#         match["source"] = {"$in": sources_pref}
#     if view_type == "verified":
#         match["prediction"] = "Real"
#     if match:
#         pipeline.append({"$match": match})

#     pipeline += [
#         {"$group": {"_id": "$url", "doc": {"$first": "$$ROOT"}}},
#         {"$replaceRoot": {"newRoot": "$doc"}},
#         {"$addFields": {"_sortDate": {"$cond":[
#             {"$regexMatch":{"input":"$published_at","regex":"^[0-9]{4}-[0-9]{2}-[0-9]{2}" }},
#             {"$toDate":"$published_at"},
#             {"$toDate":{"$toString":"$_id"}}
#         ]}}}, 
#         {"$sort": {"_sortDate": -1}},
#         {"$project":{"_sortDate":0}},
#         {"$limit": 100}
#     ]

#     saved_news = list(news.aggregate(pipeline))

#     # Find missing BERT results and schedule runs
#     missing = []
#     for a in saved_news:
#         if not a.get("bert_prediction") and not a.get("bert_pending"):
#             missing.append(a.get("url"))

#     # Run BERT synchronously for a small number so admin sees comparisons immediately
#     for url in missing[:SYNC_BERT_FOR_ADMIN]:
#         doc = news.find_one({"url": url})
#         if not doc:
#             continue
#         text = (doc.get("title","") or "") + " " + (doc.get("content") or doc.get("description","") or "")
#         try:
#             news.update_one({"url": url}, {"$set": {"bert_pending": True}})
#         except Exception:
#             pass
#         try:
#             run_bert_for_article(url, text)
#         except Exception as e:
#             print("admin sync run_bert_for_article failed:", e)

#     # Schedule background BERT for the rest (non-blocking)
#     for url in missing[SYNC_BERT_FOR_ADMIN:SYNC_BERT_FOR_ADMIN + 50]:
#         doc = news.find_one({"url": url})
#         if not doc:
#             continue
#         text = (doc.get("title","") or "") + " " + (doc.get("content") or doc.get("description","") or "")
#         try:
#             news.update_one({"url": url}, {"$set": {"bert_pending": True}})
#             _BG_EXECUTOR.submit(run_bert_for_article, url, text)
#         except Exception as e:
#             print("admin schedule run_bert_for_article failed:", e)

#     final = []
#     for a in saved_news:
#         rpt_count = reports.count_documents({"url": a.get("url")})
#         rpt_fake = reports.count_documents({"url": a.get("url"), "label":"Fake"})

#         text_for_pred = (a.get("title","") + " " + (a.get("description") or ""))
#         hf_label, hf_conf = predict_hf(text_for_pred)
#         hf_conf = float(hf_conf or 0.0)

#         bert_label = a.get("bert_prediction") or ("Pending" if a.get("bert_pending") else "Unknown")
#         bert_conf = float(a.get("bert_confidence") or 0.0)
#         bert_status = "pending" if a.get("bert_pending") else ("done" if a.get("bert_prediction") else "none")

#         domain_score = domain_reputation_score(a.get("url") or "")
#         fact_present = True if a.get("fact_check") else False
#         cred_score, cred_label = compute_credibility(hf_conf, domain_score, fact_present, rpt_fake,
#                                                      bert_label=None if bert_label in ("Pending","Unknown") else bert_label,
#                                                      bert_conf=bert_conf)

#         final.append({
#             "title": a.get("title",""),
#             "description": a.get("description",""),
#             "summary": a.get("summary",""),
#             "content": a.get("content",""),
#             "url": a.get("url", "#"),
#             "image_url": a.get("image_url"),
#             "source": a.get("source", "Unknown"),
#             "topic": a.get("topic", "General"),
#             "prediction_hf": hf_label,
#             "confidence_hf": hf_conf,
#             "prediction_bert": bert_label,
#             "confidence_bert": bert_conf,
#             "bert_status": bert_status,
#             "published_at": a.get("published_at"),
#             "fact_check": a.get("fact_check"),
#             "reported_count": rpt_count,
#             "reported_fake_count": rpt_fake,
#             "credibility_score": cred_score,
#             "credibility_label": cred_label
#         })
#     return jsonify(final)


# # Admin endpoint to force-run BERT for a given URL
# @app.post("/admin/run-bert")
# @login_required
# def admin_run_bert():
#     if not session.get("is_admin"):
#         return jsonify({"message":"forbidden"}), 403
#     data = request.json or {}
#     url = data.get("url")
#     if not url:
#         return jsonify({"message":"missing url"}), 400
#     doc = news.find_one({"url": url})
#     if not doc:
#         return jsonify({"message":"not found"}), 404
#     text = (doc.get("title","") or "") + " " + (doc.get("content") or doc.get("description","") or "")
#     try:
#         news.update_one({"url": url}, {"$set": {"bert_pending": True}})
#         _BG_EXECUTOR.submit(run_bert_for_article, url, text)
#         return jsonify({"message":"BERT scheduled for url"}), 202
#     except Exception as e:
#         print("admin/run-bert failed:", e)
#         return jsonify({"message":"error scheduling"}), 500


# # check_url endpoint (admin gets HF & BERT)
# @app.post("/check_url")
# @login_required
# def check_url():
#     data = request.json or {}
#     url = data.get("url")
#     if not url:
#         return jsonify({"message":"URL missing"}), 400

#     text = extract_text_from_url(url)
#     if not text or len(text.strip()) < 30:
#         return jsonify({"message":"Could not extract content from URL"}), 400

#     hf_label, hf_conf = predict_hf(text)
#     hf_conf = float(hf_conf or 0.0)

#     if session.get("is_admin"):
#         try:
#             bert_label, bert_conf = predict_auth_compat(text)
#         except Exception:
#             bert_label, bert_conf = "Unknown", 0.0

#         dom_score = domain_reputation_score(url)
#         fact_present = False
#         try:
#             fc = fact_check_with_google(text.split("\n",1)[0][:200])
#             fact_present = True if fc else False
#         except Exception:
#             fact_present = False

#         cred_score, cred_label = compute_credibility(hf_conf, dom_score, fact_present, reports.count_documents({"url":url,"label":"Fake"}),
#                                                     bert_label=None if bert_label == "Unknown" else bert_label,
#                                                     bert_conf=float(bert_conf or 0.0))

#         return jsonify({
#             "url": url,
#             "prediction_hf": hf_label,
#             "hf_confidence": hf_conf,
#             "prediction_bert": bert_label,
#             "bert_confidence": float(bert_conf or 0.0),
#             "credibility_score": cred_score,
#             "credibility_label": cred_label
#         })
#     else:
#         dom_score = domain_reputation_score(url)
#         cred_score, cred_label = compute_credibility(hf_conf, dom_score, False, reports.count_documents({"url":url,"label":"Fake"}))
#         return jsonify({
#             "url": url,
#             "prediction": hf_label,
#             "confidence": hf_conf,
#             "credibility_score": cred_score,
#             "credibility_label": cred_label
#         })


# # Save/report endpoints (unchanged behavior)
# @app.post("/save_article")
# @login_required
# def save_article_api():
#     data = request.get_json() or {}
#     url = data.get("url")
#     if not url:
#         return jsonify({"message": "Missing URL"}), 400
#     try:
#         uid = ObjectId(session["user_id"])
#     except Exception:
#         return jsonify({"message": "Invalid user"}), 400
#     existing = saved_articles.find_one({"user_id": uid, "url": url})
#     if existing:
#         return jsonify({"message": "Already saved"}), 200
#     doc = {
#         "user_id": uid,
#         "username": session.get("username"),
#         "url": url,
#         "title": data.get("title"),
#         "source": data.get("source"),
#         "published_at": data.get("published_at"),
#         "prediction": data.get("prediction"),
#         "confidence": data.get("confidence"),
#         "saved_at": datetime.utcnow(),
#     }
#     try:
#         saved_articles.insert_one(doc)
#         return jsonify({"message": "Article saved to your profile"}), 201
#     except Exception as e:
#         print("Error saving article:", e)
#         return jsonify({"message": "Error saving article"}), 500

# @app.post("/report")
# @login_required
# def report_article():
#     data = request.json or {}
#     url = data.get("url")
#     label = data.get("label")
#     reason = data.get("reason", "")
#     if not url or label not in ("Fake","Real"):
#         return jsonify({"message":"Invalid payload"}), 400
#     try:
#         uid = ObjectId(session["user_id"])
#     except Exception:
#         return jsonify({"message":"Invalid user"}), 400
#     existing = reports.find_one({"url": url, "user_id": uid})
#     if existing:
#         return jsonify({"message":"You already reported this article."}), 409
#     rep = {
#         "url": url,
#         "label": label,
#         "reason": reason,
#         "user_id": uid,
#         "username": session.get("username"),
#         "timestamp": datetime.utcnow()
#     }
#     reports.insert_one(rep)
#     news.update_one({"url": url}, {"$inc":{"reported_count":1,"reported_fake_count": (1 if label=="Fake" else 0)}, "$set":{"last_reported_at": datetime.utcnow()}}, upsert=False)
#     return jsonify({"message":"Report saved."}), 201

# @app.get("/user/reports")
# @login_required
# def get_user_reports():
#     try:
#         uid = ObjectId(session["user_id"])
#     except Exception:
#         return jsonify([])
#     docs = list(reports.find({"user_id": uid}).sort("timestamp",-1).limit(50))
#     out = []
#     for r in docs:
#         out.append({
#             "url": r.get("url"),
#             "label": r.get("label"),
#             "reason": r.get("reason"),
#             "timestamp": r.get("timestamp").isoformat() if r.get("timestamp") else None,
#             "username": r.get("username")
#         })
#     return jsonify(out)

# @app.get("/user/saved")
# @login_required
# def get_user_saved_articles():
#     try:
#         uid = ObjectId(session["user_id"])
#     except Exception:
#         return jsonify([])
#     docs = list(saved_articles.find({"user_id": uid}).sort("saved_at", -1))
#     out = []
#     for d in docs:
#         out.append({
#             "url": d.get("url"),
#             "title": d.get("title"),
#             "source": d.get("source"),
#             "published_at": d.get("published_at"),
#             "image_url": d.get("image_url"),
#         })
#     return jsonify(out)

# @app.get("/insert-news")
# @login_required
# def insert_news_to_db():
#     if not session.get("is_admin"):
#         return jsonify({"message":"forbidden"}), 403
#     articles = fetch_all_sources(query="latest news", limit=30)
#     inserted = 0
#     for a in articles:
#         try:
#             insert_article(a, schedule_bert=False)
#             inserted += 1
#         except Exception:
#             continue
#     return jsonify({"inserted": inserted})

# @app.get("/profile")
# @login_required
# def profile_page():
#     try:
#         uid = ObjectId(session["user_id"])
#     except Exception:
#         uid = None
#     saved = []
#     if uid:
#         saved = list(saved_articles.find({"user_id": uid}).sort("saved_at", -1))
#     return render_template("profile.html", username=session.get("username"), saved_articles=saved)

# @app.get("/terms")
# def terms_page():
#     return render_template("terms.html")


# # Run app
# if __name__ == "__main__":
#     app.run(debug=Config.DEBUG, port=int(os.environ.get("PORT", 5000)))













# app.py (corrected & compatible with your original structure)
import os
import json
import nltk
nltk.download('punkt', quiet=True)

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from bson.objectid import ObjectId
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import tldextract
from werkzeug.security import generate_password_hash

from concurrent.futures import ThreadPoolExecutor
import threading

from config import Config
from db import users, user_preferences, news, reports, saved_articles
from auth import register_user, login_user, logout_user, get_user_preferences, update_user_preferences, login_required

# IMPORTANT: use functions that actually exist in your model_utils.py
from model_utils import (
    classify_topic,
    predict_authenticity,
    summarize_text,
    fact_check_with_google,
    predict_hf,
    init_hf_model,
    load_bert_model,
    load_summarizer
)
from multi_news_api import fetch_all_sources

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# CORS
CORS(app, supports_credentials=True)
app.config["CORS_HEADERS"] = "Content-Type"

# Background execution + lock
_BG_EXECUTOR = ThreadPoolExecutor(max_workers=3)  # tune to your machine
_db_lock = threading.Lock()
SYNC_BERT_FOR_ADMIN = 2  # small number to run synchronously for admin (adjust as needed)

# Preload models (best effort)
try:
    init_hf_model()
except Exception as e:
    print("init_hf_model() failed:", e)

try:
    load_bert_model()
except Exception as e:
    print("load_bert_model() failed:", e)

try:
    load_summarizer()
except Exception as e:
    print("load_summarizer() failed:", e)

print("Model warm-up attempted at startup.")


# -----------------------
# Helpers
# -----------------------
def predict_auth_compat(text: str):
    """
    Normalize predict_authenticity -> (label_str, conf_float)
    Handles older (int_label, conf) or (str_label, conf).
    """
    try:
        res = predict_authenticity(text)
        if isinstance(res, tuple) and len(res) == 2:
            lab, conf = res
            if isinstance(lab, int):
                return ("Real" if lab == 1 else "Fake"), float(conf or 0.0)
            if isinstance(lab, str):
                lu = lab.strip().lower()
                if lu in ("real", "true", "1"):
                    return "Real", float(conf or 0.0)
                if lu in ("fake", "false", "0"):
                    return "Fake", float(conf or 0.0)
                return lab, float(conf or 0.0)
        return "Unknown", 0.0
    except Exception as e:
        print("predict_auth_compat error:", e)
        return "Unknown", 0.0


def run_bert_for_article(url: str, text: str):
    """
    Run local BERT and update DB document.
    Can be called synchronously (admin) or scheduled in background.
    """
    try:
        lab, conf = predict_auth_compat(text)
    except Exception as e:
        print("run_bert_for_article: predict_auth_compat failed:", e)
        lab, conf = "Unknown", 0.0

    try:
        with _db_lock:
            news.update_one(
                {"url": url},
                {"$set": {
                    "bert_prediction": lab,
                    "bert_confidence": float(conf),
                    "bert_pending": False,
                    "bert_computed_at": datetime.utcnow().isoformat()
                }}
            )
    except Exception as e:
        print("run_bert_for_article: DB update failed for", url, e)


# domain reputation
TRUSTED_DOMAINS = {
    "bbc.co.uk": 0.96, "bbc.com": 0.96, "reuters.com": 0.97, "apnews.com": 0.96,
    "cnn.com": 0.90, "nytimes.com": 0.94, "theguardian.com": 0.92, "bloomberg.com": 0.93
}
def domain_reputation_score(url):
    try:
        dom = tldextract.extract(url).registered_domain
        return TRUSTED_DOMAINS.get(dom, 0.40)
    except Exception:
        return 0.40


def compute_credibility(hf_conf, domain_score, fact_present, reported_fake_count, bert_label=None, bert_conf=0.0):
    """
    Combine HF + BERT + domain + fact-check + reports into a single credibility score.
    """
    try:
        signed_hf = float(hf_conf or 0.0)
    except Exception:
        signed_hf = 0.0

    signed_bert = 0.0
    if bert_label:
        if isinstance(bert_label, str) and bert_label.lower() == "real":
            signed_bert = float(bert_conf or 0.0)
        elif isinstance(bert_label, str) and bert_label.lower() == "fake":
            signed_bert = -float(bert_conf or 0.0)

    fact_score = 1.0 if fact_present else 0.20

    if reported_fake_count >= 3:
        user_score = -0.50
    elif reported_fake_count == 2:
        user_score = -0.20
    else:
        user_score = 0.0

    # Weights (tweak as needed)
    w_hf = 0.40
    w_bert = 0.30
    w_domain = 0.15
    w_fact = 0.10
    w_user = 0.05

    domain_signed = (domain_score * 2.0) - 1.0

    combined_signed = (
        (signed_hf * w_hf) +
        (signed_bert * w_bert) +
        (domain_signed * w_domain) +
        (fact_score * w_fact) +
        (user_score * w_user)
    )

    final = max(min((combined_signed + 1.0) / 2.0, 1.0), 0.0)
    if final >= 0.70:
        label = "High (Real)"
    elif final >= 0.40:
        label = "Medium (Uncertain)"
    else:
        label = "Low (Fake)"
    return round(final, 3), label


# -----------------------
# insert_article (fast)
# -----------------------
def insert_article(a, schedule_bert: bool = False):
    """
    Insert article quickly. By default we use HF for fast label and do not run local BERT.
    If schedule_bert True, the BERT run is scheduled in background.
    """
    url = a.get("url")
    if not url:
        return
    try:
        if news.count_documents({"url": url}, limit=1) > 0:
            return
    except Exception:
        pass

    title = a.get("title","") or ""
    desc = a.get("description","") or ""
    text = f"{title} {desc}"

    topic = classify_topic(text)
    try:
        hf_label, hf_conf = predict_hf(text)
        hf_conf = float(hf_conf or 0.0)
    except Exception:
        hf_label, hf_conf = "Unknown", 0.0

    summary = summarize_text(a.get("content") or desc)

    raw_date = a.get("published_at") or a.get("publishedAt") or a.get("pubDate")
    try:
        pub_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).isoformat()
    except Exception:
        pub_at = datetime.utcnow().isoformat()

    fc = None
    if hf_label == "Real":
        try:
            fact = fact_check_with_google(title)
            if fact:
                fc = {"link": fact.get("url") if isinstance(fact, dict) else fact.get("link"),
                      "publisher": fact.get("title") if isinstance(fact, dict) else None,
                      "snippet": fact.get("snippet") if isinstance(fact, dict) else None}
        except Exception:
            fc = None

    doc = {
        "title": title,
        "description": desc,
        "content": a.get("content"),
        "url": url,
        "image_url": a.get("image_url"),
        "source": a.get("source"),
        "topic": topic,
        "prediction": hf_label,
        "confidence": hf_conf,
        "summary": summary,
        "published_at": pub_at,
        "fact_check": fc,
        "reported_count": 0,
        "reported_fake_count": 0,
        "last_reported_at": None,
        "user_reports": 0,
        "bert_prediction": None,
        "bert_confidence": None,
        "bert_pending": bool(schedule_bert)
    }

    try:
        news.insert_one(doc)
    except Exception as e:
        print("insert_article: DB insert failed:", e)
        return

    if schedule_bert:
        try:
            _BG_EXECUTOR.submit(run_bert_for_article, url, title + " " + (a.get("content") or desc))
        except Exception as e:
            print("insert_article: failed to schedule BERT:", e)


# -----------------------
# URL text extraction (unchanged)
# -----------------------
def extract_text_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        art = Article(url)
        art.download()
        art.parse()
        if art.text and len(art.text.strip()) > 50:
            return art.text
    except Exception:
        pass

    try:
        r = requests.get(url, headers=headers, timeout=10)
        from readability import Document
        doc = Document(r.text)
        soup = BeautifulSoup(doc.summary(), "html.parser")
        text = soup.get_text(separator="\n")
        if len(text.strip()) > 50:
            return text
    except Exception:
        pass

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        p_tags = soup.find_all("p")
        text = "\n".join([p.get_text() for p in p_tags])
        if len(text.strip()) > 50:
            return text
    except Exception:
        pass

    return None


# -----------------------
# Flask routes (kept same URLs)
# -----------------------
@app.after_request
def add_no_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def create_default_admin():
    try:
        admin = users.find_one({"username": "Admin17"})
        if not admin:
            users.insert_one({
                "username": "Admin17",
                "password": generate_password_hash("Divya830@1789"),
                "is_admin": True,
                "created_at": datetime.utcnow()
            })
            print("✔ Default admin created")
        else:
            print("✔ Admin already exists")
    except Exception as e:
        print("Error creating default admin:", e)

create_default_admin()


@app.get("/")
def home_page():
    return render_template("index.html", username=session.get("username"), is_admin=session.get("is_admin", False))


@app.get("/features")
def features_page():
    return render_template("features.html")


@app.get("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("home_page"))
    return render_template("login.html")


@app.get("/register")
def register_page():
    if session.get("user_id"):
        return redirect(url_for("dashboard_page"))
    return render_template("register.html")


@app.get("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html", username=session.get("username"))


@app.get("/admin/dashboard")
@login_required
def admin_dashboard_page():
    if not session.get("is_admin"):
        return redirect(url_for("dashboard_page"))
    return render_template("admin.html", username=session.get("username"))


@app.get("/about")
def about_page():
    return render_template("about.html")


@app.get("/contact")
def contact_page():
    return render_template("contact.html")


# Auth routes
@app.post("/register")
def route_register():
    data = request.json or {}
    ok, msg = register_user(data.get("username"), data.get("password"))
    return (jsonify({"message": "User registered", "user_id": msg}), 201) if ok else (jsonify({"message": msg}), 409)


@app.post("/login")
def route_login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    ok, user = login_user(username, password)
    if not ok:
        return jsonify({"message": user}), 401

    # set session once and return to HOME as requested earlier
    session["user_id"] = str(user["_id"])
    session["username"] = user["username"]
    session["logged_in"] = True
    session["is_admin"] = user.get("is_admin", False)

    # for both admin and normal user, redirect to home as you intended
    return jsonify({"redirect": "/"}), 200


@app.get("/logout")
@login_required
def route_logout_get():
    logout_user()
    session.clear()
    return redirect(url_for("home_page"))


@app.post("/logout")
@login_required
def route_logout():
    logout_user()
    session.clear()
    return jsonify({"message": "Logged out"})


# Preferences
@app.get("/user/preferences")
@login_required
def route_get_prefs():
    prefs = get_user_preferences(session["user_id"])
    if not prefs:
        prefs = {"topics": [], "sources": [], "type": "all", "username": session.get("username", "User")}
    return jsonify(prefs)


@app.put("/user/preferences")
@login_required
def route_put_prefs():
    prefs = request.json or {}
    ok = update_user_preferences(session["user_id"], prefs)
    return jsonify({"message": "Preferences updated."}), 200


@app.get("/privacy")
def privacy_page():
    return render_template("privacy.html")


# News endpoint for users (fast)
@app.get("/news")
@login_required
def route_news():
    prefs = get_user_preferences(session["user_id"]) or {}
    topics = prefs.get("topics", [])
    sources_pref = prefs.get("sources", [])
    view_type = prefs.get("type", "all")

    try:
        query = " OR ".join(topics) if topics else "breaking news"
        fresh_articles = fetch_all_sources(query=query, limit=20)
        for art in fresh_articles:
            try:
                # insert in background to keep /news responsive
                _BG_EXECUTOR.submit(insert_article, art, False)
            except Exception:
                continue
    except Exception:
        pass

    pipeline = []
    match = {}
    if topics:
        match["topic"] = {"$in": topics}
    if sources_pref:
        match["source"] = {"$in": sources_pref}
    if view_type == "verified":
        match["prediction"] = "Real"
    if match:
        pipeline.append({"$match": match})

    pipeline += [
        {"$group": {"_id": "$url", "doc": {"$first": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": "$doc"}},
        {"$addFields": {"_sortDate": {"$cond":[
            {"$regexMatch":{"input":"$published_at","regex":"^[0-9]{4}-[0-9]{2}-[0-9]{2}" }},
            {"$toDate":"$published_at"},
            {"$toDate":{"$toString":"$_id"}}
        ]}}}, 
        {"$sort": {"_sortDate": -1}},
        {"$project":{"_sortDate":0}},
        {"$limit": 50}
    ]

    saved_news = list(news.aggregate(pipeline))
    final = []
    for a in saved_news:
        rpt_count = reports.count_documents({"url": a.get("url")})
        rpt_fake = reports.count_documents({"url": a.get("url"), "label":"Fake"})
        user_reported = False
        try:
            uid = ObjectId(session["user_id"])
            user_reported = reports.find_one({"url": a.get("url"), "user_id": uid}) is not None
        except Exception:
            user_reported = False

        text_for_pred = (a.get("title","") + " " + (a.get("description") or ""))
        hf_label, hf_conf = predict_hf(text_for_pred)
        hf_conf = float(hf_conf or 0.0)

        domain_score = domain_reputation_score(a.get("url") or "")
        fact_present = True if a.get("fact_check") else False
        cred_score, cred_label = compute_credibility(hf_conf, domain_score, fact_present, rpt_fake,
                                                    bert_label=a.get("bert_prediction"), bert_conf=a.get("bert_confidence") or 0.0)

        if view_type == "verified" and hf_label != "Real":
            continue

        final.append({
            "title": a.get("title",""),
            "description": a.get("description",""),
            "summary": a.get("summary",""),
            "content": a.get("content",""),
            "url": a.get("url", "#"),
            "image_url": a.get("image_url"),
            "source": a.get("source", "Unknown"),
            "topic": a.get("topic", "General"),
            "prediction": hf_label,
            "confidence": hf_conf,
            "published_at": a.get("published_at"),
            "fact_check": a.get("fact_check"),
            "reported_count": rpt_count,
            "reported_fake_count": rpt_fake,
            "user_reported": user_reported,
            "credibility_score": cred_score,
            "credibility_label": cred_label
        })
    return jsonify(final)


# Admin news: HF vs BERT comparative output
@app.get("/admin/news")
@login_required
def route_admin_news():
    if not session.get("is_admin"):
        return jsonify([]), 403

    prefs = get_user_preferences(session["user_id"]) or {}
    topics = prefs.get("topics", [])
    sources_pref = prefs.get("sources", [])
    view_type = prefs.get("type", "all")

    pipeline = []
    match = {}
    if topics:
        match["topic"] = {"$in": topics}
    if sources_pref:
        match["source"] = {"$in": sources_pref}
    if view_type == "verified":
        match["prediction"] = "Real"
    if match:
        pipeline.append({"$match": match})

    pipeline += [
        {"$group": {"_id": "$url", "doc": {"$first": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": "$doc"}},
        {"$addFields": {"_sortDate": {"$cond":[
            {"$regexMatch":{"input":"$published_at","regex":"^[0-9]{4}-[0-9]{2}-[0-9]{2}" }},
            {"$toDate":"$published_at"},
            {"$toDate":{"$toString":"$_id"}}
        ]}}}, 
        {"$sort": {"_sortDate": -1}},
        {"$project":{"_sortDate":0}},
        {"$limit": 100}
    ]

    saved_news = list(news.aggregate(pipeline))

    # find missing bert results (and not pending)
    missing = []
    for a in saved_news:
        if not a.get("bert_prediction") and not a.get("bert_pending"):
            missing.append(a.get("url"))

    # Run BERT synchronously for a small number so admin sees immediate comparisons
    for url in missing[:SYNC_BERT_FOR_ADMIN]:
        doc = news.find_one({"url": url})
        if not doc:
            continue
        text = (doc.get("title","") or "") + " " + (doc.get("content") or doc.get("description","") or "")
        try:
            news.update_one({"url": url}, {"$set": {"bert_pending": True}})
        except Exception:
            pass
        try:
            run_bert_for_article(url, text)
        except Exception as e:
            print("admin sync run_bert_for_article failed for", url, e)

    # schedule background BERT for the rest (non-blocking)
    for url in missing[SYNC_BERT_FOR_ADMIN:SYNC_BERT_FOR_ADMIN + 50]:
        doc = news.find_one({"url": url})
        if not doc:
            continue
        text = (doc.get("title","") or "") + " " + (doc.get("content") or doc.get("description","") or "")
        try:
            news.update_one({"url": url}, {"$set": {"bert_pending": True}})
            _BG_EXECUTOR.submit(run_bert_for_article, url, text)
        except Exception as e:
            print("admin schedule run_bert_for_article failed for", url, e)

    final = []
    for a in saved_news:
        rpt_count = reports.count_documents({"url": a.get("url")})
        rpt_fake = reports.count_documents({"url": a.get("url"), "label":"Fake"})

        text_for_pred = (a.get("title","") + " " + (a.get("description") or ""))
        hf_label, hf_conf = predict_hf(text_for_pred)
        hf_conf = float(hf_conf or 0.0)

        bert_label = a.get("bert_prediction") or ("Pending" if a.get("bert_pending") else "Unknown")
        bert_conf = float(a.get("bert_confidence") or 0.0)
        bert_status = "pending" if a.get("bert_pending") else ("done" if a.get("bert_prediction") else "none")

        domain_score = domain_reputation_score(a.get("url") or "")
        fact_present = True if a.get("fact_check") else False
        cred_score, cred_label = compute_credibility(hf_conf, domain_score, fact_present, rpt_fake,
                                                    bert_label=None if bert_label in ("Pending","Unknown") else bert_label,
                                                    bert_conf=bert_conf)

        final.append({
            "title": a.get("title",""),
            "description": a.get("description",""),
            "summary": a.get("summary",""),
            "content": a.get("content",""),
            "url": a.get("url", "#"),
            "image_url": a.get("image_url"),
            "source": a.get("source", "Unknown"),
            "topic": a.get("topic", "General"),
            "prediction_hf": hf_label,
            "confidence_hf": hf_conf,
            "prediction_bert": bert_label,
            "confidence_bert": bert_conf,
            "bert_status": bert_status,
            "published_at": a.get("published_at"),
            "fact_check": a.get("fact_check"),
            "reported_count": rpt_count,
            "reported_fake_count": rpt_fake,
            "credibility_score": cred_score,
            "credibility_label": cred_label
        })
    return jsonify(final)


# check_url endpoint (admin gets HF + BERT)
@app.post("/check_url")
@login_required
def check_url():
    data = request.json or {}
    url = data.get("url")
    if not url:
        return jsonify({"message":"URL missing"}), 400

    text = extract_text_from_url(url)
    if not text or len(text.strip()) < 30:
        return jsonify({"message":"Could not extract content from URL"}), 400

    hf_label, hf_conf = predict_hf(text)
    hf_conf = float(hf_conf or 0.0)

    if session.get("is_admin"):
        try:
            bert_label, bert_conf = predict_auth_compat(text)
        except Exception:
            bert_label, bert_conf = "Unknown", 0.0

        dom_score = domain_reputation_score(url)
        fact_present = False
        try:
            fc = fact_check_with_google(text.split("\n",1)[0][:200])
            fact_present = True if fc else False
        except Exception:
            fact_present = False

        cred_score, cred_label = compute_credibility(hf_conf, dom_score, fact_present, reports.count_documents({"url":url,"label":"Fake"}),
                                                    bert_label=None if bert_label == "Unknown" else bert_label,
                                                    bert_conf=float(bert_conf or 0.0))
        return jsonify({
            "url": url,
            "prediction_hf": hf_label,
            "hf_confidence": hf_conf,
            "prediction_bert": bert_label,
            "bert_confidence": float(bert_conf or 0.0),
            "credibility_score": cred_score,
            "credibility_label": cred_label
        })
    else:
        dom_score = domain_reputation_score(url)
        cred_score, cred_label = compute_credibility(hf_conf, dom_score, False, reports.count_documents({"url":url,"label":"Fake"}))
        return jsonify({
            "url": url,
            "prediction": hf_label,
            "confidence": hf_conf,
            "credibility_score": cred_score,
            "credibility_label": cred_label
        })


# Save/report endpoints
@app.post("/save_article")
@login_required
def save_article_api():
    data = request.get_json() or {}
    url = data.get("url")

    if not url:
        return jsonify({"message": "Missing URL"}), 400

    try:
        uid = ObjectId(session["user_id"])
    except Exception:
        return jsonify({"message": "Invalid user"}), 400

    existing = saved_articles.find_one({"user_id": uid, "url": url})
    if existing:
        return jsonify({"message": "Already saved"}), 200

    doc = {
        "user_id": uid,
        "username": session.get("username"),
        "url": url,
        "title": data.get("title"),
        "source": data.get("source"),
        "published_at": data.get("published_at"),
        "prediction": data.get("prediction"),
        "confidence": data.get("confidence"),
        "saved_at": datetime.utcnow(),
    }

    try:
        saved_articles.insert_one(doc)
        return jsonify({"message": "Article saved to your profile"}), 201
    except Exception as e:
        print("Error saving article:", e)
        return jsonify({"message": "Error saving article"}), 500


@app.post("/report")
@login_required
def report_article():
    data = request.json or {}
    url = data.get("url")
    label = data.get("label")
    reason = data.get("reason", "")
    if not url or label not in ("Fake","Real"):
        return jsonify({"message":"Invalid payload"}), 400

    try:
        uid = ObjectId(session["user_id"])
    except Exception:
        return jsonify({"message":"Invalid user"}), 400

    existing = reports.find_one({"url": url, "user_id": uid})
    if existing:
        return jsonify({"message":"You already reported this article."}), 409

    rep = {
        "url": url,
        "label": label,
        "reason": reason,
        "user_id": uid,
        "username": session.get("username"),
        "timestamp": datetime.utcnow()
    }
    reports.insert_one(rep)
    news.update_one({"url": url}, {"$inc":{"reported_count":1,"reported_fake_count": (1 if label=="Fake" else 0)}, "$set":{"last_reported_at": datetime.utcnow()}}, upsert=False)
    return jsonify({"message":"Report saved."}), 201


@app.get("/user/reports")
@login_required
def get_user_reports():
    try:
        uid = ObjectId(session["user_id"])
    except Exception:
        return jsonify([])
    docs = list(reports.find({"user_id": uid}).sort("timestamp",-1).limit(50))
    out = []
    for r in docs:
        out.append({
            "url": r.get("url"),
            "label": r.get("label"),
            "reason": r.get("reason"),
            "timestamp": r.get("timestamp").isoformat() if r.get("timestamp") else None,
            "username": r.get("username")
        })
    return jsonify(out)


@app.get("/user/saved")
@login_required
def get_user_saved_articles():
    try:
        uid = ObjectId(session["user_id"])
    except Exception:
        return jsonify([])

    docs = list(saved_articles.find({"user_id": uid}).sort("saved_at", -1))
    out = []
    for d in docs:
        out.append({
            "url": d.get("url"),
            "title": d.get("title"),
            "source": d.get("source"),
            "published_at": d.get("published_at"),
            "image_url": d.get("image_url"),
        })
    return jsonify(out)


@app.get("/insert-news")
@login_required
def insert_news_to_db():
    if not session.get("is_admin"):
        return jsonify({"message":"forbidden"}), 403
    articles = fetch_all_sources(query="latest news", limit=30)
    inserted = 0
    for a in articles:
        try:
            # fast insert; don't schedule BERT for all to save resources
            insert_article(a, schedule_bert=False)
            inserted += 1
        except Exception:
            continue
    return jsonify({"inserted": inserted})


@app.get("/profile")
@login_required
def profile_page():
    try:
        uid = ObjectId(session["user_id"])
    except Exception:
        uid = None

    saved = []
    if uid:
        saved = list(saved_articles.find({"user_id": uid}).sort("saved_at", -1))

    return render_template("profile.html", username=session.get("username"), saved_articles=saved)


@app.get("/terms")
def terms_page():
    return render_template("terms.html")


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=int(os.environ.get("PORT", 5000)))
