from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException
import time

# Set up WebDriver options
firefox_options = Options()
driver = webdriver.Firefox(options=firefox_options)

# Open GitHub and log in
driver.get("https://github.com/login")

# Sign in to GitHub
username = "" #add your username
password = "" #add your password

driver.find_element(By.CSS_SELECTOR, "#login_field").send_keys(username)
driver.find_element(By.ID, "password").send_keys(password)
driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

# Function to get followers
def get_followers():
    driver.get(f"https://github.com/{username}?tab=followers")
    followers = set()  # Using a set to avoid duplicates

    while True:
        try:
            # Find all followers' usernames
            followers_elements = driver.find_elements(By.CSS_SELECTOR, "a[data-hovercard-type='user']")
            followers.update([elem.get_attribute('href').split('/')[-1] for elem in followers_elements])

            # Check if there's a 'Next' button to paginate
            next_button = driver.find_element(By.CSS_SELECTOR, ".pagination > a:nth-child(2)")
            if next_button:
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)  # Wait for the next page to load
            else:
                break
        except NoSuchElementException:
            break

    return followers

# Function to unfollow users who don't follow back
def unfollow_non_followers(followers_set):
    driver.get(f"https://github.com/{username}?tab=following")

    while True:
        try:
            # Find all following users' elements
            following_elements = driver.find_elements(By.CSS_SELECTOR, "a[data-hovercard-type='user']")
            unfollow_buttons = driver.find_elements(By.CSS_SELECTOR, "input[value='Unfollow']")

            for elem, button in zip(following_elements, unfollow_buttons):
                user = elem.get_attribute('href').split('/')[-1]
                if user not in followers_set:
                    print(f"Unfollowing {user} as they are not in your followers list.")
                    try:
                        # Scroll to the unfollow button and click it
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(0.05)
                    except ElementNotInteractableException:
                        print(f"Element not interactable for {user}. Skipping...")
                    except Exception as e:
                        print(f"An error occurred while unfollowing {user}: {e}")
                else:
                    print(f"{user} is following you, so not unfollowing.")

            # Click the 'Next' button to go to the next page of followings
            next_button = driver.find_element(By.CSS_SELECTOR, ".pagination > a:nth-child(2)")
            if next_button:
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
            else:
                break

        except NoSuchElementException:
            break

# Execute the functions
try:
    followers_set = get_followers()  # Step 1: Get followers
    unfollow_non_followers(followers_set)  # Step 2: Unfollow non-followers
finally:
    driver.quit()
