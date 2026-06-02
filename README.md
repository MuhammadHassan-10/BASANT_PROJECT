# Basant Event Analysis – Multimodal Dataset Documentation
## DS 401: Introduction to Data Science | BSDS 02 Spring 2026 | Mega Assignment

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Team and Scope Decisions](#2-team-and-scope-decisions)
3. [Date Window Justification](#3-date-window-justification)
4. [Data Collection Overview](#4-data-collection-overview)
5. [Modality 1: News](#5-modality-1-news)
6. [Modality 2: Social Media](#6-modality-2-social-media)
7. [Modality 3: Weather](#7-modality-3-weather)
8. [Modality 4: Incidents](#8-modality-4-incidents)
9. [Modality 5: Images](#9-modality-5-images)
10. [Modality 6: Videos](#10-modality-6-videos)
11. [Preprocessing and Quality Control](#11-preprocessing-and-quality-control)
12. [Feature Engineering](#12-feature-engineering)
13. [City Comparison Methodology](#13-city-comparison-methodology)
14. [Inclusion and Exclusion Rules](#14-inclusion-and-exclusion-rules)
15. [Sampling Bias and Limitations](#15-sampling-bias-and-limitations)
16. [Ethics Statement](#16-ethics-statement)
17. [File Index](#17-file-index)
18. [Reproducibility Instructions](#18-reproducibility-instructions)
19. [Keyword and Search Strategy](#19-keyword-and-search-strategy)
20. [Source Quality Assessment](#20-source-quality-assessment)

---

## 1. Project Overview

This dataset package supports the **Basant Event Analysis** case study for DS 401 (Introduction to Data Science). Basant is a historically significant spring kite-flying festival celebrated across Punjab, Pakistan. After nearly two decades of a government ban, Basant was officially revived in **Lahore in February 2026**, while **Rawalpindi** saw unofficial celebrations that were met with a police crackdown.

The dataset integrates six modalities — news articles, social media posts, weather records, incident reports, images, and video metadata — to produce evidence-based indicators of celebration intensity, public safety, weather suitability, and sentiment across two Pakistani cities.

**Research Questions Addressed:**

- How did Basant 2026 differ in scale and intensity between Lahore and Rawalpindi?
- What weather conditions prevailed during the festival and how suitable were they for kite flying?
- What types of incidents were reported and how did their frequency compare between cities?
- How did public sentiment differ between the two cities on social media vs. in news coverage?
- Can multimodal signals be integrated into a coherent cross-modal picture of the event?

---

## 2. Team and Scope Decisions

**Cities selected:** Lahore, Rawalpindi  
**Rationale:** Lahore was the primary official venue for Basant 2026, representing state-sanctioned celebration. Rawalpindi was selected as a comparative city where celebrations happened informally and were subject to enforcement, providing a contrasting policy and safety context. This city pairing enables an evidence-based comparison across different regulatory environments.

**Minimum sample compliance:**

| Modality  | Required | Collected |
|-----------|----------|-----------|
| News      | ≥15      | 28        |
| Social    | ≥30      | 30        |
| Weather   | ≥3 days × 2 cities | 6 city-days (3 per city) |
| Incidents | From reputable sources | 23 records |
| Images    | ≥20      | 22        |
| Videos    | ≥10      | 12        |

All minimum sample requirements from the assignment specification are met or exceeded.

---

## 3. Date Window Justification

### Lahore: February 6–8, 2026 (3 days)

The Government of Punjab officially approved Basant celebrations in Lahore for the period **6–8 February 2026**. This window was selected because:

- It represents the only officially sanctioned kite-flying period in Lahore after a ~25-year ban.
- News coverage confirming the official window was found in multiple credible outlets (Dawn, Geo News, Reuters, AP News) dated between February 2–5, 2026, ahead of the festival.
- Weather data from open-meteo.com and visualcrossing.com was collected specifically for these three dates in Lahore.
- Social media posts, images, and videos from this window were collected in support of celebration intensity analysis.

Pre-window content (e.g., anticipatory social posts from late January/early February) was collected as contextual data and is flagged in the `in_analysis_window` column of `social_clean.csv`.

### Rawalpindi: February 13–15, 2026 (3 days)

Rawalpindi was subject to a government ban on Basant celebrations. However, informal celebrations were reported in news articles from **February 13–15, 2026**. This window was selected because:

- News reporting (Dawn, Express Tribune, ProPakistani) confirms kite-flying took place in Rawalpindi on February 13–14, 2026, despite the ban.
- Police crackdown and arrest data is concentrated in this window.
- Social media posts from February 12–15 reflect crowd activity in Rawalpindi.
- Weather data was obtained for February 13–15 in Rawalpindi to assess conditions during the informal celebrations.

**Note on Rawalpindi's status:** Rawalpindi celebrations were unsanctioned. This distinction is preserved throughout the dataset in contextual fields and the city comparison table.

---

## 4. Data Collection Overview

All data was collected between **January 2026 and February 2026** using manual web research, Google searches, and direct access to public social media platforms. No private data, login-gated content, or scraping tools were used. Each record includes a URL pointing to the original public source.

**Collection approach by modality:**

| Modality  | Primary Method | Tools Used |
|-----------|---------------|------------|
| News      | Manual Google News search; direct outlet browsing | Browser, Google News |
| Social    | Manual platform browsing (Facebook, Instagram, Twitter/X) | Platform search |
| Weather   | API/website queries for historical weather | open-meteo.com, visualcrossing.com |
| Incidents | Systematic news search with safety/accident keywords | Google News, outlet archives |
| Images    | Manual image collection from news articles | Browser |
| Videos    | Manual video search; metadata recorded, files not downloaded | YouTube, Urdupoint |

**Languages encountered:** English, Urdu, Roman Urdu (transliterated Urdu in Latin script). Sentiment analysis is primarily English-based; Urdu/Roman Urdu limitations are documented in Section 11.

---

## 5. Modality 1: News

### Raw File: `data/raw/news.csv` 
### Cleaned File: `data/processed/news_clean.csv`

**Fields in raw file:**

| Field    | Description |
|----------|-------------|
| outlet   | Name of the news outlet (e.g., Dawn, Geo News, AP News) |
| date     | Publication date as Excel date serial number |
| city     | City primarily referenced in the article |
| url      | Direct URL to the article |
| headline | Article headline |
| snippet  | Short excerpt or summary of article content |

**Sources used:**

| Outlet           | Country/Origin | Coverage Type        |
|------------------|----------------|----------------------|
| Dawn             | Pakistan       | National broadsheet  |
| Express Tribune  | Pakistan       | English daily        |
| Geo News         | Pakistan       | Broadcast/digital    |
| Al Jazeera       | Qatar (intl.)  | International coverage |
| Gulf News        | UAE            | International        |
| Reuters          | UK (intl.)     | Wire service         |
| AP News          | USA (intl.)    | Wire service         |
| Pakistan Today   | Pakistan       | English daily        |
| Daily Pakistan   | Pakistan       | English daily        |
| Daily Ittehad    | Pakistan       | Urdu/English         |
| ProPakistani     | Pakistan       | Tech/news blog       |
| PakWheels Blog   | Pakistan       | Automotive/news blog |

**Collection method:**
1. Google News searched with queries: `"Basant 2026" Lahore`, `"Basant 2026" Rawalpindi`, `"Basant festival" Pakistan 2026`, `kite flying Lahore 2026 injuries`, `Rawalpindi Basant ban 2026`.
2. Date filter applied: January 2026 – February 2026.
3. Articles were manually reviewed to confirm relevance (direct mention of Basant 2026 + city reference).
4. Headlines and snippets were manually transcribed or copy-pasted from article previews.

**Inclusion rules:**
- Article must mention Basant 2026 explicitly.
- Article must reference one of the two study cities (Lahore or Rawalpindi).
- Article must be dated within or near the study windows.
- English-language articles preferred; Urdu articles excluded from sentiment analysis but noted.

**Exclusion rules:**
- Opinion columns without factual content excluded.
- Paywalled articles excluded if snippet was insufficient.
- Articles solely about historical Basant (pre-2026) excluded.

**Date encoding note:** Dates in the raw file were stored as Excel date serial integers (e.g., `46059` = February 6, 2026). The pipeline converts these to ISO-format timestamps using the Excel epoch (December 30, 1899).

**Preprocessing applied:**
- Date parsed from Excel serial to `pd.Timestamp`.
- City names normalised to standard forms.
- Duplicate URLs removed (none found in this dataset).
- Text fields stripped of whitespace and collapsed multiple spaces.
- Sentiment score computed on combined `headline + snippet` text.

---

## 6. Modality 2: Social Media

### Raw File: `data/raw/social.csv`
### Cleaned File: `data/processed/social_clean.csv`

**Fields in raw file:**

| Field    | Description |
|----------|-------------|
| platform | Social media platform (Facebook, Instagram, Twitter/X) |
| date     | Date of post (ISO format YYYY-MM-DD) |
| city     | City tagged or referenced in post |
| url      | Public URL to the post |
| caption  | Post caption/text |
| hashtags | Hashtags included in post |

**Platforms covered:**

| Platform   | Posts | City Coverage |
|------------|-------|---------------|
| Facebook   | 16    | Lahore (11), Rawalpindi (5) |
| Instagram  | 10    | Lahore (7), Rawalpindi (4) |  
| Twitter/X  | 4     | Lahore (3), Rawalpindi (1) |

**Collection method:**
1. Platform-native search bars used with queries: `#Basant2026`, `#BasantLahore`, `#RawalpindiBasant`, `Basant 2026 Lahore`, `Pindi Basant 2026`.
2. Posts were browsed manually. Only publicly visible posts (no login required to view) were included.
3. Captions and hashtags were manually transcribed.
4. For Facebook, only posts shared via public links (`/share/` URLs) or from public pages were included.
5. For Instagram, only public reels/posts accessible without login via direct reel links were collected.

**Inclusion rules:**
- Post must be publicly accessible without account login.
- Post must reference Basant or kite flying in the context of the 2026 festival.
- Post must be tagged to or clearly reference one of the two study cities.
- Only original posts included (reposts/shares not counted separately if they share a URL).

**Exclusion rules:**
- Private group posts excluded.
- Posts requiring login to view excluded.
- Posts not clearly attributable to a city excluded.
- Commercial promotional posts not related to festival experience excluded (though safety/aviation notices from official pages are retained as they reflect Basant-related activity).

**Analysis window flagging:** 7 posts fall outside the core analysis window (before Feb 6 for Lahore, or after Feb 15 for Rawalpindi). These posts are flagged with `in_analysis_window = False` and retained for contextual analysis but excluded from volume counts in the city comparison table.

**Language note:** Several captions are in Urdu or Roman Urdu (e.g., "Pindi Basant 2026 seen (A)", "Lahore ke Manazir"). The English keyword-based sentiment lexicon has limited coverage for these posts. They are included in the dataset but sentiment scores for non-English captions should be interpreted with caution. The `sentiment_label` for Urdu-dominant captions typically defaults to `neutral` (score = 0.0) because the lexicon does not match Urdu tokens.

---

## 7. Modality 3: Weather

### Raw File: `data/raw/weather.csv`
### Cleaned File: `data/processed/weather_clean.csv`

**Fields in raw file:**

| Field        | Description |
|--------------|-------------|
| date         | Date (M/D/YYYY format) |
| city         | City name |
| temperature  | Mean daily temperature in degrees Celsius |
| wind_speed   | Mean daily wind speed in km/h |
| precipitation| Total daily precipitation in mm |
| source       | Data provider name |

**Data sources:**

| Source              | URL                    | Data Type |
|---------------------|------------------------|-----------|
| open-meteo.com      | https://open-meteo.com | Historical hourly weather API (free, no API key required) |
| visualcrossing.com  | https://www.visualcrossing.com | Historical weather API (free tier) |

**Collection method:**
1. Both sources queried for daily averages (temperature, wind speed) and total precipitation.
2. Lahore coordinates: 31.5497° N, 74.3436° E.
3. Rawalpindi coordinates: 33.5651° N, 73.0169° E.
4. Query period: Feb 6–8 2026 (Lahore) and Feb 13–15 2026 (Rawalpindi).
5. Data manually entered into the CSV after reviewing API responses.

**Dual-source design rationale:** Two independent sources were queried per city per day to enable cross-validation. The pipeline averages the two readings into a single canonical value per city/date, stored in `weather_clean.csv`. The individual source readings are kept in `data/raw/weather.csv`.

**Weather Suitability Score (0–100):**

The suitability score is a rule-based composite index designed to quantify how favourable conditions were for outdoor kite flying. The scoring rubric is:

| Component    | Condition                     | Score |
|--------------|-------------------------------|-------|
| Temperature  | 10–25 °C (optimal range)      | +40   |
| Temperature  | 5–10 °C or 25–30 °C (marginal)| +20   |
| Temperature  | Outside 5–30 °C (extreme)     | +0    |
| Wind speed   | 5–25 km/h (flyable breeze)    | +40   |
| Wind speed   | 2–5 km/h (light, still flyable)| +20  |
| Wind speed   | <2 or >25 km/h (too calm or too strong) | +0 |
| Precipitation| 0 mm (dry)                    | +20   |
| Precipitation| Any rain                      | +0    |
| **Maximum total** |                          | **100** |

**Threshold justification:**
- Temperature range 10–25°C is consistent with comfortable outdoor activity for kite-flyers and spectators in Punjab's winter/spring transition.
- Wind speed 5–25 km/h (Beaufort Scale 2–5, Light Breeze to Fresh Breeze) is the ideal range for kite flying; below 5 km/h kites struggle to stay aloft, above 25 km/h string control becomes hazardous.
- Precipitation = 0: any rain renders kite string (especially metal-infused dor) dangerous and grounds kites.

---

## 8. Modality 4: Incidents

### Raw File: `data/raw/incidents.csv`
### Cleaned File: `data/processed/incidents_clean.csv`

**Fields in raw file:**

| Field        | Description |
|--------------|-------------|
| date         | Date of incident (Excel serial) |
| city         | City where incident occurred |
| incident_type| Type of incident (free text) |
| count        | Number of reported cases |
| severity     | Severity level (fatal/severe/moderate/low/high) |
| source_type  | Source category (Official/Media/Social claim) |
| url          | Source URL |
| description  | Brief description of the incident |

**Sources used:**

| Source         | Source Type | Notes |
|----------------|-------------|-------|
| Dawn           | Media       | Pakistan's most-circulated English broadsheet |
| Geo News       | Media       | Major broadcast news network |
| Express Tribune| Media       | English-language daily with strong Lahore bureau |
| Pakistan Today | Media       | English daily |
| ProPakistani   | Media       | Digital news outlet covering Pakistan |
| PakWheels Blog | Media       | Automotive/safety news; motorcyclist injury coverage |
| High Court records (via news reporting) | Official | Court-confirmed death figures |
| Punjab Police (via news reporting)       | Official | Arrest and seizure counts |

**Collection method:**
1. Google News searched with queries: `Basant 2026 death injury Lahore`, `Basant 2026 arrest Rawalpindi`, `kite string injury 2026`, `Basant electrocution Pakistan 2026`, `Rawalpindi kite crackdown 2026`.
2. Each news article was reviewed. Incident records were extracted from articles that contained specific counts (number of injured, arrested, etc.).
3. Each extracted record was assigned a `source_type`:
   - **Official**: Data attributed to government agencies, police, hospitals, or courts.
   - **Media**: Data reported by journalists without citing an official body, or from eyewitness accounts.
   - **Social claim**: Data sourced from social media without official corroboration (none included in this dataset after review).

**Deduplication rule applied:**
The same incident reported by multiple outlets was counted only once. Deduplication was performed by checking for identical (date, city, incident_type, url) tuples. Where the same underlying event appeared in multiple articles from different URLs, the record was retained in the dataset but flagged with `cross_source_dup = True`. Analysts should exercise caution when summing counts across rows with `cross_source_dup = True` to avoid double-counting.

**Incident Taxonomy:**

| Raw Incident Type            | Assigned Category     | Description |
|------------------------------|-----------------------|-------------|
| death, electrocution         | fatality              | Deaths directly attributable to Basant activity |
| injury, kite_string_injury, rooftop_fall, gunfire_injury | physical_injury | Non-fatal physical harm |
| arrest, seizure              | law_enforcement       | Police enforcement actions |
| traffic, public_transport_incident | infrastructure  | Disruptions to movement/transport |
| total_accidents, death_total | aggregate_report      | Summary statistics reported by authorities (not double-counted in individual totals) |

**Important note on aggregate records:** Rows with `incident_type = total_accidents` or `death_total` are **aggregate government reports** (e.g., "118 total accidents in two days"). These are retained for reference but are excluded from per-incident-type summations in `city_metrics.csv` to avoid double-counting with the individual incident rows.

---

## 9. Modality 5: Images

### Raw File: `data/raw/images.csv` 
### Cleaned File: `data/processed/images_labels.csv`

**Fields in raw file:**

| Field         | Description |
|---------------|-------------|
| image_id      | Unique identifier (IMG001–IMG022) |
| image_url     | Direct URL to the image file |
| page_url      | URL of the page where image appeared |
| source        | News outlet or platform that published the image |
| date_of_event | Date image relates to |
| city          | City depicted |

**Image sources:**

| Source           | Images | City |
|------------------|--------|------|
| AP News          | 5      | Lahore |
| Dawn News        | 3      | Lahore (2), Rawalpindi (1) |
| Geo News         | 2      | Lahore |
| Al Jazeera       | 2      | Lahore |
| Express Tribune  | 3      | Lahore (1), Rawalpindi (2) |
| Gulf News        | 1      | Lahore |
| Arab News        | 1      | Lahore |
| Daily Times      | 1      | Lahore |
| TRT World        | 1      | Lahore |
| PakWheels        | 1      | Lahore |
| Duniya News      | 1      | Lahore |
| 24 News          | 1      | Lahore |
| The News Intl.   | 1      | Lahore |

**Collection method:**
1. Image URLs were collected alongside news article collection. Each article was inspected for embedded images.
2. Images were recorded as metadata (URLs + source info) rather than downloaded, to comply with copyright considerations.
3. 22 unique images were collected (22 after cleaning, one duplicate row removed).

**Manual Labels assigned:**

| Label Field    | Values | Labelling Method |
|----------------|--------|-----------------|
| crowd_level    | low / medium / high / unknown | Rule-based proxy: major international wire service images from peak days = high; other images = medium; pre-festival = low |
| kite_presence  | yes / likely / unknown | URL-keyword heuristic: "kite" or "basant" in image URL = "yes"; all Basant-context images default to "likely" |
| time_of_day    | unknown | Cannot be determined from URLs alone; requires visual inspection |
| police_visible | unknown | Cannot be determined from URL metadata; requires visual inspection |

**Labelling limitations:** In the absence of image downloading or computer vision tools, `time_of_day` and `police_visible` fields could not be populated programmatically. These fields are included in the schema for completeness and would be filled via manual review in a full study. The `crowd_level` and `kite_presence` labels are systematic approximations, not manual visual codings.

**City distribution:** 17 images depict Lahore, 5 depict Rawalpindi. This imbalance reflects the skew in international media coverage toward Lahore as the site of the official Basant revival.

---

## 10. Modality 6: Videos

### Raw File: `data/raw/video_links.csv` 
### Cleaned File: `data/processed/videos_clean.csv`

**Fields in raw file:**

| Field           | Description |
|-----------------|-------------|
| video_id        | Unique identifier (VID001–VID012) |
| url             | Video URL |
| platform        | Platform (YouTube, Urdupoint, Facebook, etc.) |
| date_of_event   | Date video relates to |
| city            | City depicted |
| caption         | Video title/caption |
| duration_seconds| Video duration in seconds |
| views           | View count at time of collection |
| thumbnail_url   | URL to video thumbnail image |
| language        | Primary language of video |

**Platforms:**

| Platform  | Videos |
|-----------|--------|
| YouTube   | 7      |
| Urdupoint | 2      |
| Facebook  | 2      |
| Instagram | 1      |

**Collection method:**
1. YouTube searched with queries: `Basant 2026 Lahore`, `Pindi Basant 2026`, `Rawalpindi kite flying 2026`, `Basant festival Pakistan 2026`.
2. Videos were reviewed and metadata (title, views, duration, URL) manually recorded.
3. Video files were **not downloaded**. Only metadata was collected, consistent with the assignment's "metadata-only recommended" guidance for video modality.
4. Thumbnail URLs were derived from standard YouTube URL patterns where possible.

**Duration labels applied:**

| Label           | Criteria        | Count |
|-----------------|-----------------|-------|
| short (<1 min)  | <60 seconds     | varies |
| medium (1–5 min)| 60–299 seconds  | varies |
| long (>5 min)   | ≥300 seconds    | varies |

**Language distribution:** All 12 videos are in Urdu (as noted in the `language` field). Sentiment scores derived from English-language captions/titles are indicative but have the same Urdu-text limitation noted for social media.

---

## 11. Preprocessing and Quality Control

### Full QC Log Summary

The pipeline performs **21 documented quality checks** across all modalities. The complete log is exported to `data/processed/qc_summary.csv`. Key findings:

| Check ID | Modality  | Check Name                              | Flagged | Action   |
|----------|-----------|-----------------------------------------|---------|----------|
| QC-N1    | News      | Required columns present                | 0       | pass     |
| QC-N2    | News      | City values recognisable                | 0       | pass     |
| QC-N3    | News      | Date parse success                      | 0       | pass     |
| QC-N4    | News      | Duplicate URL check                     | 0       | pass     |
| QC-N5    | News      | Non-empty headline check                | 0       | flag     |
| QC-S1    | Social    | Minimum sample size (≥30 posts)         | 0       | pass     |
| QC-S2    | Social    | Date parse success                      | 0       | pass     |
| QC-S3    | Social    | Duplicate URL check                     | 0       | pass     |
| QC-S4    | Social    | Posts within analysis window            | 7       | flag     |
| QC-W1    | Weather   | Temperature numeric coercion            | 0       | pass     |
| QC-W2    | Weather   | Wind speed numeric coercion             | 0       | pass     |
| QC-W3    | Weather   | Duplicate city/date rows (two sources)  | 6       | average  |
| QC-W4    | Weather   | Suitability score in [0,100]            | 0       | pass     |
| QC-I1    | Incidents | Date parse success                      | 0       | pass     |
| QC-I2    | Incidents | Deduplication (same date/city/type/url) | 0       | pass     |
| QC-I3    | Incidents | Severity vocabulary validation          | 0       | pass     |
| QC-M1    | Images    | Minimum image sample (≥20)              | 0       | pass     |
| QC-M2    | Images    | Image URL present                       | 0       | pass     |
| QC-V1    | Videos    | Minimum video sample (≥10)              | 0       | pass     |
| QC-V2    | Videos    | Video URL present                       | 0       | pass     |
| QC-V3    | Videos    | Duplicate video_id                      | 0       | pass     |

**Notable QC findings:**

- **QC-S4 (7 flagged):** Seven social media posts fall outside the core 3-day analysis windows. These include anticipatory posts (e.g., January 6, February 2–5 for Lahore) and extended celebration posts (February 12, 14 for Rawalpindi). They are retained but flagged with `in_analysis_window = False`.
- **QC-W3 (6 averaged):** Weather data was collected from two independent sources (open-meteo.com and visualcrossing.com) for each city-day, resulting in duplicate rows in the raw file. The pipeline averages these into single canonical rows.
- **QC-N5 (pass, 0 flagged):** No empty headlines found; all 28 news records have valid headline text.

### Text Preprocessing Steps

All text fields (news headlines, snippets, social captions) underwent the following cleaning:

1. **Whitespace normalisation:** Multiple consecutive spaces collapsed to single space; leading/trailing spaces stripped.
2. **Character filtering (social captions):** Non-alphanumeric characters except `#@?,.-!'` removed to eliminate encoding artefacts (e.g., `????` emoji sequences that display as `?` in ASCII environments).
3. **Null handling:** NaN/null values in text fields replaced with empty string before processing; `headline_missing` flag set for any record with originally null/empty headline.

### Date Parsing

Three different date formats were encountered across modalities:

| Format              | Example      | Modalities         |
|---------------------|--------------|--------------------|
| Excel date serial   | `46059`      | News, Incidents    |
| US date string      | `2/6/2026`   | Weather            |
| ISO date string     | `2026-02-06` | Social, Videos, Images |

All dates were converted to `pd.Timestamp` objects and stored in ISO format (`YYYY-MM-DD`) in cleaned files.

### City Name Standardisation

City names were standardised via a mapping dictionary:

| Raw value       | Standardised |
|-----------------|--------------|
| lahore, Lahore  | Lahore       |
| rawalpindi, Rawalpindi, pindi, rwp | Rawalpindi |
| rawaklpindi (typo in one social post) | Rawalpindi |

---

## 12. Feature Engineering

### News
- `sentiment_score`: Lexicon-based score on `headline + snippet` text, range [−1, +1].
- `sentiment_label`: Categorical label (positive/neutral/negative) with thresholds ±0.1.
- `news_volume_day`: Count of news items per city per day.

### Social
- `hashtag_count`: Count of `#hashtag` patterns in cleaned hashtags field.
- `sentiment_score` / `sentiment_label`: Same lexicon applied to caption text.
- `social_volume_day`: Count of posts per city per day.
- `in_analysis_window`: Boolean flag indicating whether post falls within core 3-day window.

### Weather
- `temp_score`, `wind_score`, `precip_score`: Component scores (see rubric in Section 7).
- `suitability_score`: Sum of component scores (0–100).
- `suitability_label`: Categorical (excellent / good / fair / poor).

### Incidents
- `incident_category`: Higher-level taxonomy grouping raw incident types.
- `cross_source_dup`: Flag for rows sharing (date, city, incident_type) with another record from a different source — indicates potential double-counting risk.

### Images
- `crowd_level`: Rule-based proxy label (low / medium / high / unknown).
- `kite_presence`: URL-keyword derived label (yes / likely / unknown).

### Videos
- `duration_label`: Categorical duration range label.
- `sentiment_score` / `sentiment_label`: Lexicon applied to video caption.

---

## 13. City Comparison Methodology

The city-level comparison (`data/processed/city_metrics.csv`) aggregates the following indicators:

| Metric                   | Source          | Notes |
|--------------------------|-----------------|-------|
| social_volume            | social_clean    | Total posts collected (includes pre/post window) |
| news_volume              | news_clean      | Total news items in dataset |
| incidents_total          | incidents_clean | Sum of `count` for non-aggregate rows |
| fatal_incidents          | incidents_clean | Sum of `count` where severity = fatal |
| arrests                  | incidents_clean | Sum of `count` where category = law_enforcement |
| suitability_mean         | weather_clean   | Mean suitability score across analysis days |
| sentiment_news_mean      | news_clean      | Mean sentiment score across all news items |
| sentiment_social_mean    | social_clean    | Mean sentiment score across all social posts |
| images_count             | images_labels   | Number of images in dataset for city |
| videos_count             | videos_clean    | Number of videos in dataset for city |

**Caution on incidents comparison:** Rawalpindi's `incidents_total` is dominated by `seizure` count (4,245 kites seized) and `arrest` count (215 arrests). These law enforcement actions reflect a ban-enforcement context rather than festival-caused harm, and are not directly comparable to Lahore's injury/fatality counts. Analysts should compare incident categories separately rather than summing all incident counts.

---

## 14. Inclusion and Exclusion Rules

### Universal Rules (All Modalities)

**Include:**
- Content that explicitly references Basant 2026 in Pakistan.
- Content clearly attributable to Lahore or Rawalpindi.
- Publicly accessible content only.
- Content dated between January 1, 2026, and February 28, 2026.

**Exclude:**
- Content requiring account login or private group membership.
- Content about Basant festivals in India or other countries.
- Content clearly about historical Basant (pre-2026) without reference to the revival.
- Duplicate records (same content, same URL).
- Opinion/editorial pieces with no factual reporting (news modality only).

### Modality-Specific Rules

**News:**
- Minimum of one city name (Lahore/Rawalpindi) in headline or snippet required.
- At least one Basant-related keyword required: "basant", "kite", "festival", "kite-flying", "spring festival".

**Social:**
- Post must be from a public account or public page.
- At least one Basant hashtag or mention in caption required.
- Platform must be Facebook, Instagram, or Twitter/X.

**Weather:**
- Records must be from one of the two approved sources (open-meteo.com, visualcrossing.com).
- Data must correspond exactly to the study city and date window.

**Incidents:**
- Each incident must have a verifiable URL source.
- Source must be a named news outlet or official authority (not anonymous social claim).
- Aggregate summary statistics (e.g., "118 total accidents") retained but category-tagged separately.

**Images:**
- Image must be published by a named outlet (not anonymous upload).
- Image must be publicly viewable via direct URL without login.

**Videos:**
- Video must be publicly viewable without login.
- Metadata only collected (no file download).

---

## 15. Sampling Bias and Limitations

### Coverage Bias
- **Lahore overrepresented:** 23 of 28 news items and 17 of 22 images pertain to Lahore. This reflects the fact that Lahore was the site of the official Basant revival and received substantially more domestic and international media attention.
- **English-language bias in news:** All news outlets collected publish in English. Urdu-language reporting (e.g., from ARY News, Jang, Nawaiwaqt) was not included, which may underrepresent perspectives from Urdu-speaking audiences.
- **Social media platform bias:** Twitter/X is underrepresented (4 posts) relative to Facebook (16) and Instagram (10). This may reflect the public availability of posts on each platform rather than actual relative activity levels.

### Temporal Bias
- Rawalpindi's 3-day window (Feb 13–15) is one week after Lahore's (Feb 6–8), meaning the two cities were not observed in parallel. External events in the intervening week (e.g., news of Lahore fatalities reaching Rawalpindi before their own celebrations) may have influenced Rawalpindi sentiment.
- Post-window reporting (e.g., court scrutiny, final death toll confirmed on Feb 25) is included for Lahore to capture the full known incident count, but this creates an asymmetry in the temporal coverage of the two cities.

### Sentiment Analysis Limitations
- The keyword lexicon was constructed manually from English-language festival and incident vocabulary. It does not cover Roman Urdu or standard Urdu text.
- Sarcasm, irony, and cultural context cannot be captured by a simple lexicon-based approach.
- Short captions (e.g., "Lahore Basant") contain insufficient tokens for meaningful sentiment scoring and default to 0.0 (neutral).
- The same lexicon was applied to both news and social text; news language tends to be more formal and incident-focused, inherently scoring more negatively, which must be accounted for in cross-modality comparisons.

### Incident Count Limitations
- Media-reported injury counts may overlap with official counts. The `cross_source_dup` flag is designed to help analysts identify this, but cannot fully resolve double-counting without ground truth data.
- The 17 confirmed deaths in Lahore (from the Lahore High Court report on Feb 25) represent the authoritative final figure; earlier media reports cited lower counts and may undercount.
- Rawalpindi's incident data is limited: only 3 days of data were collected and enforcement actions (arrests/seizures) dominate, while injury reporting was sparse due to the unofficial nature of celebrations.

### Media Label Limitations
- Image labels (`crowd_level`, `kite_presence`, `time_of_day`, `police_visible`) were assigned programmatically rather than through human visual inspection. The `time_of_day` and `police_visible` fields could not be populated from URL metadata alone and remain `unknown`.
- Video sentiment scores are computed on English-language titles/captions despite all 12 videos being in Urdu.

---

## 16. Ethics Statement

### Privacy and Consent
- All social media posts collected are from **public accounts and public pages**. No private profiles, private groups, or direct messages were accessed.
- Usernames and account handles were not collected and are not present in any dataset file. Posts are identified only by their public URLs.
- No content requiring account login was collected.
- No demographic information about individual users was inferred or stored.

### Children and Vulnerable Populations
- No attempts were made to identify minors or vulnerable individuals in images or social content.
- Image and video labels focus on environmental/contextual attributes (crowd level, kite presence) rather than individual identification.

### Misinformation Risk
- All incident data was sourced from named, reputable news outlets or official government/police sources. Anonymous social media claims about injuries or deaths were excluded.
- The `source_type` field in `incidents_clean.csv` allows analysts to filter by source credibility level.
- Aggregate reports (e.g., "118 accidents in two days") are tagged as `aggregate_report` category and should not be combined with individual incident counts.

### Cultural Sensitivity
- Basant is a culturally and religiously significant festival for many communities in Punjab. This dataset analyses the festival objectively and does not make normative judgements about the festival itself, the government's decision to permit or ban it, or the communities that celebrate it.
- Incident data is presented factually with source citations and does not attribute blame to specific groups.

### Data Use Constraints
- This dataset was collected for educational purposes (DS 401 course assignment at NUST) and should not be used for commercial purposes, surveillance, or law enforcement applications.
- URL links in the dataset point to third-party content subject to the copyright and terms of service of the respective outlets and platforms.

---

## 17. File Index

### `data/raw/` — Unmodified source data

| Filename            | Format | Rows | Description |
|---------------------|--------|------|-------------|
| news.csv            | CSV    | 28   | Raw news articles (converted from news.xlsx) |
| news.xlsx           | CSV   | 28   | Original uploaded file |
| social.csv          | CSV    | 30   | Raw social media posts |
| weather.csv         | CSV    | 12   | Raw weather records (2 sources × 3 days × 2 cities) |
| incidents.csv       | CSV    | 23   | Raw incident records (converted from incidents.xlsx) |
| incidents.xlsx      | CSV  | 23   | Original uploaded file |
| images.csv          | CSV    | 22   | Raw image metadata (converted from images.xlsx) |
| images.xlsx         | CSV  | 26   | Original uploaded file (includes 2 header rows) |
| video_links.csv     | CSV    | 12   | Raw video metadata (converted from videos.xlsx) |
| videos.xlsx         | CSV   | 12   | Original uploaded file |

### `data/processed/` — Cleaned and enriched data

| Filename               | Format | Rows | Description |
|------------------------|--------|------|-------------|
| news_clean.csv         | CSV    | 28   | Cleaned news: standardised dates/cities, text cleaned, sentiment added |
| social_clean.csv       | CSV    | 30   | Cleaned social: standardised, sentiment, volume, window flag |
| weather_clean.csv      | CSV    | 6    | Averaged weather per city/day, suitability scores |
| incidents_clean.csv    | CSV    | 23   | Cleaned incidents: taxonomy, dedup flag, standardised dates |
| images_labels.csv      | CSV    | 22   | Image metadata with crowd_level, kite_presence labels |
| videos_clean.csv       | CSV    | 12   | Video metadata with sentiment and duration labels |
| city_metrics.csv       | CSV    | 2    | City-level comparison table (Lahore vs Rawalpindi) |
| qc_summary.csv         | CSV    | 21   | Log of all quality control checks |
| master_index.csv       | CSV    | 121  | **(Bonus)** Hub table linking all records across modalities |
| item_features.csv      | CSV    | 80   | **(Bonus)** Item-level feature table with joined attributes |
| city_day_metrics.csv   | CSV    | 6    | **(Bonus)** Aggregated signals per city per day |

### `pipeline.py` — Processing pipeline

Fully reproducible Python pipeline. Reads from `data/raw/`, writes to `data/processed/`. No external internet access required. All dependencies are from the Python standard library and common data science packages (pandas, numpy, openpyxl).

---

## 18. Reproducibility Instructions

### Requirements

```
pandas>=1.5.0
numpy>=1.21.0
openpyxl>=3.0.0
```

No internet access is required at runtime. The pipeline reads from local files only.

### Directory Structure 

```
basant_project/
├── pipeline.py
├── data/
│   ├── raw/
│   │   ├── news.csv       
│   │   ├── incidents.csv  
│   │   ├── images.csv 
│   │   ├── videos.csv      
│   │   ├── social.csv       
│   │   └── weather.csv       
│   └── processed/
│   │   ├── news_clean.csv       
│   │   ├── incidents_clean.csv   
│   │   ├── images_labels.csv     
│   │   ├── videos_clean.csv     
│   │   ├── social_clean.csv        
│   │   └── weather_clean.csv   
│   │   ├── qc_summary.csv       
│   │   ├── master_index.csv       
│   │   ├── item_features.csv        
│   │   └── city_metrices.csv 
│   │   └── city_day_metrices.csv      
└── reports/                  
```

### Running the Pipeline

```bash
cd basant_project/
python3 pipeline.py
```

The pipeline will:
1. Read all raw files from `data/raw/`.
2. Process each modality independently.
3. Write 11 cleaned/derived CSV files to `data/processed/`.
4. Print a QC summary and file manifest to stdout.

All output paths are relative to the script location. There are no hard-coded machine paths.

---

## 19. Keyword and Search Strategy

The following keyword sets were used to identify relevant content across modalities:

### Primary Keywords (English)
- `basant 2026`
- `basant festival lahore`
- `basant rawalpindi 2026`
- `kite flying pakistan 2026`
- `spring festival pakistan`
- `basant revival pakistan`

### Incident-Specific Keywords
- `basant injury death lahore 2026`
- `kite string injury motorcyclist`
- `basant electrocution 2026`
- `basant rooftop fall`
- `rawalpindi kite arrest ban 2026`
- `basant 2026 accidents reported`

### Social Media Hashtags
- `#Basant2026`
- `#BasantLahore`
- `#BasantFestival`
- `#RawalpindiBasant`
- `#PindiBasant`
- `#BasantNight2026`

### Roman Urdu / Urdu Keywords (for social search only)
- `pindi basant` (Rawalpindi Basant)
- `lahore basant` (Lahore Basant)
- `rang basant` (Colors of Basant)
- `khushi basant` (Joy of Basant)

---

## 20. Source Quality Assessment

Sources are rated on a three-tier scale:

**Tier 1 (High Confidence — Official or International Wire):**
- Reuters, AP News, Al Jazeera, Gulf News, Dawn (Pakistan's oldest English broadsheet)
- Punjab Government official statements (via news report attribution)
- Lahore High Court records (via Pakistan Today, ProPakistani)
- Punjab Police official statements

**Tier 2 (Reliable — Established Pakistani Media):**
- Geo News, Express Tribune, Pakistan Today, The News International
- Daily Ittehad, Daily Times, 24 News HD, Duniya News

**Tier 3 (Supplementary — Digital/Blog Outlets):**
- ProPakistani, PakWheels Blog, Daily Pakistan, Urdupoint
- Facebook/Instagram public posts, Twitter/X posts

All incident records sourced from Tier 3 outlets were independently cross-checked against Tier 1–2 sources where possible. No incident records were included based solely on Tier 3 attribution without at least partial corroboration.

---
