from bs4 import BeautifulSoup
def exclude_night_disruptions(data):
    keywords = ["night", "nights", "nacht"]
    return [
        d for d in data
        if not any(kw in d.get("timestamp", "").lower() for kw in keywords)
    ]
def extract_morgen_disruptions(html_file=None, html_string=None):
    if html_string:
        soup = BeautifulSoup(html_string, "html.parser")
    elif html_file:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
    else:
        raise ValueError("Either html_file or html_string must be provided.")

    morgen_section = soup.find("div", {"id": "tbc-p4"})
    if not morgen_section:
        print("⚠️ Could not find 'morgen' section (id='tbc-p4').")
        return []

    entries = morgen_section.find_all("div", class_="c-construction-announcement")

    data = []
    for entry in entries:
        lines = entry.get("data-lines", "")
        title_elem = entry.find(class_="o-construction-announcement-title__heading")
        title = title_elem.get_text(strip=True) if title_elem else ""

        timestamp_elem = entry.find(class_="c-timespans")
        timestamp = timestamp_elem.get_text(strip=True) if timestamp_elem else ""

        reason_elem = entry.find(class_="c-construction-announcement-foot__labels")
        reason = reason_elem.get_text(strip=True) if reason_elem else ""

        data.append({
            "data-lines": lines,
            "title": title,
            "timestamp": timestamp,
            "reason": reason
        })
    return exclude_night_disruptions(data)