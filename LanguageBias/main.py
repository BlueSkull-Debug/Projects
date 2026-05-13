import re
import html
import requests
import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime


# ------------------------------------------------------
# LOADED LANGUAGE / BIAS ANALYSIS WEB APP
# Streamlit version for cloud
# ------------------------------------------------------
# PAGE SETUP
# ------------------------------------------------------
st.set_page_config(
   page_title="BiasLens | Media Bias Analysis Tool",
   page_icon="📰",
   layout="wide"
)


# ------------------------------------------------------
# CUSTOM CSS FOR STYLE
# ------------------------------------------------------
st.markdown(
   """
   <style>
       .stApp {
           background: #f7f7f4;
           color: #1f1f1f;
       }


       .main-title {
           font-size: 3.2rem;
           font-weight: 900;
           letter-spacing: -2px;
           margin-bottom: 0.2rem;
           color: #111111;
       }


       .subtitle {
           font-size: 1.05rem;
           color: #5b5b5b;
           margin-bottom: 2rem;
           max-width: 850px;
       }


       .metric-card {
           background: #ffffff;
           border: 1px solid #e6e2dc;
           border-radius: 18px;
           padding: 1.3rem;
           box-shadow: 0 8px 25px rgba(0,0,0,0.04);
           min-height: 150px;
       }


       .metric-label {
           font-size: 0.82rem;
           text-transform: uppercase;
           letter-spacing: 0.08rem;
           color: #777777;
           font-weight: 700;
       }


       .metric-value {
           font-size: 2.2rem;
           font-weight: 900;
           margin-top: 0.35rem;
           color: #111111;
       }


       .metric-help {
           font-size: 0.92rem;
           color: #666666;
           margin-top: 0.45rem;
           line-height: 1.35;
       }


       .section-card {
           background: #ffffff;
           border: 1px solid #e6e2dc;
           border-radius: 18px;
           padding: 1.4rem;
           box-shadow: 0 8px 25px rgba(0,0,0,0.04);
           margin-bottom: 1rem;
       }


       .small-label {
           font-size: 0.85rem;
           font-weight: 800;
           color: #5b5b5b;
           letter-spacing: 0.03rem;
           text-transform: uppercase;
       }


       .finding-box {
           border-left: 5px solid #111111;
           background: #fafafa;
           border-radius: 12px;
           padding: 1rem 1.2rem;
           margin-bottom: 0.8rem;
       }


       .highlighted-article {
           background: #ffffff;
           border: 1px solid #e6e2dc;
           border-radius: 18px;
           padding: 1.4rem;
           line-height: 1.75;
           font-size: 1rem;
           max-height: 500px;
           overflow-y: auto;
       }


       .highlight-emotional {
           background: #fff1a8;
           border-radius: 5px;
           padding: 1px 4px;
           font-weight: 700;
       }


       .highlight-extreme {
           background: #ffd6e7;
           border-radius: 5px;
           padding: 1px 4px;
           font-weight: 700;
       }


       .highlight-loaded {
           background: #ffd2b8;
           border-radius: 5px;
           padding: 1px 4px;
           font-weight: 700;
       }


       .highlight-framing {
           background: #d7ecff;
           border-radius: 5px;
           padding: 1px 4px;
           font-weight: 700;
       }


       .highlight-opinion {
           background: #dff5d8;
           border-radius: 5px;
           padding: 1px 4px;
           font-weight: 700;
       }


       .pill {
           display: inline-block;
           padding: 0.28rem 0.65rem;
           border-radius: 999px;
           background: #efeee9;
           color: #333333;
           font-size: 0.82rem;
           font-weight: 800;
           margin: 0.15rem 0.2rem 0.15rem 0;
       }


       .footer-note {
           font-size: 0.82rem;
           color: #777777;
           margin-top: 1rem;
       }
   </style>
   """,
   unsafe_allow_html=True
)


