import requests
from scraper import extract_morgen_disruptions
from image_generator import generate_disruption_images

def main():
    # Step 1: Download the HTML
    url = "https://sbahn.berlin/en/plan-a-journey/timetable-changes/"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch page:", response.status_code)
        return
    
    html_content = response.text

    # Step 2: Parse the HTML string directly
    disruptions = extract_morgen_disruptions(html_string=html_content)
    
    # Step 3: Generate the disruption images
    image_paths = generate_disruption_images(disruptions)
    print("Generated images:")
    for path in image_paths:
        print(path)

if __name__ == "__main__":
    main()