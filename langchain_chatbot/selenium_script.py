from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def extract_courses():
    # Extracts course details from Brainlox courses page using Selenium.
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (optional)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Open Brainlox Courses Page
        driver.get("https://brainlox.com/courses/category/technical")
        driver.implicitly_wait(5)  # Wait for elements to load

        # Extract all course containers
        course_containers = driver.find_elements(By.CLASS_NAME, "single-courses-box")

        courses_data = []
        errors = []  # To store errors

        # Loop through each course
        for course in course_containers:
            try:
                title = course.find_element(By.TAG_NAME, "h3").text
                course_link = course.find_element(By.TAG_NAME, "a").get_attribute("href")
                price = course.find_element(By.CLASS_NAME, "price-per-session").text

                # Extract description (Modify this based on the actual HTML structure)
                description_element = course.find_elements(By.TAG_NAME, "p")
                description = description_element[0].text if description_element else "No description available"

                # Find the "Book Demo" button safely
                book_demo_btn = course.find_elements(By.XPATH, './/a[contains(@class, "BookDemo-btn")]')
                book_demo_link = book_demo_btn[0].get_attribute("href") if book_demo_btn else "N/A"

                courses_data.append({
                    "title": title,
                    "course_link": course_link,
                    "price": price,
                    "description": description,
                    "book_demo_link": book_demo_link
                })

            except Exception as e:
                errors.append(f"⚠️ Error extracting a course: {e}")

        return courses_data

    finally:
        driver.quit()


# Testing the function (only runs if script is executed directly)
if __name__ == "__main__":
    courses = extract_courses()
    if courses:
        print("✅ Courses Extracted:")
        for course in courses:
            print(course)
    else:
        print("❌ No courses found.")