# ------------------------------------------------------
# BIAS PATTERNS
# ------------------------------------------------------
bias_patterns = {
   "Emotional Language": {
       "patterns": [
           r"\boutrageous\b", r"\bshocking\b", r"\bterrifying\b", r"\bhorrific\b",
           r"\bdisgusting\b", r"\bheartbreaking\b", r"\bdevastating\b",
           r"\bdangerous\b", r"\btragic\b", r"\bfurious\b", r"\balarming\b",
           r"\bscary\b", r"\bpanic\b", r"\bevil\b", r"\bchaos\b", r"\bcrisis\b"
       ],
       "explanation": "This wording may create a strong emotional reaction instead of staying neutral.",
       "css": "highlight-emotional"
   },
   "Extreme Language": {
       "patterns": [
           r"\balways\b", r"\bnever\b", r"\beveryone\b", r"\bno one\b",
           r"\bcompletely\b", r"\btotally\b", r"\babsolutely\b", r"\bentirely\b",
           r"\bworst\b", r"\bbest\b", r"\ball\b", r"\bnothing\b",
           r"\bmust\b", r"\bguaranteed\b", r"\bundeniable\b"
       ],
       "explanation": "Extreme wording can make a claim sound more certain or dramatic than the evidence may support.",
       "css": "highlight-extreme"
   },
   "Loaded Wording": {
       "patterns": [
           r"\bpropaganda\b", r"\bcorrupt\b", r"\bradical\b", r"\bagenda\b",
           r"\bbrainwashed\b", r"\bfake\b", r"\blies\b", r"\bmanipulated\b",
           r"\belites\b", r"\bdisaster\b", r"\bfailure\b", r"\bincompetent\b",
           r"\bcriminal\b", r"\breckless\b", r"\battack\b", r"\bdestroy\b"
       ],
       "explanation": "Loaded terms can push the reader toward a judgment before giving full evidence.",
       "css": "highlight-loaded"
   },
   "One-Sided Framing": {
       "patterns": [
           r"critics say", r"supporters insist", r"experts warn", r"many believe",
           r"some people claim", r"it is clear that", r"the truth is",
           r"without question", r"there is no doubt", r"refused to answer"
       ],
       "explanation": "This phrase may frame the issue from one side or present a claim as obvious.",
       "css": "highlight-framing"
   },
   "Opinionated Phrasing": {
       "patterns": [
           r"\bshould\b", r"\bclearly\b", r"\bobviously\b", r"\bwrong\b",
           r"\bright\b", r"\bunfair\b", r"\bdeserves\b", r"\bfailed to\b",
           r"\brefused to\b", r"\bfinally admitted\b"
       ],
       "explanation": "This wording may suggest the writer is interpreting or judging the event instead of only reporting it.",
       "css": "highlight-opinion"
   }
}


factual_markers = [
   "according to", "reported", "data", "study", "survey", "evidence",
   "percent", "%", "said", "stated", "announced", "published",
   "research", "official", "records show", "documents show"
]


balance_markers = [
   "however", "although", "on the other hand", "meanwhile", "but",
   "supporters", "critics", "opponents", "different views", "both sides"
]


quote_markers = ["said", "stated", "told", "according to", "wrote", "reported", "explained", "announced"]
data_markers = ["data", "study", "survey", "research", "percent", "%", "statistics", "report", "records"]
anonymous_markers = ["anonymous", "unnamed source", "sources familiar", "person familiar", "officials familiar"]


# ------------------------------------------------------
# TEXT PROCESSING FUNCTIONS
# ------------------------------------------------------
def clean_text(text):
   return re.sub(r"\s+", " ", text).strip()




def split_into_sentences(text):
   sentences = re.split(r"(?<=[.!?])\s+", text.strip())
   return [sentence.strip() for sentence in sentences if sentence.strip()]




def get_words(text):
   return re.findall(r"\b[\w'-]+\b", text.lower())




def count_marker_matches(text, markers):
   lowered = text.lower()
   return sum(lowered.count(marker.lower()) for marker in markers)




