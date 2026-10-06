import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


# ==========================================
# Browser Setup
# ==========================================

options = webdriver.ChromeOptions()

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)
driver.maximize_window()


# ==========================================
# Configuration
# ==========================================

BASE_URL = "https://www.naukrigulf.com"

search_pages = [
    f"{BASE_URL}/data-engineer-jobs",
    f"{BASE_URL}/data-engineer-jobs-2",
    f"{BASE_URL}/data-engineer-jobs-3"
]

jobs = []
visited_links = set()


# ==========================================
# Helper Function
# ==========================================

def get_first_text(selectors):
    """
    Try multiple CSS selectors and return
    the first non-empty text found.
    """

    for selector in selectors:

        try:

            elements = driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            for element in elements:

                text = element.text.strip()

                if text:
                    return text

        except Exception:
            continue

    return "N/A"


# ==========================================
# Check Real Job Link
# ==========================================

def is_real_job(url, title):

    if not url:
        return False

    url_lower = url.lower()
    title_lower = title.lower().strip()


    # Individual job URL
    if "-jid-" not in url_lower:
        return False


    # Exclude related/search pages
    excluded_titles = [
        "airport jobs",
        "fresher jobs",
        "teaching jobs",
        "data entry clerk jobs",
        "data analytics jobs",
        "data administrator jobs",
        "data management jobs",
        "data warehousing jobs",
        "data manager jobs",
        "data mining jobs",
        "data center administrator jobs",
        "data engineer jobs in"
    ]


    for excluded in excluded_titles:

        if excluded in title_lower:
            return False


    return True


# ==========================================
# Main Scraper
# ==========================================

try:

    for page_number, page_url in enumerate(search_pages, 1):

        print(
            f"\n=================== "
            f"Scraping Page {page_number} "
            f"==================="
        )


        # ======================================
        # Open Search Page
        # ======================================

        driver.get(page_url)

        time.sleep(4)


        # ======================================
        # Find Potential Job Links
        # ======================================

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "a.ng-head, a.title, .job-title a, a[href*='-jobs-in-']"
        )

        print(
            f"Potential links found: {len(elements)}"
        )


        page_links = []


        # ======================================
        # Extract Real Job Links
        # ======================================

        for element in elements:

            try:

                href = element.get_attribute("href")
                title = element.text.strip()


                if not href:
                    continue


                if not title:
                    continue


                if not is_real_job(href, title):
                    continue


                if href not in page_links:

                    page_links.append(href)


            except Exception:

                continue


        print(
            f"Real Data Engineer jobs found on Page "
            f"{page_number}: {len(page_links)}"
        )


        # ======================================
        # Scrape Each Job
        # ======================================

        for index, job_url in enumerate(page_links, 1):

            try:

                # ----------------------------------
                # Avoid Duplicate Jobs
                # ----------------------------------

                if job_url in visited_links:
                    continue

                visited_links.add(job_url)


                # ----------------------------------
                # Open Job Page
                # ----------------------------------

                driver.get(job_url)

                time.sleep(2.5)


                # ==================================
                # Job Title
                # ==================================

                try:

                    title = driver.find_element(
                        By.TAG_NAME,
                        "h1"
                    ).text.strip()

                except Exception:

                    title = "N/A"


                # ==================================
                # Company Name
                # ==================================

                company = get_first_text([
                    "a.info-org"
                ])


                # ==================================
                # Required Experience
                # ==================================

                experience = get_first_text([
                    "li.info-exp span:not(.ico)",
                    "li.info-exp span",
                    ".info-exp span:not(.ico)"
                ])


                # ==================================
                # Job Location
                # ==================================

                location = get_first_text([
                    "li.info-loc span:not(.ico)",
                    "li.info-loc span",
                    ".info-loc span:not(.ico)"
                ])


                # ==================================
                # Full Job Description
                # ==================================

                description = "N/A"


                description_selectors = [
                    ".jd-desc",
                    ".job-description",
                    "#job-description",
                    "[class*='jd-desc']",
                    "[class*='job-description']"
                ]


                for selector in description_selectors:

                    try:

                        description_elements = driver.find_elements(
                            By.CSS_SELECTOR,
                            selector
                        )

                        for element in description_elements:

                            text = element.text.strip()

                            if len(text) > 100:

                                description = text
                                break


                        if description != "N/A":
                            break


                    except Exception:

                        continue


                # ==================================
                # Description Fallback
                # ==================================

                if description == "N/A":

                    try:

                        description = driver.find_element(
                            By.TAG_NAME,
                            "body"
                        ).text.strip()

                    except Exception:

                        description = "N/A"


                # ==================================
                # Save Job
                # ==================================

                jobs.append([
                    title,
                    company,
                    location,
                    experience,
                    description
                ])


                print(
                    f"[{index}/{len(page_links)}] "
                    f"Scraped: {title} | "
                    f"{company} | "
                    f"{location} | "
                    f"{experience}"
                )


            except Exception as error:

                print(
                    f"Error scraping job: {job_url}"
                )

                print(f"Error: {error}")

                continue


finally:

    driver.quit()


# ==========================================
# Export CSV
# ==========================================

csv_filename = "data_engineer_jobs.csv"


with open(
    csv_filename,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Job Title",
        "Company Name",
        "Job Location",
        "Required Experience",
        "Full Job Description"
    ])

    writer.writerows(jobs)


# ==========================================
# Final Result
# ==========================================

print("\n==========================================")
print("Task Completed Successfully!")
print("==========================================")

print(
    f"Total jobs scraped: {len(jobs)}"
)

print(
    f"CSV file: {csv_filename}"
)
