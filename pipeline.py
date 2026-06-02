"""
╔═════════════════════════════════════════════════════════════════════════════╗
║  DS 401 – Introduction to Data Science | BSDS 02 Spring 2026                ║
║                                                                             ║
║  pipeline.py  –  Fully Unified End-to-End Reproducible Pipeline             ║
║                                                                             ║
║  Cities     : Lahore (Feb 6–8, 2026) | Rawalpindi (Feb 13–15, 2026)         ║
║  Modalities : News · Social · Weather · Incidents · Images · Videos         ║
║                                                                             ║
║  PIPELINE STAGES                                                            ║
║  ─────────────────────────────────────────────────────────────────          ║
║  STAGE 0 │ Setup       – paths, directories, global config                  ║
║  STAGE 1 │ Collect/Log – load raw files, log source manifest                ║
║  STAGE 2 │ Clean       – normalise, deduplicate, QC checks (21 checks)      ║
║  STAGE 3 │ Features    – sentiment, suitability, volume, taxonomy, labels   ║
║  STAGE 4 │ Analysis    – per-modality + city comparison computations        ║
║  STAGE 5 │ Plots       – 26 charts saved to /reports/ as PNG                ║
║  STAGE 6 │ Outputs     – write all processed CSVs + bonus integration       ║
║                                                                             ║
║  INPUTS  (data/raw/)                                                        ║
║    news.xlsx · incidents.xlsx · images.xlsx · videos.xlsx                   ║
║    social.csv · weather.csv                                                 ║
║                                                                             ║
║  OUTPUTS (data/processed/)                                                  ║
║    news_clean.csv · social_clean.csv · weather_clean.csv                    ║
║    incidents_clean.csv · images_labels.csv · videos_clean.csv               ║
║    city_metrics.csv · qc_summary.csv                                        ║
║    [Bonus] master_index.csv · item_features.csv · city_day_metrics.csv      ║
║                                                                             ║
║  OUTPUTS (reports/)                                                         ║
║    fig_01 … fig_26  (.png)  — one figure per analysis perspective           ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import warnings
from datetime import datetime

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 0 │ SETUP — paths, directories, visual style
# ══════════════════════════════════════════════════════════════════════════════

BASE      = os.path.dirname(os.path.abspath(__file__))
RAW       = os.path.join(BASE, "data", "raw")
PROCESSED = os.path.join(BASE, "data", "processed")
REPORTS   = os.path.join(BASE, "reports")

for d in [RAW, PROCESSED, REPORTS]:
    os.makedirs(d, exist_ok=True)

# ── Analysis parameters ───────────────────────────────────────────────────────
CITIES        = ["Lahore", "Rawalpindi"]
WINDOW_LAHORE = ("2026-02-06", "2026-02-08")
WINDOW_PINDI  = ("2026-02-13", "2026-02-15")

# ── Visual style ──────────────────────────────────────────────────────────────
CITY_COLORS = {"Lahore": "#1F6AA5", "Rawalpindi": "#E05A2B"}
SENT_COLORS = {"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c"}
PALETTE     = ["#1F6AA5", "#E05A2B", "#27AE60", "#8E44AD", "#E67E22"]
FONT_TITLE  = {"fontsize": 13, "fontweight": "bold", "pad": 10}
FONT_AXIS   = {"fontsize": 10}

def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_title(title, **FONT_TITLE)
    ax.set_xlabel(xlabel, **FONT_AXIS)
    ax.set_ylabel(ylabel, **FONT_AXIS)
    for sp in ax.spines.values():
        sp.set_color("#CCCCCC")
    ax.tick_params(colors="#444444", labelsize=9)
    ax.grid(axis="y", color="#EEEEEE", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

def savefig(fig, name):
    path = os.path.join(REPORTS, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"      [saved] {name}")

print("══════════════════════════════════════════════════════")
print("  Basant 2026 – End-to-End Analysis Pipeline")
print("══════════════════════════════════════════════════════")
print(f"  BASE      : {BASE}")
print(f"  RAW       : {RAW}")
print(f"  PROCESSED : {PROCESSED}")
print(f"  REPORTS   : {REPORTS}")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 1 │ COLLECT / LOG — load raw files, print source manifest
# ══════════════════════════════════════════════════════════════════════════════
print("\n──────────────────────────────────────────────────────")
print("  STAGE 1 │ COLLECT / LOG")
print("──────────────────────────────────────────────────────")

# Source log: what files exist, where they came from, date collected
SOURCE_LOG = [
    {"modality": "news",      "filename": "news.xlsx",      "format": "xlsx",
     "source_origin": "Dawn, Express Tribune, Geo News, Reuters, AP News, Al Jazeera, Gulf News, et al.",
     "collection_method": "Manual Google News search", "date_collected": "Feb 2026"},
    {"modality": "social",    "filename": "social.csv",     "format": "csv",
     "source_origin": "Facebook, Instagram, Twitter/X (public posts only)",
     "collection_method": "Manual platform search via public hashtags",  "date_collected": "Feb 2026"},
    {"modality": "weather",   "filename": "weather.csv",    "format": "csv",
     "source_origin": "open-meteo.com | visualcrossing.com",
     "collection_method": "Historical weather API queries (dual-source for cross-validation)", "date_collected": "Feb 2026"},
    {"modality": "incidents", "filename": "incidents.xlsx", "format": "xlsx",
     "source_origin": "Dawn, Geo News, Express Tribune, Pakistan Today, ProPakistani, LHC records",
     "collection_method": "Targeted news search on safety/incident keywords", "date_collected": "Feb 2026"},
    {"modality": "images",    "filename": "images.xlsx",    "format": "xlsx",
     "source_origin": "AP News, Dawn, Geo News, Al Jazeera, Gulf News, Express Tribune, et al.",
     "collection_method": "Image URLs extracted from news articles (metadata only, no download)", "date_collected": "Feb 2026"},
    {"modality": "videos",    "filename": "videos.xlsx",    "format": "xlsx",
     "source_origin": "YouTube, Urdupoint, Facebook (public videos)",
     "collection_method": "Manual search; metadata only (URL, title, duration, views)", "date_collected": "Feb 2026"},
]

# Load raw files
print("\n  Loading raw files …")
news_raw  = pd.read_excel(os.path.join(RAW, "news.xlsx"))
social_raw= pd.read_csv(  os.path.join(RAW, "social.csv"))
weather_raw=pd.read_csv(  os.path.join(RAW, "weather.csv"))
inc_raw   = pd.read_excel(os.path.join(RAW, "incidents.xlsx"))
img_raw   = pd.read_excel(os.path.join(RAW, "images.xlsx"), header=2)
vid_raw   = pd.read_excel(os.path.join(RAW, "videos.xlsx"))

print(f"  {'Modality':<12} {'File':<22} {'Raw rows':>9} {'Columns':>8}")
print(f"  {'─'*12} {'─'*22} {'─'*9} {'─'*8}")
for df, log in [(news_raw,"news.xlsx"),(social_raw,"social.csv"),
                (weather_raw,"weather.csv"),(inc_raw,"incidents.xlsx"),
                (img_raw,"images.xlsx"),(vid_raw,"videos.xlsx")]:
    print(f"  {log.split('.')[0]:<12} {log:<22} {len(df):>9} {len(df.columns):>8}")

# Write source log CSV
pd.DataFrame(SOURCE_LOG).to_csv(os.path.join(PROCESSED, "source_log.csv"), index=False)
print(f"\n  Source manifest → data/processed/source_log.csv")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 2 │ CLEAN — normalise, validate, deduplicate; 21 QC checks logged
# ══════════════════════════════════════════════════════════════════════════════
print("\n──────────────────────────────────────────────────────")
print("  STAGE 2 │ CLEAN")
print("──────────────────────────────────────────────────────")

# ── Shared utilities ──────────────────────────────────────────────────────────
CITY_MAP = {
    "lahore": "Lahore", "rawalpindi": "Rawalpindi",
    "pindi": "Rawalpindi", "rwp": "Rawalpindi",
}

def normalise_city(val):
    if pd.isna(val):
        return np.nan
    v = str(val).strip().lower()
    for k, std in CITY_MAP.items():
        if k in v:
            return std
    return str(val).strip().title()

def parse_date(val):
    """Multi-format date parser: ISO, US slash, UK slash, Excel serial."""
    if pd.isna(val):
        return pd.NaT
    if isinstance(val, (int, float)):
        try:
            return pd.Timestamp("1899-12-30") + pd.Timedelta(days=int(val))
        except Exception:
            return pd.NaT
    s = str(val).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d",
                "%d/%m/%Y", "%B %d, %Y"):
        try:
            return pd.Timestamp(datetime.strptime(s, fmt))
        except ValueError:
            pass
    try:
        return pd.Timestamp(s)
    except Exception:
        return pd.NaT

# ── QC log accumulator ────────────────────────────────────────────────────────
qc_records = []

def qc_log(modality, check_id, check_name, n_before, n_after, n_flagged, action, notes=""):
    qc_records.append({
        "modality": modality, "check_id": check_id, "check_name": check_name,
        "n_before": n_before, "n_after": n_after, "n_flagged": n_flagged,
        "action": action, "notes": notes,
    })
    flag = "⚑" if n_flagged > 0 else "✓"
    print(f"    {flag} {check_id:<8} {check_name:<45} flagged={n_flagged}  action={action}")

# ── 2A. Clean NEWS ────────────────────────────────────────────────────────────
print("\n  [2A] News …")
news = news_raw.copy()
n0   = len(news)

required = {"outlet","date","city","url","headline","snippet"}
missing  = required - set(news.columns)
qc_log("news","QC-N1","Required columns present",
       n0,n0,len(missing),"pass" if not missing else "flag",
       f"Missing: {missing}" if missing else "All required columns present")

news["city"] = news["city"].apply(normalise_city)
qc_log("news","QC-N2","City values recognisable",
       n0,n0,int(news["city"].isna().sum()),
       "flag" if news["city"].isna().any() else "pass")

news["date"] = news["date"].apply(parse_date)
n_bad = news["date"].isna().sum()
qc_log("news","QC-N3","Date parse success",
       n0,n0-int(n_bad),int(n_bad),"drop" if n_bad else "pass",
       f"{n_bad} rows with unparseable dates")
news = news.dropna(subset=["date"])

n_dup = news.duplicated(subset=["url"]).sum()
qc_log("news","QC-N4","Duplicate URL check",
       len(news),len(news)-int(n_dup),int(n_dup),"drop" if n_dup else "pass")
news = news.drop_duplicates(subset=["url"])

n_empty = (news["headline"].isna() | (news["headline"].str.strip()=="")).sum()
qc_log("news","QC-N5","Non-empty headline check",
       len(news),len(news),int(n_empty),"flag",f"{n_empty} empty headlines")
news["headline_missing"] = news["headline"].isna() | (news["headline"].str.strip()=="")

# ── 2B. Clean SOCIAL ─────────────────────────────────────────────────────────
print("\n  [2B] Social …")
social = social_raw.copy()
n0     = len(social)

qc_log("social","QC-S1","Minimum sample size (>=30 posts)",
       n0,n0,0 if n0>=30 else 1,"pass" if n0>=30 else "flag",f"n={n0}")

social["city"]     = social["city"].apply(normalise_city)
social["date"]     = social["date"].apply(parse_date)
social["platform"] = social["platform"].str.strip().str.title()

n_bad = social["date"].isna().sum()
qc_log("social","QC-S2","Date parse success",
       n0,n0-int(n_bad),int(n_bad),"drop" if n_bad else "pass")
social = social.dropna(subset=["date"])

n_dup = social.duplicated(subset=["url"]).sum()
qc_log("social","QC-S3","Duplicate URL check",
       len(social),len(social)-int(n_dup),int(n_dup),"drop" if n_dup else "pass")
social = social.drop_duplicates(subset=["url"])

def in_window(row):
    d, c = row["date"], row["city"]
    if c == "Lahore":
        return pd.Timestamp(WINDOW_LAHORE[0]) <= d <= pd.Timestamp(WINDOW_LAHORE[1])
    if c == "Rawalpindi":
        return pd.Timestamp(WINDOW_PINDI[0])  <= d <= pd.Timestamp(WINDOW_PINDI[1])
    return False

social["in_analysis_window"] = social.apply(in_window, axis=1)
n_out = (~social["in_analysis_window"]).sum()
qc_log("social","QC-S4","Posts within analysis window",
       len(social),len(social),int(n_out),"flag",
       f"{n_out} posts outside core window (retained, flagged)")

# ── 2C. Clean WEATHER ────────────────────────────────────────────────────────
print("\n  [2C] Weather …")
weather = weather_raw.copy()
n0      = len(weather)

weather["city"] = weather["city"].apply(normalise_city)
weather["date"] = weather["date"].apply(parse_date)

for col in ["temperature","wind_speed","precipitation"]:
    weather[col] = pd.to_numeric(weather[col], errors="coerce")

qc_log("weather","QC-W1","Temperature numeric coercion",
       n0,n0,int(weather["temperature"].isna().sum()),
       "flag" if weather["temperature"].isna().any() else "pass")
qc_log("weather","QC-W2","Wind speed numeric coercion",
       n0,n0,int(weather["wind_speed"].isna().sum()),
       "flag" if weather["wind_speed"].isna().any() else "pass")

n_dup_w = weather.duplicated(subset=["date","city"]).sum()
qc_log("weather","QC-W3","Duplicate city/date rows (two sources)",
       n0,n0//2,int(n_dup_w),"average",
       "Two sources per city/date averaged to one canonical row")

# ── 2D. Clean INCIDENTS ───────────────────────────────────────────────────────
print("\n  [2D] Incidents …")
inc  = inc_raw.copy()
n0   = len(inc)

inc["city"]          = inc["city"].apply(normalise_city)
inc["date"]          = inc["date"].apply(parse_date)
inc["incident_type"] = inc["incident_type"].str.strip().str.lower()
inc["source_type"]   = inc["source_type"].str.strip().str.title()
inc["severity"]      = inc["severity"].str.strip().str.lower()
inc["count"]         = pd.to_numeric(inc["count"], errors="coerce").fillna(0).astype(int)

n_bad = inc["date"].isna().sum()
qc_log("incidents","QC-I1","Date parse success",
       n0,n0-int(n_bad),int(n_bad),"drop" if n_bad else "pass")
inc = inc.dropna(subset=["date"])

n_dup = inc.duplicated(subset=["date","city","incident_type","url"]).sum()
qc_log("incidents","QC-I2","Deduplication (same date/city/type/url)",
       len(inc),len(inc)-int(n_dup),int(n_dup),"drop" if n_dup else "pass",
       "Same event at same URL deduplicated")
inc = inc.drop_duplicates(subset=["date","city","incident_type","url"])

VALID_SEV = {"fatal","severe","moderate","low","high"}
n_bad_sev = (~inc["severity"].isin(VALID_SEV)).sum()
qc_log("incidents","QC-I3","Severity vocabulary validation",
       len(inc),len(inc),int(n_bad_sev),"flag" if n_bad_sev else "pass",
       f"{n_bad_sev} non-standard severity values")

# ── 2E. Clean IMAGES ─────────────────────────────────────────────────────────
print("\n  [2E] Images …")
img = img_raw[img_raw.iloc[:,0] != "image_id"].reset_index(drop=True)
img.columns = ["image_id","image_url","page_url","source","date_of_event","city"]
img = img.dropna(subset=["image_id"]).copy()

img["city"]          = img["city"].apply(normalise_city)
img["date_of_event"] = img["date_of_event"].apply(parse_date)
n0 = len(img)

qc_log("images","QC-M1","Minimum image sample (>=20)",
       n0,n0,0 if n0>=20 else 1,"pass" if n0>=20 else "flag",f"n={n0}")
qc_log("images","QC-M2","Image URL present",
       n0,n0,int(img["image_url"].isna().sum()),
       "flag" if img["image_url"].isna().any() else "pass")

# ── 2F. Clean VIDEOS ─────────────────────────────────────────────────────────
print("\n  [2F] Videos …")
vid  = vid_raw.copy()
n0   = len(vid)

vid["city"]          = vid["city"].apply(normalise_city)
vid["date_of_event"] = vid["date_of_event"].apply(parse_date)
vid["platform"]      = vid["platform"].str.strip().str.title()
vid["language"]      = vid["language"].str.strip().str.title()

for col in ["duration_seconds","views"]:
    vid[col] = pd.to_numeric(vid[col], errors="coerce")

qc_log("videos","QC-V1","Minimum video sample (>=10)",
       n0,n0,0 if n0>=10 else 1,"pass" if n0>=10 else "flag",f"n={n0}")
qc_log("videos","QC-V2","Video URL present",
       n0,n0,int(vid["url"].isna().sum()),
       "flag" if vid["url"].isna().any() else "pass")

n_dup = vid.duplicated(subset=["video_id"]).sum()
qc_log("videos","QC-V3","Duplicate video_id",
       n0,n0-int(n_dup),int(n_dup),"drop" if n_dup else "pass")
vid = vid.drop_duplicates(subset=["video_id"])

print(f"\n  QC complete — {len(qc_records)} checks run")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 3 │ FEATURES — engineer all derived fields per modality
# ══════════════════════════════════════════════════════════════════════════════
print("\n──────────────────────────────────────────────────────")
print("  STAGE 3 │ FEATURES")
print("──────────────────────────────────────────────────────")

# ── 3A. Sentiment lexicon ─────────────────────────────────────────────────────
POS_WORDS = {
    "happy","celebrate","joy","festival","beautiful","amazing","wonderful",
    "great","love","excited","vibrant","cultural","heritage","revival",
    "return","color","colours","kite","flying","tradition","festive",
    "boost","iconic","prime","emotion","official","grand","revive",
    "mubarak","khushi","rang","jashn","roshan","tayari","maza",
}
NEG_WORDS = {
    "death","dead","killed","injury","injured","accident","fatal","harm",
    "danger","banned","ban","illegal","arrest","violat","crackdown","fire",
    "electrocution","falls","casualties","victim","prohibit","restrict",
    "safety","court","scrutiny","petition",
}

def lexicon_sentiment(text):
    """Keyword lexicon score in [-1, 1]. Covers English + basic Roman Urdu."""
    if pd.isna(text) or str(text).strip() == "":
        return 0.0
    tokens = re.findall(r"[a-z]+", str(text).lower())
    pos = sum(1 for t in tokens if any(p in t for p in POS_WORDS))
    neg = sum(1 for t in tokens if any(n in t for n in NEG_WORDS))
    total = pos + neg
    return 0.0 if total == 0 else round((pos - neg) / total, 4)

def sent_label(s):
    return "positive" if s > 0.1 else ("negative" if s < -0.1 else "neutral")

# ── 3B. News features ─────────────────────────────────────────────────────────
print("  [3A] News features …")
news["headline_clean"] = news["headline"].fillna("").str.strip().str.replace(r"\s+", " ", regex=True)
news["snippet_clean"]  = news["snippet"].fillna("").str.strip().str.replace(r"\s+", " ", regex=True)
news["sentiment_score"] = (news["headline_clean"] + " " + news["snippet_clean"]).apply(lexicon_sentiment)
news["sentiment_label"] = news["sentiment_score"].apply(sent_label)
news["date_only"]       = news["date"].dt.normalize()
news_vol = news.groupby(["city","date_only"]).size().reset_index(name="news_volume_day")
news     = news.merge(news_vol, on=["city","date_only"], how="left")
print(f"      sentiment computed on {len(news)} articles  |  {news['sentiment_label'].value_counts().to_dict()}")

# ── 3C. Social features ───────────────────────────────────────────────────────
print("  [3B] Social features …")
social["caption_clean"]  = (social["caption"].fillna("").str.strip()
                             .str.replace(r"\s+", " ", regex=True)
                             .str.replace(r"[^\w\s#@?,.\-!']", "", regex=True))
social["hashtags_clean"] = social["hashtags"].fillna("").str.strip().str.lower()
social["hashtag_count"]  = social["hashtags_clean"].apply(
    lambda x: len(re.findall(r"#\w+", x)))
social["sentiment_score"] = social["caption_clean"].apply(lexicon_sentiment)
social["sentiment_label"] = social["sentiment_score"].apply(sent_label)
social["date_only"]       = social["date"].dt.normalize()
soc_vol = social.groupby(["city","date_only"]).size().reset_index(name="social_volume_day")
social  = social.merge(soc_vol, on=["city","date_only"], how="left")
print(f"      sentiment computed on {len(social)} posts  |  {social['sentiment_label'].value_counts().to_dict()}")

# ── 3D. Weather suitability score ─────────────────────────────────────────────
print("  [3C] Weather suitability score …")
# Average dual-source readings into one canonical row per city/date
weather_avg = (weather
    .groupby(["date","city"], as_index=False)
    .agg(temperature=("temperature","mean"),
         wind_speed =("wind_speed", "mean"),
         precipitation=("precipitation","mean"),
         sources=("source", lambda x: " | ".join(x.dropna().unique())))
    .round({"temperature":2,"wind_speed":2,"precipitation":3}))

# ── Suitability rubric (0–100) ────────────────────────────────────────────────
# Temperature  10–25°C  → 40 pts  │  5–10 or 25–30°C → 20 pts  │  else 0
# Wind speed   5–25 km/h → 40 pts │  2–5 km/h        → 20 pts  │  else 0
# Precipitation 0 mm    → 20 pts  │  any rain         → 0 pts
def temp_score(t):
    if pd.isna(t): return 0
    return 40 if 10<=t<=25 else (20 if (5<=t<10 or 25<t<=30) else 0)
def wind_score(w):
    if pd.isna(w): return 0
    return 40 if 5<=w<=25 else (20 if 2<=w<5 else 0)
def precip_score(p):
    return 0 if pd.isna(p) else (20 if p==0 else 0)
def suit_label(s):
    return "excellent" if s>=80 else ("good" if s>=60 else ("fair" if s>=40 else "poor"))

weather_avg["temp_score"]        = weather_avg["temperature"].apply(temp_score)
weather_avg["wind_score"]        = weather_avg["wind_speed"].apply(wind_score)
weather_avg["precip_score"]      = weather_avg["precipitation"].apply(precip_score)
weather_avg["suitability_score"] = (weather_avg["temp_score"]
                                    + weather_avg["wind_score"]
                                    + weather_avg["precip_score"])
weather_avg["suitability_label"] = weather_avg["suitability_score"].apply(suit_label)

n_out_range = ((weather_avg["suitability_score"]<0)|(weather_avg["suitability_score"]>100)).sum()
qc_log("weather","QC-W4","Suitability score in [0,100]",
       len(weather_avg),len(weather_avg),int(n_out_range),
       "pass" if not n_out_range else "flag")
print(f"      suitability computed on {len(weather_avg)} city-days  |  {weather_avg['suitability_label'].value_counts().to_dict()}")

# ── 3E. Incident taxonomy ─────────────────────────────────────────────────────
print("  [3D] Incident taxonomy …")
TAXONOMY = {
    "death":"fatality","death_total":"fatality","electrocution":"fatality",
    "injury":"physical_injury","kite_string_injury":"physical_injury",
    "rooftop_fall":"physical_injury","gunfire_injury":"physical_injury",
    "arrest":"law_enforcement","seizure":"law_enforcement",
    "traffic":"infrastructure","public_transport_incident":"infrastructure",
    "total_accidents":"aggregate_report",
}
inc["incident_category"] = inc["incident_type"].map(TAXONOMY).fillna("other")
inc["cross_source_dup"]  = inc.duplicated(subset=["date","city","incident_type"], keep=False)
print(f"      taxonomy applied: {inc['incident_category'].value_counts().to_dict()}")

# ── 3F. Image labels ──────────────────────────────────────────────────────────
print("  [3E] Image labels …")
HIGH_SOURCES = {"Ap News","Geo News","Al Jazeera","Gulf News","Reuters"}

def crowd_level(source, city, date):
    if pd.isna(date): return "unknown"
    d = date.date()
    if city=="Lahore" and d in [datetime(2026,2,6).date(),
                                 datetime(2026,2,7).date(),
                                 datetime(2026,2,8).date()]:
        return "high" if any(s in str(source) for s in HIGH_SOURCES) else "medium"
    return "medium" if city=="Rawalpindi" else "low"

def kite_presence(url):
    if pd.isna(url): return "unknown"
    return "yes" if ("kite" in str(url).lower() or "basant" in str(url).lower()) else "likely"

img["crowd_level"]   = img.apply(lambda r: crowd_level(r["source"],r["city"],r["date_of_event"]), axis=1)
img["kite_presence"] = img["image_url"].apply(kite_presence)
img["time_of_day"]   = "unknown"   # requires visual inspection
img["police_visible"]= "unknown"   # requires visual inspection
img["source"]        = img["source"].str.strip()
print(f"      labels: crowd={img['crowd_level'].value_counts().to_dict()}  kite={img['kite_presence'].value_counts().to_dict()}")

# ── 3G. Video features ────────────────────────────────────────────────────────
print("  [3F] Video features …")
def dur_label(s):
    if pd.isna(s): return "unknown"
    return "short (<1 min)" if s<60 else ("medium (1-5 min)" if s<300 else "long (>5 min)")

vid["sentiment_score"] = vid["caption"].apply(lexicon_sentiment)
vid["sentiment_label"] = vid["sentiment_score"].apply(sent_label)
vid["duration_label"]  = vid["duration_seconds"].apply(dur_label)
print(f"      duration: {vid['duration_label'].value_counts().to_dict()}")

print("  Feature engineering complete.")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 4 │ ANALYSIS — per-modality computations + city comparison table
# ══════════════════════════════════════════════════════════════════════════════
print("\n──────────────────────────────────────────────────────")
print("  STAGE 4 │ ANALYSIS")
print("──────────────────────────────────────────────────────")

# ── 4A. Assemble cleaned DataFrames ──────────────────────────────────────────
news_clean = news[[
    "outlet","date","city","url","headline_clean","snippet_clean",
    "sentiment_score","sentiment_label","news_volume_day","headline_missing"
]].rename(columns={"headline_clean":"headline","snippet_clean":"snippet"})

social_clean = social[[
    "platform","date","city","url","caption_clean","hashtags_clean",
    "hashtag_count","sentiment_score","sentiment_label",
    "social_volume_day","in_analysis_window"
]].rename(columns={"caption_clean":"caption","hashtags_clean":"hashtags"})

weather_clean = weather_avg[[
    "date","city","temperature","wind_speed","precipitation","sources",
    "temp_score","wind_score","precip_score","suitability_score","suitability_label"
]]

inc_clean = inc[[
    "date","city","incident_type","incident_category","count","severity",
    "source_type","url","description","cross_source_dup"
]]

images_clean = img[[
    "image_id","image_url","page_url","source","date_of_event","city",
    "crowd_level","kite_presence","time_of_day","police_visible"
]]

videos_clean = vid[[
    "video_id","url","platform","date_of_event","city","caption",
    "duration_seconds","duration_label","views","thumbnail_url",
    "language","sentiment_score","sentiment_label"
]]

# ── 4B. Celebration indicators ────────────────────────────────────────────────
print("\n  [4A] Celebration indicators …")
for city in CITIES:
    n  = len(news_clean[news_clean["city"]==city])
    s  = len(social_clean[social_clean["city"]==city])
    sw = len(social_clean[(social_clean["city"]==city)&social_clean["in_analysis_window"]])
    print(f"      {city}: news={n}  social_total={s}  social_in_window={sw}")

# ── 4C. Incident analysis ─────────────────────────────────────────────────────
print("\n  [4B] Incident analysis …")
inc_ind = inc_clean[~inc_clean["incident_type"].isin(["total_accidents","death_total"])]
for city in CITIES:
    sub = inc_ind[inc_ind["city"]==city]
    print(f"      {city}: total_count={sub['count'].sum()}  fatal={sub[sub['severity']=='fatal']['count'].sum()}  records={len(sub)}")

# ── 4D. Weather suitability summary ──────────────────────────────────────────
print("\n  [4C] Weather suitability …")
for city in CITIES:
    sub = weather_clean[weather_clean["city"]==city]
    print(f"      {city}: mean_suit={sub['suitability_score'].mean():.1f}  "
          f"temp_range={sub['temperature'].min():.1f}–{sub['temperature'].max():.1f}°C  "
          f"wind_range={sub['wind_speed'].min():.1f}–{sub['wind_speed'].max():.1f} km/h")

# ── 4E. Sentiment summary ─────────────────────────────────────────────────────
print("\n  [4D] Sentiment summary …")
for city in CITIES:
    ns = news_clean[news_clean["city"]==city]["sentiment_score"].mean()
    ss = social_clean[social_clean["city"]==city]["sentiment_score"].mean()
    print(f"      {city}: news_sent_mean={ns:.4f}  social_sent_mean={ss:.4f}")

# ── 4F. City comparison table ─────────────────────────────────────────────────
print("\n  [4E] City comparison table …")
city_rows = []
for city in CITIES:
    inc_city = inc_ind[inc_ind["city"]==city]
    wc       = weather_clean[weather_clean["city"]==city]
    city_rows.append({
        "city":                  city,
        "date_window":           "Feb 6-8 2026" if city=="Lahore" else "Feb 13-15 2026",
        "n_days":                3,
        "social_volume":         int(social_clean[social_clean["city"]==city].shape[0]),
        "news_volume":           int(news_clean[news_clean["city"]==city].shape[0]),
        "incidents_total":       int(inc_city["count"].sum()),
        "fatal_incidents":       int(inc_city[inc_city["severity"]=="fatal"]["count"].sum()),
        "arrests":               int(inc_city[inc_city["incident_category"]=="law_enforcement"]["count"].sum()),
        "suitability_mean":      round(wc["suitability_score"].mean(), 1),
        "sentiment_news_mean":   round(news_clean[news_clean["city"]==city]["sentiment_score"].mean(), 4),
        "sentiment_social_mean": round(social_clean[social_clean["city"]==city]["sentiment_score"].mean(), 4),
        "images_count":          int(images_clean[images_clean["city"]==city].shape[0]),
        "videos_count":          int(videos_clean[videos_clean["city"]==city].shape[0]),
    })
city_metrics = pd.DataFrame(city_rows)
print(city_metrics.to_string(index=False))

# ── 4G. City-day metrics (bonus integration) ──────────────────────────────────
print("\n  [4F] City-day metrics …")
day_rows = []
all_days = ([(c,d) for c in ["Lahore"]     for d in pd.date_range(*WINDOW_LAHORE)] +
            [(c,d) for c in ["Rawalpindi"] for d in pd.date_range(*WINDOW_PINDI)])
for city, day in all_days:
    sc  = social_clean[(social_clean["city"]==city)&(social_clean["date"].dt.normalize()==day)]
    nc  = news_clean[(news_clean["city"]==city)&(news_clean["date"].dt.normalize()==day)]
    wc  = weather_clean[(weather_clean["city"]==city)&(weather_clean["date"].dt.normalize()==day)]
    icd = inc_ind[(inc_ind["city"]==city)&(inc_ind["date"].dt.normalize()==day)]
    day_rows.append({
        "city":city,"date":day.strftime("%Y-%m-%d"),
        "social_volume":int(len(sc)),"news_volume":int(len(nc)),
        "social_sentiment_mean":round(sc["sentiment_score"].mean(),4),
        "news_sentiment_mean":  round(nc["sentiment_score"].mean(),4),
        "suitability_score":    float(wc["suitability_score"].values[0]) if len(wc) else np.nan,
        "temperature_c":        float(wc["temperature"].values[0])       if len(wc) else np.nan,
        "wind_speed_kmh":       float(wc["wind_speed"].values[0])        if len(wc) else np.nan,
        "incident_count":       int(icd["count"].sum()),
        "fatal_count":          int(icd[icd["severity"]=="fatal"]["count"].sum()),
    })
city_day_metrics = pd.DataFrame(day_rows)

print("  Analysis complete.")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 5 │ PLOTS — 26 charts across all modalities + city comparison
# ══════════════════════════════════════════════════════════════════════════════
print("\n──────────────────────────────────────────────────────")
print("  STAGE 5 │ PLOTS")
print("──────────────────────────────────────────────────────")

# ── Fig 01 – News volume per city per day ─────────────────────────────────────
print("  [5A] News charts …")
news_daily = (news_clean.groupby(["city", news_clean["date"].dt.date])
                         .size().reset_index(name="count").rename(columns={"date":"day"}))
fig, axes = plt.subplots(1,2,figsize=(13,5),facecolor="white")
fig.suptitle("News Coverage of Basant 2026", fontsize=15, fontweight="bold")
for ax,(city,grp) in zip(axes, news_daily.groupby("city")):
    bars=ax.bar(grp["day"].astype(str),grp["count"],color=CITY_COLORS[city],
                width=0.5,zorder=2,edgecolor="white")
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.05,
                str(int(b.get_height())),ha="center",va="bottom",fontsize=10,fontweight="bold")
    style_ax(ax,f"{city}: Daily News Volume","Date","Article Count")
    ax.set_ylim(0,grp["count"].max()*1.4)
    ax.set_xticklabels(grp["day"].astype(str),rotation=25,ha="right")
plt.tight_layout(); savefig(fig,"fig_01_news_daily_volume.png")

# ── Fig 02 – News sentiment pie ───────────────────────────────────────────────
fig, axes = plt.subplots(1,2,figsize=(13,5),facecolor="white")
fig.suptitle("News Sentiment Distribution by City",fontsize=14,fontweight="bold")
for ax,city in zip(axes,CITIES):
    sub=news_clean[news_clean["city"]==city]["sentiment_label"].value_counts()
    vals=[sub.get(l,0) for l in ["positive","neutral","negative"]]
    wedges,texts,ats=ax.pie(vals,labels=["Positive","Neutral","Negative"],
                            colors=[SENT_COLORS[l] for l in ["positive","neutral","negative"]],
                            autopct="%1.0f%%",startangle=140,
                            wedgeprops={"edgecolor":"white","linewidth":1.5},
                            textprops={"fontsize":10})
    for at in ats: at.set_fontsize(10); at.set_fontweight("bold")
    ax.set_title(f"{city}  (n={sum(vals)})",fontsize=12,fontweight="bold")
plt.tight_layout(); savefig(fig,"fig_02_news_sentiment_pie.png")

# ── Fig 03 – News sentiment trend ────────────────────────────────────────────
fig,ax=plt.subplots(figsize=(12,5),facecolor="white")
for city,grp in news_clean.groupby("city"):
    ds=grp.groupby(grp["date"].dt.date)["sentiment_score"].mean().reset_index()
    ax.plot(ds["date"].astype(str),ds["sentiment_score"],
            marker="o",linewidth=2,markersize=7,color=CITY_COLORS[city],label=city,zorder=3)
    for _,row in ds.iterrows():
        ax.annotate(f'{row["sentiment_score"]:.2f}',(str(row["date"]),row["sentiment_score"]),
                    textcoords="offset points",xytext=(0,9),ha="center",fontsize=8,color=CITY_COLORS[city])
ax.axhline(0,color="#999",linewidth=1,linestyle="--",label="Neutral (0.0)")
style_ax(ax,"Mean Daily News Sentiment Score Over Time","Date","Sentiment Score")
ax.legend(fontsize=9); ax.set_ylim(-1.2,1.2); plt.xticks(rotation=30,ha="right")
plt.tight_layout(); savefig(fig,"fig_03_news_sentiment_trend.png")

# ── Fig 04 – Top news outlets ─────────────────────────────────────────────────
fig,ax=plt.subplots(figsize=(10,5),facecolor="white")
oc=news_clean["outlet"].value_counts()
ax.barh(oc.index[::-1],oc.values[::-1],color=PALETTE[0],edgecolor="white",zorder=2)
for i,v in enumerate(oc.values[::-1]):
    ax.text(v+0.05,i,str(v),va="center",fontsize=9)
style_ax(ax,"News Articles by Outlet","Count","")
ax.set_xlim(0,oc.max()+2); plt.tight_layout(); savefig(fig,"fig_04_news_outlets.png")

# ── Fig 05 – Social volume per day ───────────────────────────────────────────
print("  [5B] Social charts …")
sw=social_clean[social_clean["in_analysis_window"]==True]
sd=(sw.groupby(["city",sw["date"].dt.date]).size()
      .reset_index(name="count").rename(columns={"date":"day"}))
fig,axes=plt.subplots(1,2,figsize=(13,5),facecolor="white")
fig.suptitle("Social Media Activity During Basant 2026 (In-Window Posts)",fontsize=14,fontweight="bold")
for ax,(city,grp) in zip(axes,sd.groupby("city")):
    bars=ax.bar(grp["day"].astype(str),grp["count"],color=CITY_COLORS[city],
                width=0.4,zorder=2,edgecolor="white")
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.05,
                str(int(b.get_height())),ha="center",va="bottom",fontsize=11,fontweight="bold")
    style_ax(ax,f"{city}: Daily Post Volume","Date","Post Count")
    ax.set_ylim(0,max(grp["count"].max()*1.4,3))
    ax.set_xticklabels(grp["day"].astype(str),rotation=30,ha="right")
plt.tight_layout(); savefig(fig,"fig_05_social_daily_volume.png")

# ── Fig 06 – Social sentiment bars ───────────────────────────────────────────
fig,axes=plt.subplots(1,2,figsize=(13,5),facecolor="white")
fig.suptitle("Social Media Sentiment by City",fontsize=14,fontweight="bold")
for ax,city in zip(axes,CITIES):
    sub=social_clean[social_clean["city"]==city]["sentiment_label"].value_counts()
    vals=[sub.get(l,0) for l in ["positive","neutral","negative"]]
    bars=ax.bar(["Positive","Neutral","Negative"],vals,
                color=[SENT_COLORS[l] for l in ["positive","neutral","negative"]],
                edgecolor="white",zorder=2,width=0.5)
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.05,
                str(int(b.get_height())),ha="center",va="bottom",fontsize=12,fontweight="bold")
    style_ax(ax,f"{city} Social Sentiment (n={sum(vals)})","","Post Count")
    ax.set_ylim(0,max(vals)*1.4 if max(vals)>0 else 5)
plt.tight_layout(); savefig(fig,"fig_06_social_sentiment_bars.png")

# ── Fig 07 – Platform distribution ───────────────────────────────────────────
fig,ax=plt.subplots(figsize=(8,5),facecolor="white")
pc=social_clean.groupby(["city","platform"]).size().unstack(fill_value=0)
pc.plot(kind="bar",ax=ax,color=PALETTE[:pc.shape[1]],edgecolor="white",width=0.6,zorder=2)
style_ax(ax,"Social Platform Distribution by City","City","Post Count")
ax.legend(title="Platform",bbox_to_anchor=(1.01,1),loc="upper left",fontsize=9)
plt.xticks(rotation=0); plt.tight_layout(); savefig(fig,"fig_07_social_platform_city.png")

# ── Fig 08 – News vs Social sentiment comparison ──────────────────────────────
fig,ax=plt.subplots(figsize=(9,5),facecolor="white")
x=np.arange(len(CITIES)); w=0.3
nm=[news_clean[news_clean["city"]==c]["sentiment_score"].mean() for c in CITIES]
sm=[social_clean[social_clean["city"]==c]["sentiment_score"].mean() for c in CITIES]
b1=ax.bar(x-w/2,nm,width=w,color="#1F6AA5",label="News",edgecolor="white",zorder=2)
b2=ax.bar(x+w/2,sm,width=w,color="#E05A2B",label="Social",edgecolor="white",zorder=2)
for b in list(b1)+list(b2):
    h=b.get_height()
    ax.text(b.get_x()+b.get_width()/2,h+(0.02 if h>=0 else -0.06),
            f"{h:.2f}",ha="center",va="bottom",fontsize=9)
ax.axhline(0,color="#999",linewidth=1,linestyle="--")
style_ax(ax,"Mean Sentiment Score: News vs Social by City","City","Mean Sentiment Score")
ax.set_xticks(x); ax.set_xticklabels(CITIES,fontsize=11); ax.set_ylim(-1.0,0.8); ax.legend(fontsize=10)
plt.tight_layout(); savefig(fig,"fig_08_news_vs_social_sentiment.png")

# ── Fig 09 – Weather temp + wind ─────────────────────────────────────────────
print("  [5C] Weather charts …")
fig,axes=plt.subplots(1,2,figsize=(13,5),facecolor="white")
fig.suptitle("Weather Conditions During Basant 2026",fontsize=14,fontweight="bold")
for ax,city in zip(axes,CITIES):
    wc=weather_clean[weather_clean["city"]==city].copy()
    wc["label"]=wc["date"].dt.strftime("%b %d"); x=np.arange(len(wc))
    ax2=ax.twinx()
    ax.bar(x,wc["temperature"],width=0.35,color=CITY_COLORS[city],alpha=0.85,
           label="Temperature (°C)",zorder=2,edgecolor="white")
    ax2.plot(x,wc["wind_speed"],marker="s",color="#E67E22",linewidth=2,
             markersize=8,label="Wind Speed (km/h)",zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(wc["label"],rotation=15)
    ax.set_ylabel("Temperature (°C)",color=CITY_COLORS[city],fontsize=9)
    ax2.set_ylabel("Wind Speed (km/h)",color="#E67E22",fontsize=9)
    ax.set_title(city,fontsize=12,fontweight="bold")
    ax.set_ylim(0,30); ax2.set_ylim(0,30)
    ax.tick_params(axis="y",colors=CITY_COLORS[city])
    ax2.tick_params(axis="y",colors="#E67E22")
    ax.grid(axis="y",color="#EEEEEE",linewidth=0.8)
    l1,lb1=ax.get_legend_handles_labels(); l2,lb2=ax2.get_legend_handles_labels()
    ax.legend(l1+l2,lb1+lb2,fontsize=8,loc="upper left")
plt.tight_layout(); savefig(fig,"fig_09_weather_temp_wind.png")

# ── Fig 10 – Suitability heatmap ─────────────────────────────────────────────
pivot=weather_clean.pivot(index="city",columns="date",values="suitability_score")
pivot.columns=[c.strftime("%b %d") for c in pivot.columns]
fig,ax=plt.subplots(figsize=(10,3.5),facecolor="white")
sns.heatmap(pivot,ax=ax,annot=True,fmt=".0f",cmap="YlGn",linewidths=0.5,
            linecolor="white",vmin=0,vmax=100,annot_kws={"size":13,"weight":"bold"},
            cbar_kws={"label":"Suitability Score (0–100)"})
ax.set_title("Weather Suitability Score by City and Day",**FONT_TITLE)
ax.set_xlabel("Date"); ax.set_ylabel("City"); plt.tight_layout()
savefig(fig,"fig_10_weather_suitability_heatmap.png")

# ── Fig 11 – Suitability components ──────────────────────────────────────────
fig,ax=plt.subplots(figsize=(11,5),facecolor="white")
weather_clean["label"]=weather_clean["city"]+"\n"+weather_clean["date"].dt.strftime("%b %d")
x=np.arange(len(weather_clean)); w=0.25
b1=ax.bar(x-w,weather_clean["temp_score"],  width=w,label="Temperature",color="#2196F3",edgecolor="white",zorder=2)
b2=ax.bar(x,  weather_clean["wind_score"],  width=w,label="Wind Speed", color="#FF9800",edgecolor="white",zorder=2)
b3=ax.bar(x+w,weather_clean["precip_score"],width=w,label="Precipitation",color="#4CAF50",edgecolor="white",zorder=2)
for b in list(b1)+list(b2)+list(b3):
    if b.get_height()>0:
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.5,str(int(b.get_height())),
                ha="center",va="bottom",fontsize=8)
style_ax(ax,"Suitability Score Components by City-Day","City – Date","Component Score (pts)")
ax.set_xticks(x); ax.set_xticklabels(weather_clean["label"],fontsize=9)
ax.set_ylim(0,60); ax.legend(fontsize=9)
plt.tight_layout(); savefig(fig,"fig_11_weather_components.png")

# ── Fig 12 – Incidents by category ───────────────────────────────────────────
print("  [5D] Incidents charts …")
cc=(inc_ind.groupby(["city","incident_category"])["count"].sum().reset_index())
cp=cc.pivot(index="incident_category",columns="city",values="count").fillna(0)
fig,ax=plt.subplots(figsize=(11,5),facecolor="white")
cp.plot(kind="bar",ax=ax,color=[CITY_COLORS["Lahore"],CITY_COLORS["Rawalpindi"]],
        edgecolor="white",width=0.6,zorder=2)
for p in ax.patches:
    if p.get_height()>0:
        ax.annotate(f"{int(p.get_height())}",
                    (p.get_x()+p.get_width()/2,p.get_height()),
                    ha="center",va="bottom",fontsize=9,fontweight="bold",
                    xytext=(0,3),textcoords="offset points")
style_ax(ax,"Incident Counts by Category and City","Incident Category","Total Count")
ax.set_xticklabels(ax.get_xticklabels(),rotation=25,ha="right"); ax.legend(title="City",fontsize=9)
plt.tight_layout(); savefig(fig,"fig_12_incidents_by_category.png")

# ── Fig 13 – Lahore daily incidents ──────────────────────────────────────────
li=(inc_ind[inc_ind["city"]=="Lahore"]
    .groupby(inc_ind[inc_ind["city"]=="Lahore"]["date"].dt.date)["count"]
    .sum().reset_index())
li.columns=["day","count"]
fig,ax=plt.subplots(figsize=(9,5),facecolor="white")
bars=ax.bar(li["day"].astype(str),li["count"],color=CITY_COLORS["Lahore"],
            edgecolor="white",zorder=2,width=0.4)
for b in bars:
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.5,
            str(int(b.get_height())),ha="center",va="bottom",fontsize=12,fontweight="bold")
style_ax(ax,"Lahore: Daily Incident Count (Feb 6–8 2026)","Date","Reported Count")
plt.tight_layout(); savefig(fig,"fig_13_incidents_lahore_daily.png")

# ── Fig 14 – Severity breakdown ───────────────────────────────────────────────
SEV_COL={"fatal":"#C0392B","severe":"#E67E22","high":"#F39C12","moderate":"#F1C40F","low":"#2ECC71"}
sp=(inc_ind.groupby(["city","severity"])["count"].sum().reset_index())
spiv=sp.pivot(index="city",columns="severity",values="count").fillna(0)
ord_sev=[s for s in ["fatal","severe","high","moderate","low"] if s in spiv.columns]
spiv=spiv[ord_sev]
fig,ax=plt.subplots(figsize=(9,5),facecolor="white")
bot=np.zeros(len(spiv))
for sev in ord_sev:
    vals=spiv[sev].values
    ax.bar(spiv.index,vals,bottom=bot,color=SEV_COL.get(sev,"#95A5A6"),
           label=sev.capitalize(),edgecolor="white",zorder=2)
    bot+=vals
style_ax(ax,"Incident Severity Breakdown by City","City","Total Count")
ax.legend(title="Severity",bbox_to_anchor=(1.01,1),loc="upper left",fontsize=9)
plt.tight_layout(); savefig(fig,"fig_14_incidents_severity.png")

# ── Fig 15 – Source type ──────────────────────────────────────────────────────
fig,ax=plt.subplots(figsize=(8,5),facecolor="white")
sc2=incidents_source_pivot=inc_clean.groupby(["city","source_type"]).size().unstack(fill_value=0)
sc2.plot(kind="bar",ax=ax,color=["#27AE60","#E74C3C","#3498DB"][:sc2.shape[1]],
         edgecolor="white",width=0.5,zorder=2)
style_ax(ax,"Incident Records by Source Type and City","City","Record Count")
ax.legend(title="Source Type",fontsize=9); plt.xticks(rotation=0)
plt.tight_layout(); savefig(fig,"fig_15_incidents_source_type.png")

# ── Fig 16 – Images city + crowd ─────────────────────────────────────────────
print("  [5E] Media charts …")
fig,axes=plt.subplots(1,2,figsize=(12,5),facecolor="white")
fig.suptitle("Image Media Analysis",fontsize=14,fontweight="bold")
cimg=images_clean["city"].value_counts()
axes[0].pie(cimg.values,labels=cimg.index,
            colors=[CITY_COLORS.get(c,"#95A5A6") for c in cimg.index],
            autopct="%1.0f%%",startangle=90,
            wedgeprops={"edgecolor":"white","linewidth":1.5},textprops={"fontsize":10})
axes[0].set_title(f"Images by City (n={len(images_clean)})",fontsize=11,fontweight="bold")
crow=images_clean.groupby(["city","crowd_level"]).size().unstack(fill_value=0)
crow.plot(kind="bar",ax=axes[1],color=["#2ECC71","#E67E22","#E74C3C","#95A5A6"][:crow.shape[1]],
          edgecolor="white",width=0.5,zorder=2)
style_ax(axes[1],"Crowd Level Labels by City","City","Image Count")
axes[1].legend(title="Crowd Level",fontsize=9); axes[1].tick_params(axis="x",rotation=0)
plt.tight_layout(); savefig(fig,"fig_16_images_city_crowd.png")

# ── Fig 17 – Kite presence + sources ─────────────────────────────────────────
fig,axes=plt.subplots(1,2,figsize=(12,5),facecolor="white")
fig.suptitle("Image Metadata Analysis",fontsize=14,fontweight="bold")
kp=images_clean["kite_presence"].value_counts()
axes[0].pie(kp.values,labels=kp.index,colors=["#27AE60","#F39C12","#BDC3C7"][:len(kp)],
            autopct="%1.0f%%",startangle=120,
            wedgeprops={"edgecolor":"white","linewidth":1.5},textprops={"fontsize":10})
axes[0].set_title("Kite Presence in Images",fontsize=11,fontweight="bold")
src_c=images_clean["source"].value_counts()
axes[1].barh(src_c.index[::-1],src_c.values[::-1],color=PALETTE[0],edgecolor="white",zorder=2)
for i,v in enumerate(src_c.values[::-1]):
    axes[1].text(v+0.05,i,str(v),va="center",fontsize=9)
style_ax(axes[1],"Images by News Source","Count",""); axes[1].set_xlim(0,src_c.max()+2)
plt.tight_layout(); savefig(fig,"fig_17_images_kite_sources.png")

# ── Fig 18 – Videos city + duration ──────────────────────────────────────────
fig,axes=plt.subplots(1,2,figsize=(12,5),facecolor="white")
fig.suptitle("Video Metadata Analysis",fontsize=14,fontweight="bold")
vc=videos_clean["city"].value_counts()
axes[0].pie(vc.values,labels=vc.index,
            colors=[CITY_COLORS.get(c,"#95A5A6") for c in vc.index],
            autopct="%1.0f%%",startangle=90,
            wedgeprops={"edgecolor":"white","linewidth":1.5},textprops={"fontsize":10})
axes[0].set_title(f"Videos by City (n={len(videos_clean)})",fontsize=11,fontweight="bold")
dc=videos_clean["duration_label"].value_counts()
axes[1].bar(dc.index,dc.values,color=PALETTE[:len(dc)],edgecolor="white",zorder=2,width=0.4)
for i,(k,v) in enumerate(dc.items()):
    axes[1].text(i,v+0.05,str(v),ha="center",va="bottom",fontsize=11,fontweight="bold")
style_ax(axes[1],"Videos by Duration Category","","Count"); axes[1].set_ylim(0,dc.max()+2)
plt.tight_layout(); savefig(fig,"fig_18_videos_city_duration.png")

# ── Fig 19 – Radar chart ──────────────────────────────────────────────────────
print("  [5F] City comparison charts …")
labs_r=["News\nVolume","Social\nVolume","Suitability\nScore",
        "Social\nSentiment","Images\nCount","Videos\nCount"]
lr=city_metrics[city_metrics["city"]=="Lahore"].iloc[0]
pr=city_metrics[city_metrics["city"]=="Rawalpindi"].iloc[0]
keys=["news_volume","social_volume","suitability_mean","sentiment_social_mean","images_count","videos_count"]
def norm_val(v,mn,mx): return 0.5 if mx==mn else (v-mn)/(mx-mn)
raw_l=[lr[k] for k in keys]; raw_p=[pr[k] for k in keys]
maxs=[max(a,b) for a,b in zip(raw_l,raw_p)]; mins=[min(a,b) for a,b in zip(raw_l,raw_p)]
ln=[norm_val(v,mn,mx) for v,mn,mx in zip(raw_l,mins,maxs)]
pn=[norm_val(v,mn,mx) for v,mn,mx in zip(raw_p,mins,maxs)]
N=len(labs_r); angles=[n/float(N)*2*np.pi for n in range(N)]; angles+=angles[:1]
ln+=ln[:1]; pn+=pn[:1]
fig,ax=plt.subplots(figsize=(8,8),subplot_kw={"polar":True},facecolor="white")
ax.plot(angles,ln,linewidth=2,color=CITY_COLORS["Lahore"],label="Lahore")
ax.fill(angles,ln,alpha=0.2,color=CITY_COLORS["Lahore"])
ax.plot(angles,pn,linewidth=2,color=CITY_COLORS["Rawalpindi"],label="Rawalpindi")
ax.fill(angles,pn,alpha=0.2,color=CITY_COLORS["Rawalpindi"])
ax.set_xticks(angles[:-1]); ax.set_xticklabels(labs_r,fontsize=10)
ax.set_yticks([]); ax.set_title("City Comparison: Normalised Indicators",fontsize=13,fontweight="bold",pad=20)
ax.legend(loc="upper right",bbox_to_anchor=(1.25,1.1),fontsize=10)
plt.tight_layout(); savefig(fig,"fig_19_city_comparison_radar.png")

# ── Fig 20 – Volume comparison bar ───────────────────────────────────────────
fig,ax=plt.subplots(figsize=(12,5),facecolor="white")
cols=["social_volume","news_volume","images_count","videos_count"]
labs=["Social Posts","News Articles","Images","Videos"]
x=np.arange(len(cols)); w=0.35
vl=[lr[m] for m in cols]; vp=[pr[m] for m in cols]
b1=ax.bar(x-w/2,vl,width=w,color=CITY_COLORS["Lahore"],label="Lahore",edgecolor="white",zorder=2)
b2=ax.bar(x+w/2,vp,width=w,color=CITY_COLORS["Rawalpindi"],label="Rawalpindi",edgecolor="white",zorder=2)
for b in list(b1)+list(b2):
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.2,
            str(int(b.get_height())),ha="center",va="bottom",fontsize=10,fontweight="bold")
style_ax(ax,"City Comparison: Media Coverage Volumes","Metric","Count")
ax.set_xticks(x); ax.set_xticklabels(labs,fontsize=10); ax.legend(fontsize=10)
plt.tight_layout(); savefig(fig,"fig_20_city_comparison_volumes.png")

# ── Fig 21 – Lahore dual-axis: volume vs incidents ────────────────────────────
ld=city_day_metrics[city_day_metrics["city"]=="Lahore"].copy()
ld["label"]=pd.to_datetime(ld["date"]).dt.strftime("%b %d")
fig,ax1=plt.subplots(figsize=(9,5),facecolor="white")
ax2=ax1.twinx(); x=np.arange(len(ld))
ax1.bar(x-0.15,ld["social_volume"],width=0.25,color=CITY_COLORS["Lahore"],label="Social Posts",edgecolor="white",zorder=2)
ax1.bar(x+0.15,ld["news_volume"],  width=0.25,color="#5DADE2",label="News Articles",edgecolor="white",zorder=2)
ax2.plot(x,ld["incident_count"],marker="D",color="#C0392B",linewidth=2.5,markersize=8,label="Incidents",zorder=3)
for i,row in ld.iterrows():
    ax2.annotate(int(row["incident_count"]),
                 (list(ld.index).index(i),row["incident_count"]),
                 textcoords="offset points",xytext=(0,8),ha="center",fontsize=9,color="#C0392B")
ax1.set_xticks(x); ax1.set_xticklabels(ld["label"])
ax1.set_ylabel("Content Volume",color=CITY_COLORS["Lahore"],fontsize=10)
ax2.set_ylabel("Incident Count",color="#C0392B",fontsize=10)
ax1.tick_params(axis="y",colors=CITY_COLORS["Lahore"])
ax2.tick_params(axis="y",colors="#C0392B")
ax1.set_title("Lahore: Daily Content Volume vs Incident Count",fontsize=13,fontweight="bold")
ax1.grid(axis="y",color="#EEEEEE")
l1,lb1=ax1.get_legend_handles_labels(); l2,lb2=ax2.get_legend_handles_labels()
ax1.legend(l1+l2,lb1+lb2,loc="upper left",fontsize=9)
plt.tight_layout(); savefig(fig,"fig_21_lahore_volume_vs_incidents.png")

# ── Fig 22 – Sentiment heatmap ────────────────────────────────────────────────
sd2=pd.DataFrame({"Metric":["News Sentiment","Social Sentiment"],
                  "Lahore":[lr["sentiment_news_mean"],lr["sentiment_social_mean"]],
                  "Rawalpindi":[pr["sentiment_news_mean"],pr["sentiment_social_mean"]]})
sd2=sd2.set_index("Metric")
fig,ax=plt.subplots(figsize=(7,3),facecolor="white")
sns.heatmap(sd2,ax=ax,annot=True,fmt=".3f",cmap="RdYlGn",center=0,vmin=-1,vmax=1,
            linewidths=1,linecolor="white",annot_kws={"size":13,"weight":"bold"},
            cbar_kws={"label":"Sentiment Score"})
ax.set_title("Sentiment Comparison: News vs Social by City",**FONT_TITLE)
plt.tight_layout(); savefig(fig,"fig_22_sentiment_heatmap.png")

# ── Fig 23 – Cross-modal: suitability vs incidents ───────────────────────────
print("  [5G] Bonus cross-modal charts …")
fig,ax=plt.subplots(figsize=(9,5),facecolor="white")
for _,row in city_day_metrics.iterrows():
    color=CITY_COLORS.get(row["city"],"#666")
    ax.scatter(row["suitability_score"],row["incident_count"],color=color,s=120,zorder=3,edgecolors="white")
    ax.annotate(f"{row['city']}\n{row['date'][5:]}",
                (row["suitability_score"],row["incident_count"]),
                textcoords="offset points",xytext=(6,4),fontsize=8,color=color)
style_ax(ax,"Cross-Modal: Weather Suitability vs Incident Count per City-Day",
         "Suitability Score (0–100)","Incident Count")
patches=[mpatches.Patch(color=CITY_COLORS[c],label=c) for c in CITIES]
ax.legend(handles=patches,fontsize=9); ax.set_xlim(90,110); ax.grid(True,color="#EEEEEE")
plt.tight_layout(); savefig(fig,"fig_23_xmodal_suitability_vs_incidents.png")

# ── Fig 24 – Modality distribution in master index ────────────────────────────
master=pd.read_csv(os.path.join(PROCESSED,"master_index.csv"))
mc=master["modality"].value_counts()
fig,axes=plt.subplots(1,2,figsize=(12,5),facecolor="white")
fig.suptitle("Multimodal Integration Overview",fontsize=14,fontweight="bold")
axes[0].pie(mc.values,labels=mc.index,colors=PALETTE[:len(mc)],autopct="%1.0f%%",startangle=120,
            wedgeprops={"edgecolor":"white","linewidth":1.5},textprops={"fontsize":10})
axes[0].set_title(f"Records by Modality (n={len(master)})",fontsize=11,fontweight="bold")
mcp=master.groupby(["modality","city"]).size().unstack(fill_value=0)
mcp.plot(kind="bar",ax=axes[1],color=[CITY_COLORS["Lahore"],CITY_COLORS["Rawalpindi"]],edgecolor="white",zorder=2)
style_ax(axes[1],"Records by Modality and City","Modality","Record Count")
axes[1].legend(title="City",fontsize=9); axes[1].tick_params(axis="x",rotation=30)
plt.tight_layout(); savefig(fig,"fig_24_master_index_overview.png")

# ── Fig 25 – News vs Social volume scatter ────────────────────────────────────
fig,ax=plt.subplots(figsize=(10,5),facecolor="white")
for city,grp in city_day_metrics.groupby("city"):
    ax.scatter(grp["news_volume"],grp["social_volume"],
               color=CITY_COLORS[city],s=200,zorder=3,edgecolors="white",linewidth=1.5,label=city)
    for _,row in grp.iterrows():
        ax.annotate(row["date"][5:],(row["news_volume"],row["social_volume"]),
                    textcoords="offset points",xytext=(6,4),fontsize=8,color=CITY_COLORS[city])
style_ax(ax,"Cross-Modal: Daily News Volume vs Social Volume","News Articles","Social Posts")
ax.legend(fontsize=10); ax.grid(True,color="#EEEEEE")
plt.tight_layout(); savefig(fig,"fig_25_xmodal_news_vs_social.png")

# ── Fig 26 – QC summary chart ─────────────────────────────────────────────────
print("  [5H] QC summary chart …")
qc_df=pd.DataFrame(qc_records)
ACTION_COL={"pass":"#2ECC71","flag":"#F39C12","drop":"#E74C3C",
            "average":"#3498DB","flag-drop":"#E67E22"}
colors=[ACTION_COL.get(a.split("-")[0],"#95A5A6") for a in qc_df["action"]]
fig,ax=plt.subplots(figsize=(10,6),facecolor="white")
ax.barh(qc_df["check_id"][::-1],qc_df["n_before"][::-1],
        color=colors[::-1],edgecolor="white",height=0.6,zorder=2)
style_ax(ax,f"Quality Control: {len(qc_df)} Checks Across All Modalities","Records Before Check","Check ID")
patches=[mpatches.Patch(color=v,label=k) for k,v in ACTION_COL.items()]
ax.legend(handles=patches,fontsize=9,title="Action",bbox_to_anchor=(1.01,1),loc="upper left")
plt.tight_layout(); savefig(fig,"fig_26_qc_summary.png")

charts=sorted(os.listdir(REPORTS))
print(f"\n  {len(charts)} charts saved to reports/")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 6 │ OUTPUTS — write all CSVs + bonus integration package
# ══════════════════════════════════════════════════════════════════════════════
print("\n──────────────────────────────────────────────────────")
print("  STAGE 6 │ OUTPUTS")
print("──────────────────────────────────────────────────────")

# ── Core processed CSVs ───────────────────────────────────────────────────────
news_clean.to_csv(   os.path.join(PROCESSED,"news_clean.csv"),      index=False)
social_clean.to_csv( os.path.join(PROCESSED,"social_clean.csv"),    index=False)
weather_clean.to_csv(os.path.join(PROCESSED,"weather_clean.csv"),   index=False)
inc_clean.to_csv(    os.path.join(PROCESSED,"incidents_clean.csv"), index=False)
images_clean.to_csv( os.path.join(PROCESSED,"images_labels.csv"),   index=False)
videos_clean.to_csv( os.path.join(PROCESSED,"videos_clean.csv"),    index=False)
city_metrics.to_csv( os.path.join(PROCESSED,"city_metrics.csv"),    index=False)

# ── QC summary ────────────────────────────────────────────────────────────────
qc_df.to_csv(os.path.join(PROCESSED,"qc_summary.csv"), index=False)
print(f"  QC: {(qc_df['action']=='pass').sum()} pass  |  "
      f"{qc_df['action'].str.contains('flag').sum()} flag  |  "
      f"{(~qc_df['action'].isin(['pass','flag'])).sum()} fix/average")

# ── Bonus: master_index ───────────────────────────────────────────────────────
def make_master_index():
    rows = []
    for _,r in news_clean.iterrows():
        rows.append({"record_id":f"N_{r['outlet'][:3].upper()}_{r['date'].strftime('%Y%m%d')}_{r.name}",
                     "modality":"news","city":r["city"],"date":r["date"].strftime("%Y-%m-%d"),
                     "source_ref":r["url"],"text_field":r["headline"]})
    for _,r in social_clean.iterrows():
        rows.append({"record_id":f"S_{r['platform'][:3].upper()}_{r['date'].strftime('%Y%m%d')}_{r.name}",
                     "modality":"social","city":r["city"],"date":r["date"].strftime("%Y-%m-%d"),
                     "source_ref":r["url"],"text_field":str(r["caption"])[:80]})
    for _,r in inc_clean.iterrows():
        rows.append({"record_id":f"I_{r['city'][:3].upper()}_{r['date'].strftime('%Y%m%d')}_{r.name}",
                     "modality":"incident","city":r["city"],"date":r["date"].strftime("%Y-%m-%d"),
                     "source_ref":r["url"],"text_field":r["incident_type"]})
    for _,r in weather_clean.iterrows():
        rows.append({"record_id":f"W_{r['city'][:3].upper()}_{r['date'].strftime('%Y%m%d')}",
                     "modality":"weather","city":r["city"],"date":r["date"].strftime("%Y-%m-%d"),
                     "source_ref":r["sources"],
                     "text_field":f"temp={r['temperature']} wind={r['wind_speed']} suit={r['suitability_score']}"})
    for _,r in images_clean.iterrows():
        rows.append({"record_id":f"M_{r['image_id']}","modality":"image","city":r["city"],
                     "date":r["date_of_event"].strftime("%Y-%m-%d") if pd.notna(r["date_of_event"]) else "",
                     "source_ref":r["image_url"],"text_field":f"crowd={r['crowd_level']} kite={r['kite_presence']}"})
    for _,r in videos_clean.iterrows():
        rows.append({"record_id":f"V_{r['video_id']}","modality":"video","city":r["city"],
                     "date":r["date_of_event"].strftime("%Y-%m-%d") if pd.notna(r["date_of_event"]) else "",
                     "source_ref":r["url"],"text_field":str(r["caption"])[:80]})
    return pd.DataFrame(rows)

master_index=make_master_index()
master_index.to_csv(os.path.join(PROCESSED,"master_index.csv"),index=False)

# ── Bonus: item_features ──────────────────────────────────────────────────────
def make_item_features():
    rows=[]
    for _,r in news_clean.iterrows():
        rows.append({"record_id":f"N_{r['outlet'][:3].upper()}_{r['date'].strftime('%Y%m%d')}_{r.name}",
                     "modality":"news","city":r["city"],"date":r["date"].strftime("%Y-%m-%d"),
                     "sentiment_score":r["sentiment_score"],"sentiment_label":r["sentiment_label"],
                     "volume_day":r["news_volume_day"],"crowd_level":np.nan,"kite_presence":np.nan,
                     "suitability":np.nan,"incident_count":np.nan})
    for _,r in social_clean.iterrows():
        rows.append({"record_id":f"S_{r['platform'][:3].upper()}_{r['date'].strftime('%Y%m%d')}_{r.name}",
                     "modality":"social","city":r["city"],"date":r["date"].strftime("%Y-%m-%d"),
                     "sentiment_score":r["sentiment_score"],"sentiment_label":r["sentiment_label"],
                     "volume_day":r["social_volume_day"],"crowd_level":np.nan,"kite_presence":np.nan,
                     "suitability":np.nan,"incident_count":np.nan})
    for _,r in images_clean.iterrows():
        rows.append({"record_id":f"M_{r['image_id']}","modality":"image","city":r["city"],
                     "date":r["date_of_event"].strftime("%Y-%m-%d") if pd.notna(r["date_of_event"]) else "",
                     "sentiment_score":np.nan,"sentiment_label":np.nan,"volume_day":np.nan,
                     "crowd_level":r["crowd_level"],"kite_presence":r["kite_presence"],
                     "suitability":np.nan,"incident_count":np.nan})
    return pd.DataFrame(rows)

item_features=make_item_features()
item_features.to_csv(os.path.join(PROCESSED,"item_features.csv"),index=False)

# ── Bonus: city_day_metrics ───────────────────────────────────────────────────
city_day_metrics.to_csv(os.path.join(PROCESSED,"city_day_metrics.csv"),index=False)

# ── Final manifest ────────────────────────────────────────────────────────────
print("\n  OUTPUT FILES:")
print(f"  {'File':<35} {'Rows':>6} {'Size':>8}")
print(f"  {'─'*35} {'─'*6} {'─'*8}")
for f in sorted(os.listdir(PROCESSED)):
    fpath=os.path.join(PROCESSED,f)
    try:
        nrows=len(pd.read_csv(fpath)) if f.endswith(".csv") else "–"
    except Exception:
        nrows="–"
    kb=os.path.getsize(fpath)//1024
    print(f"  {f:<35} {str(nrows):>6} {str(kb)+' KB':>8}")

print(f"\n  REPORTS ({len(charts)} charts):")
for c in charts:
    kb=os.path.getsize(os.path.join(REPORTS,c))//1024
    print(f"    {c:<45} {str(kb)+' KB':>7}")

print("\n══════════════════════════════════════════════════════")
print("    PIPELINE COMPLETE — all stages finished")
print("══════════════════════════════════════════════════════")
print(f"\n  City Comparison Summary:")
print(city_metrics.to_string(index=False))