def detect_tone(sentence):
   lowered = sentence.lower()


   negative_words = [
       "bad", "dangerous", "tragic", "failed", "failure", "harmful", "angry",
       "fear", "crisis", "disaster", "threat", "problem", "corrupt", "reckless"
   ]


   positive_words = [
       "good", "successful", "helpful", "improved", "benefit", "strong",
       "safe", "effective", "progress", "support", "hope"
   ]


   negative_count = sum(1 for word in negative_words if re.search(r"\b" + re.escape(word) + r"\b", lowered))
   positive_count = sum(1 for word in positive_words if re.search(r"\b" + re.escape(word) + r"\b", lowered))


   if negative_count > positive_count:
       return "Negative / critical tone"
   if positive_count > negative_count:
       return "Positive / supportive tone"
   return "Mostly neutral tone"




def get_score_description(score):
   if score < 15:
       return "Low: The article has a mostly neutral wording pattern based on this prototype."
   if score < 35:
       return "Moderate: Some wording may influence the reader, but the article is not heavily loaded overall."
   if score < 60:
       return "High: The article contains several loaded, emotional, or opinionated language patterns."
   return "Very High: The article uses a lot of language that may strongly shape the reader's opinion."




def find_bias_in_sentence(sentence):
   sentence_results = []
   lowered_sentence = sentence.lower()


   for category, data in bias_patterns.items():
       found_terms = []


       for pattern in data["patterns"]:
           matches = re.findall(pattern, lowered_sentence, flags=re.IGNORECASE)


           for match in matches:
               if isinstance(match, tuple):
                   found_terms.append(" ".join(match))
               else:
                   found_terms.append(match)


       if found_terms:
           sentence_results.append({
               "category": category,
               "terms": sorted(set(found_terms)),
               "explanation": data["explanation"],
               "tone": detect_tone(sentence),
               "sentence": sentence
           })


   return sentence_results




def calculate_bias_score(text, results):
   sentences = split_into_sentences(text)
   words = get_words(text)


   if not sentences or not words:
       return 0


   flagged_sentences = set()
   total_flags = 0
   weighted_points = 0


   weights = {
       "Emotional Language": 3,
       "Extreme Language": 2,
       "Loaded Wording": 3,
       "One-Sided Framing": 2,
       "Opinionated Phrasing": 2
   }


   for item in results:
       flagged_sentences.add(item["sentence"])
       term_count = len(item["terms"])
       total_flags += term_count
       weighted_points += term_count * weights.get(item["category"], 1)


   flagged_sentence_ratio = len(flagged_sentences) / len(sentences)
   flag_density = total_flags / len(words)
   base_score = (flagged_sentence_ratio * 60) + (flag_density * 500) + weighted_points


   factual_count = count_marker_matches(text, factual_markers)
   balance_count = count_marker_matches(text, balance_markers)
   adjustment = (factual_count * 1.5) + (balance_count * 2)


   return max(0, min(round(base_score - adjustment, 2), 100))




def analyze_text(text):
   text = clean_text(text)
   sentences = split_into_sentences(text)
   all_results = []


   for sentence in sentences:
       all_results.extend(find_bias_in_sentence(sentence))


   score = calculate_bias_score(text, all_results)
   return score, all_results




def get_category_counts(results):
   counts = {}
   for item in results:
       counts[item["category"]] = counts.get(item["category"], 0) + 1
   return counts




def get_top_category(results):
   counts = get_category_counts(results)
   if not counts:
       return "None"
   return max(counts, key=counts.get)


# ------------------------------------------------------
# ARTICLE FETCHING
# ------------------------------------------------------
def fetch_article_from_url(url):
   headers = {"User-Agent": "Mozilla/5.0"}
   response = requests.get(url, headers=headers, timeout=10)
   response.raise_for_status()


   soup = BeautifulSoup(response.text, "html.parser")


   for tag in soup(["script", "style", "noscript"]):
       tag.extract()


   headline = ""
   h1 = soup.find("h1")
   if h1:
       headline = clean_text(h1.get_text(" ", strip=True))
   elif soup.title:
       headline = clean_text(soup.title.get_text(" ", strip=True))


   paragraphs = soup.find_all("p")
   article_text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
   article_text = clean_text(article_text)


   return headline, article_text


# ------------------------------------------------------
# HIGHLIGHTING
# ------------------------------------------------------
def build_highlighted_html(text, results):
   if not text:
       return ""


   spans = []
   lowered_text = text.lower()


   for item in results:
       category = item["category"]
       css_class = bias_patterns[category]["css"]


       for term in item["terms"]:
           pattern = r"\b" + re.escape(term.lower()) + r"\b"


           for match in re.finditer(pattern, lowered_text):
               spans.append({
                   "start": match.start(),
                   "end": match.end(),
                   "class": css_class,
                   "category": category
               })


   if not spans:
       return html.escape(text)


   spans = sorted(spans, key=lambda x: (x["start"], -(x["end"] - x["start"])))
   filtered_spans = []
   last_end = -1


   for span in spans:
       if span["start"] >= last_end:
           filtered_spans.append(span)
           last_end = span["end"]


   output = []
   current = 0


   for span in filtered_spans:
       output.append(html.escape(text[current:span["start"]]))
       highlighted_piece = html.escape(text[span["start"]:span["end"]])
       output.append(f'<span class="{span["class"]}" title="{html.escape(span["category"])}">{highlighted_piece}</span>')
       current = span["end"]


   output.append(html.escape(text[current:]))
   return "".join(output)


# ------------------------------------------------------
# HEADLINE ANALYSIS
# ------------------------------------------------------
def compare_headline_to_article(headline, article_text):
   headline = clean_text(headline)
   article_text = clean_text(article_text)


   if not headline:
       return {
           "available": False,
           "score": 0,
           "notes": ["No headline was entered or found from the URL."],
           "headline_results": []
       }


   headline_score, headline_results = analyze_text(headline)
   article_score, article_results = analyze_text(article_text)


   notes = []


   if headline_score > article_score + 15:
       notes.append("The headline appears more emotionally loaded than the article body.")
   else:
       notes.append("The headline does not appear much more loaded than the article body.")


   if headline_results:
       notes.append("The headline contains loaded, emotional, extreme, or opinionated language patterns.")
   else:
       notes.append("The headline does not contain major loaded language patterns from this prototype.")


   headline_words = set(get_words(headline))
   article_words = set(get_words(article_text))
   overlap = headline_words.intersection(article_words)
   overlap_ratio = len(overlap) / max(len(headline_words), 1)


   if overlap_ratio < 0.35:
       notes.append("The headline may not closely match the article body based on word overlap.")
   else:
       notes.append("The headline appears connected to the article body based on keyword overlap.")


   if any(word in headline.lower() for word in ["destroy", "exposed", "shocking", "secret", "finally admitted", "panic"]):
       notes.append("The headline may make the story sound more dramatic than the article evidence supports.")


   return {
       "available": True,
       "score": headline_score,
       "article_score": article_score,
       "notes": notes,
       "headline_results": headline_results
   }


# ------------------------------------------------------
# SOURCE TRANSPARENCY CHECK
# ------------------------------------------------------
def calculate_transparency_score(article_text, headline, user_checks):
   text = clean_text(article_text)
   lowered = text.lower()


   auto_checks = {
       "Cites sources or quotes": count_marker_matches(text, quote_markers) > 0 or '"' in text,
       "Includes data or evidence": count_marker_matches(text, data_markers) > 0,
       "Shows more than one side": count_marker_matches(text, balance_markers) > 0,
       "Uses anonymous claims": any(marker in lowered for marker in anonymous_markers),
       "Headline matches article": True
   }


   if headline:
       headline_words = set(get_words(headline))
       article_words = set(get_words(article_text))
       overlap = headline_words.intersection(article_words)
       auto_checks["Headline matches article"] = len(overlap) / max(len(headline_words), 1) >= 0.35


   final_checks = {
       "Cites sources or quotes": user_checks.get("cites_sources", auto_checks["Cites sources or quotes"]),
       "Includes data or evidence": user_checks.get("includes_data", auto_checks["Includes data or evidence"]),
       "Quotes more than one side": user_checks.get("multiple_sides", auto_checks["Shows more than one side"]),
       "Avoids anonymous claims": not user_checks.get("anonymous_claims", auto_checks["Uses anonymous claims"]),
       "Headline matches article": user_checks.get("headline_matches", auto_checks["Headline matches article"])
   }


   score = round((sum(1 for value in final_checks.values() if value) / len(final_checks)) * 100, 2)


   if score >= 80:
       meaning = "Strong transparency: The article shows several signs of source support and media literacy quality."
   elif score >= 60:
       meaning = "Moderate transparency: The article has some support, but users should still review the evidence carefully."
   elif score >= 40:
       meaning = "Limited transparency: The article may need stronger sourcing, data, or balanced viewpoints."
   else:
       meaning = "Low transparency: The article may not provide enough evidence or source clarity."


   return score, meaning, final_checks, auto_checks


# ------------------------------------------------------
# REPORT CREATION
# ------------------------------------------------------
def create_report(headline, article_text, score, results, headline_analysis=None, transparency=None):
   category_counts = get_category_counts(results)
   flagged_sentence_count = len(set(item["sentence"] for item in results))
   total_sentences = len(split_into_sentences(article_text))


   report = []
   report.append("BiasLens Media Bias Analysis Report")
   report.append("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
   report.append("-" * 45)
   report.append("")


   if headline:
       report.append("Headline:")
       report.append(headline)
       report.append("")


   report.append(f"Bias Score: {score}%")
   report.append(get_score_description(score))
   report.append(f"Flagged Sentences: {flagged_sentence_count} out of {total_sentences}")
   report.append(f"Most Common Category: {get_top_category(results)}")
   report.append("")


   report.append("Category Counts:")
   if category_counts:
       for category, count in category_counts.items():
           report.append(f"- {category}: {count}")
   else:
       report.append("- No major categories detected")
   report.append("")


   if headline_analysis and headline_analysis.get("available"):
       report.append("Headline Analysis:")
       report.append(f"Headline Bias Score: {headline_analysis['score']}%")
       for note in headline_analysis["notes"]:
           report.append(f"- {note}")
       report.append("")


   if transparency:
       transparency_score, meaning, final_checks, auto_checks = transparency
       report.append("Source Transparency:")
       report.append(f"Transparency Score: {transparency_score}%")
       report.append(meaning)
       for label, value in final_checks.items():
           report.append(f"- {label}: {'Yes' if value else 'No'}")
       report.append("")


   report.append("Detailed Findings:")
   if results:
       for number, item in enumerate(results, start=1):
           report.append(f"{number}. {item['category']}")
           report.append(f"Tone: {item['tone']}")
           report.append(f"Terms/Phrases: {', '.join(item['terms'])}")
           report.append(f"Why this may matter: {item['explanation']}")
           report.append(f"Sentence: {item['sentence']}")
           report.append("")
   else:
       report.append("No major bias indicators were detected by this prototype.")


   report.append("Prototype Note:")
   report.append("This tool uses rule-based phrase matching, sentence context, tone clues, and transparency questions. It supports human review but does not prove whether an article is fully biased or unbiased.")


   return "\n".join(report)


# ------------------------------------------------------
# STREAMLIT UI
# ------------------------------------------------------
st.markdown('<div class="main-title">BiasLens</div>', unsafe_allow_html=True)
st.markdown(
   '<div class="subtitle">A clean Python-based media bias analysis tool that reviews loaded language, emotional tone, framing, headline strength, and source transparency.</div>',
   unsafe_allow_html=True
)


with st.sidebar:
   st.subheader("How to use")
   st.write("1. Paste an article URL or article text.")
   st.write("2. Add a headline if you want headline analysis.")
   st.write("3. Click Analyze Article.")
   st.write("4. Review highlighted wording, score, and explanations.")
   st.divider()
   st.caption("This is a prototype. It helps users review media language, but it should not be treated as a final fact-checker.")


left_col, right_col = st.columns([1.1, 0.9], gap="large")


with left_col:
   st.markdown('<div class="section-card">', unsafe_allow_html=True)
   st.markdown('<div class="small-label">Input</div>', unsafe_allow_html=True)


   url = st.text_input("Article URL", placeholder="Paste article URL here...", label_visibility="visible")


   load_clicked = st.button("Load from URL", use_container_width=True)


   if "article_text" not in st.session_state:
       st.session_state.article_text = ""
   if "headline" not in st.session_state:
       st.session_state.headline = ""


   if load_clicked:
       if not url.strip():
           st.warning("Please enter a URL first.")
       else:
           try:
               fetched_headline, fetched_text = fetch_article_from_url(url)
               if not fetched_text:
                   st.error("Could not extract readable paragraph text from this page. You can still paste the article manually.")
               else:
                   st.session_state.article_text = fetched_text
                   if fetched_headline:
                       st.session_state.headline = fetched_headline
                   st.success("Article loaded successfully.")
           except requests.exceptions.RequestException:
               st.error("Could not load the webpage. Some websites block scraping, so try pasting the article text manually.")
           except Exception as error:
               st.error(f"Something went wrong: {error}")


   headline = st.text_input(
       "Headline (optional)",
       value=st.session_state.headline,
       placeholder="Paste or edit the headline here..."
   )


   article_text = st.text_area(
       "Article Text",
       value=st.session_state.article_text,
       height=360,
       placeholder="Paste article text here if you are not using a URL..."
   )


   st.session_state.article_text = article_text
   st.session_state.headline = headline


   st.markdown('</div>', unsafe_allow_html=True)


with right_col:
   st.markdown('<div class="section-card">', unsafe_allow_html=True)
   st.markdown('<div class="small-label">Optional Advanced Checks</div>', unsafe_allow_html=True)


   include_headline_check = st.checkbox("Analyze headline vs. article", value=True)
   include_transparency_check = st.checkbox("Include source transparency score", value=True)


   user_checks = {}


   if include_transparency_check:
       with st.expander("Source credibility questions", expanded=False):
           st.caption("You can answer these manually. If you leave them unchecked, the app still attempts a basic automatic estimate.")
           user_checks["cites_sources"] = st.checkbox("Does the article cite sources or include quotes?")
           user_checks["includes_data"] = st.checkbox("Does the article include data, research, or evidence?")
           user_checks["multiple_sides"] = st.checkbox("Does the article quote or explain more than one side?")
           user_checks["anonymous_claims"] = st.checkbox("Does the article rely on anonymous claims?")
           user_checks["headline_matches"] = st.checkbox("Does the headline seem to match the article body?")


   analyze_clicked = st.button("Analyze Article", type="primary", use_container_width=True)
   st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------
# ANALYSIS OUTPUT
# ------------------------------------------------------
if analyze_clicked:
   if not article_text.strip():
       st.error("Please enter article text or load an article from a URL first.")
   else:
       score, results = analyze_text(article_text)
       category_counts = get_category_counts(results)
       total_sentences = len(split_into_sentences(article_text))
       flagged_sentence_count = len(set(item["sentence"] for item in results))
       top_category = get_top_category(results)


       headline_analysis = None
       if include_headline_check:
           headline_analysis = compare_headline_to_article(headline, article_text)


       transparency = None
       if include_transparency_check:
           transparency = calculate_transparency_score(article_text, headline, user_checks)


       st.divider()


       metric_one, metric_two, metric_three, metric_four = st.columns(4)


       with metric_one:
           st.markdown(
               f"""
               <div class="metric-card">
                   <div class="metric-label">Bias Score</div>
                   <div class="metric-value">{score}%</div>
                   <div class="metric-help">{get_score_description(score)}</div>
               </div>
               """,
               unsafe_allow_html=True
           )


       with metric_two:
           st.markdown(
               f"""
               <div class="metric-card">
                   <div class="metric-label">Flagged Sentences</div>
                   <div class="metric-value">{flagged_sentence_count}/{total_sentences}</div>
                   <div class="metric-help">Sentences with at least one loaded, emotional, or framing pattern.</div>
               </div>
               """,
               unsafe_allow_html=True
           )


       with metric_three:
           st.markdown(
               f"""
               <div class="metric-card">
                   <div class="metric-label">Top Category</div>
                   <div class="metric-value" style="font-size:1.6rem;">{top_category}</div>
                   <div class="metric-help">Most common type of language flagged in this article.</div>
               </div>
               """,
               unsafe_allow_html=True
           )


       with metric_four:
           if transparency:
               transparency_score, transparency_meaning, final_checks, auto_checks = transparency
               metric_value = f"{transparency_score}%"
               metric_help = transparency_meaning
           else:
               metric_value = "Off"
               metric_help = "Source transparency scoring was not selected."


           st.markdown(
               f"""
               <div class="metric-card">
                   <div class="metric-label">Transparency Score</div>
                   <div class="metric-value">{metric_value}</div>
                   <div class="metric-help">{metric_help}</div>
               </div>
               """,
               unsafe_allow_html=True
           )


       st.subheader("Summary")
       st.markdown('<div class="section-card">', unsafe_allow_html=True)
       if results:
           st.write("This article contains language patterns that may influence how readers interpret the topic. The flagged wording should be reviewed in context rather than treated as automatically biased.")
       else:
           st.write("No major loaded language patterns were found by this prototype. This does not prove the article is perfectly neutral, but it suggests fewer obvious bias indicators.")


       if category_counts:
           st.write("**Category breakdown:**")
           for category, count in category_counts.items():
               st.markdown(f'<span class="pill">{category}: {count}</span>', unsafe_allow_html=True)
       st.markdown('</div>', unsafe_allow_html=True)


       if include_headline_check and headline_analysis:
           with st.expander("Headline vs. Article Analysis", expanded=True):
               if headline_analysis["available"]:
                   st.write(f"**Headline bias score:** {headline_analysis['score']}%")
                   for note in headline_analysis["notes"]:
                       st.write(f"- {note}")


                   if headline_analysis["headline_results"]:
                       st.write("**Headline flagged language:**")
                       for item in headline_analysis["headline_results"]:
                           st.write(f"- **{item['category']}**: {', '.join(item['terms'])}")
                   else:
                       st.write("No major headline bias indicators were found by this prototype.")
               else:
                   st.info("No headline was entered or found. Add a headline to use this feature.")


       if include_transparency_check and transparency:
           transparency_score, transparency_meaning, final_checks, auto_checks = transparency
           with st.expander("Source Transparency Details", expanded=True):
               st.write(f"**Transparency Score:** {transparency_score}%")
               st.write(transparency_meaning)
               st.write("**Checklist results:**")
               for label, value in final_checks.items():
                   st.write(f"- {'✅' if value else '❌'} {label}")


       st.subheader("Highlighted Article")
       highlighted_html = build_highlighted_html(article_text, results)
       st.markdown(
           f'<div class="highlighted-article">{highlighted_html}</div>',
           unsafe_allow_html=True
       )


       with st.expander("Detailed Bias Findings", expanded=False):
           if results:
               for number, item in enumerate(results, start=1):
                   st.markdown(
                       f"""
                       <div class="finding-box">
                           <strong>{number}. {item['category']}</strong><br>
                           <strong>Tone:</strong> {item['tone']}<br>
                           <strong>Flagged terms/phrases:</strong> {', '.join(item['terms'])}<br>
                           <strong>Why this may matter:</strong> {item['explanation']}<br><br>
                           <em>{html.escape(item['sentence'])}</em>
                       </div>
                       """,
                       unsafe_allow_html=True
                   )
           else:
               st.write("No major bias indicators were detected by this prototype.")


       report_text = create_report(
           headline=headline,
           article_text=article_text,
           score=score,
           results=results,
           headline_analysis=headline_analysis,
           transparency=transparency
       )


       st.download_button(
           label="Download Analysis Report",
           data=report_text,
           file_name="biaslens_analysis_report.txt",
           mime="text/plain",
           use_container_width=True
       )


       st.markdown(
           '<div class="footer-note">Prototype note: BiasLens uses rule-based phrase matching, sentence-level context, tone clues, headline comparison, and source transparency questions. It supports media literacy review, but it does not prove whether an article is fully biased or unbiased.</div>',
           unsafe_allow_html=True
       )
