from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time


login_url = "http://---"
username = "yourmail"
password = "yourpass"
recipient_email = "your yandex or other mail"

chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 5)  

try:
    print("1. Opening login page...")
    driver.get(login_url)

    print("2. Entering login and password...")
    login_field = wait.until(EC.presence_of_element_located((By.NAME, "RainLoopEmail")))
    login_field.send_keys(username)

    password_field = driver.find_element(By.NAME, "RainLoopPassword")
    password_field.send_keys(password)

    print("3. Clicking login button...")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

    print("4. Waiting for mail to load...")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "messageList")))
    print("✓ Login successful")

    # Find unread emails
    print("5. Searching for unread emails (by 'unseen' class)...")
    # Look for .messageListItem with class 'unseen'. It might also have 'flagged'.
    unread_selector = (By.CSS_SELECTOR, ".messageList .messageListItem.unseen")
    try:
        unread_mails = driver.find_elements(*unread_selector)
        print(f"   ✓ Found {len(unread_mails)} unread emails (by .unseen)")
    except Exception as e:
        print(f"   ❌ Error searching for unread emails: {e}")
        unread_mails = []

    # If not found by 'unseen', try 'flagged unseen'
    if not unread_mails:
        print("   Trying selector .messageListItem.flagged.unseen...")
        try:
            unread_selector_flagged = (By.CSS_SELECTOR, ".messageList .messageListItem.flagged.unseen")
            unread_mails = driver.find_elements(*unread_selector_flagged)
            print(f"   ✓ Found {len(unread_mails)} unread emails (by .flagged.unseen)")
        except Exception as e:
            print(f"   ❌ Error searching for unread emails (flagged.unseen): {e}")

    if not unread_mails:
        print("   ❌ No unread emails. Exiting.")
        exit(0)

    # Process each unread email
    for idx, mail_element in enumerate(unread_mails):
        print(f"\n--- Processing email {idx+1}/{len(unread_mails)} ---")

        # Click on the email to open in messageView
        print("   Clicking on the email to open in preview pane...")
        # Try to find .wrapper inside mail_element
        wrapper_elem = None
        try:
            wrapper_elem = mail_element.find_element(By.CSS_SELECTOR, ".wrapper")
            print("   Found .wrapper inside .messageListItem, clicking it...")
        except:
            print("   .wrapper not found, clicking .messageListItem...")
            wrapper_elem = mail_element

        # Click on wrapper (or the element itself)
        try:
            wrapper_elem.click()
            print("   ✓ Clicked on email via .click()")
        except Exception as e_click_wrapper:
            print(f"   ❌ Error with .click() on email: {e_click_wrapper}")
            # Try via JavaScript
            try:
                driver.execute_script("arguments[0].click();", wrapper_elem)
                print("   ✓ Clicked on email via JavaScript")
            except Exception as e_js_wrapper:
                print(f"   ❌ Error clicking via JavaScript: {e_js_wrapper}")
                continue # Move to the next email

        print("   Waiting for preview pane area (messageView or .b-content) to appear...")
        # Wait for an element typical for an open email in the pane
        # This could be .messageView, or .b-content inside #rl-sub-right
        preview_area_selector = (By.CSS_SELECTOR, ".messageView, #rl-sub-right .b-content") # Try both
        wait.until(EC.presence_of_element_located(preview_area_selector))
        print("   ✓ Preview pane area opened")

        # Wait for 'Forward' button in the toolbar of the preview pane
        print("   Waiting for 'Forward' button in the preview pane toolbar...")
        # The 'Forward' button might be in the toolbar of the open email (messageView)
        # Look for a button with data-bind='command: forwardCommand' or tooltip 'MESSAGE/BUTTON_FORWARD'
        # It might also have the class buttonForward
        # Look inside .messageView or #rl-sub-right
        forward_button_toolbar_selector = (By.CSS_SELECTOR, ".messageView a.buttonForward.command, .messageView [data-bind*='forwardCommand'], #rl-sub-right a.buttonForward.command, #rl-sub-right [data-bind*='forwardCommand']")
        # Or XPATH: //a[contains(@data-bind, 'forwardCommand')]
        forward_button = None
        try:
            forward_button = wait.until(EC.element_to_be_clickable(forward_button_toolbar_selector))
            print("   ✓ 'Forward' button in preview pane toolbar found and clickable")
        except:
            print("   ❌ 'Forward' button in toolbar NOT found.")
            print("   Looking for 'More' button (buttonMore) in the preview pane toolbar...")
            # If 'Forward' button is not found in the toolbar, look for 'More' button
            button_more_selector = (By.CSS_SELECTOR, ".messageView a.buttonMore.dropdown-toggle, #rl-sub-right a.buttonMore.dropdown-toggle")
            button_more = None
            try:
                button_more = wait.until(EC.element_to_be_clickable(button_more_selector))
                print("   ✓ 'More' button in preview pane toolbar found and clickable")
            except:
                print("   ❌ 'More' button in toolbar NOT found.")
                print("   ❌ Could not find 'Forward' or 'More' button.")
                # Print HTML of the preview area for debugging
                try:
                    message_view_elem = driver.find_element(By.CSS_SELECTOR, ".messageView, #rl-sub-right .b-content")
                    print("HTML of preview area (messageView) (first 1000 chars):")
                    print(message_view_elem.get_attribute("outerHTML")[:1000])
                except:
                    print("Could not get HTML of preview area")
                continue # Move to the next email

            # Click the 'More' button to open the menu
            print("   Clicking the 'More' button...")
            try:
                button_more.click()
                print("   ✓ 'More' button clicked, menu should open")
            except Exception as e_click_more:
                print(f"   ❌ Error clicking 'More' button: {e_click_more}")
                # Try via JavaScript
                try:
                    driver.execute_script("arguments[0].click();", button_more)
                    print("   ✓ 'More' button clicked via JavaScript")
                except Exception as e_js_more:
                    print(f"   ❌ Error clicking via JavaScript: {e_js_more}")
                    continue # Move to the next email

            print("   Waiting for 'Forward' button in the dropdown menu...")
            # The 'Forward' button inside the dropdown menu
            forward_in_menu_selector = (By.XPATH, "//a[@data-bind='command: forwardCommand' and contains(@class, 'menuitem')]")
            # Or: //span[@data-i18n='MESSAGE/BUTTON_FORWARD']/ancestor::a[@data-bind='command: forwardCommand']
            forward_button = wait.until(EC.element_to_be_clickable(forward_in_menu_selector))
            print("   ✓ 'Forward' button in menu found and clickable")

        # Click the 'Forward' button (from toolbar or menu)
        print("   Clicking the 'Forward' button...")
        try:
            forward_button.click()
            print("   ✓ 'Forward' button clicked")
        except Exception as e_click_forward:
            print(f"   ❌ Error clicking 'Forward' button: {e_click_forward}")
            # Try via JavaScript
            try:
                driver.execute_script("arguments[0].click();", forward_button)
                print("   ✓ 'Forward' button clicked via JavaScript")
            except Exception as e_js_forward:
                print(f"   ❌ Error clicking via JavaScript: {e_js_forward}")
                continue # Move to the next email

        # Wait for the editor form (compose area) to open
        print("   Waiting for the editor form (inputosaurus-container) to appear...")
        inputosaurus_selector = (By.CSS_SELECTOR, "ul.inputosaurus-container input.ui-autocomplete-input")
        wait.until(EC.presence_of_element_located(inputosaurus_selector))
        print("✓ Editor form opened (inputosaurus found)")

        # Enter the recipient address
        print("   Entering recipient address...")
        # Look for the input field inside inputosaurus
        try:
            to_field = driver.find_element(By.CSS_SELECTOR, "ul.inputosaurus-container input.ui-autocomplete-input")
            print("   ✓ Found 'To' field in .inputosaurus-container")
        except Exception as e_alt1:
            print(f"   ❌ Could not find 'To' field in .inputosaurus-container: {e_alt1}")
            print("   ❌ Could not enter recipient address.")
            continue # Move to the next email

        # If field is found, enter the address
        if to_field:
            # Click the field to activate it (if it's inputosaurus)
            try:
                to_field.click()
                print("   ✓ Clicked on 'To' field")
            except Exception as e_click:
                print(f"   ⚠ Error clicking 'To' field: {e_click} (might be non-critical)")

            # Send the address
            try:
                to_field.send_keys(recipient_email)
                print(f"   ✓ Address '{recipient_email}' entered into 'To' field")
            except Exception as e_send:
                print(f"   ❌ Error entering address: {e_send}")
                continue # Move to the next email
        else:
            print("   ❌ Could not find 'To' field to enter address.")
            continue # Move to the next email

        print("   ✓ Recipient address entered")

        # Send the email
        print("   Sending the email...")
        # Send button
        send_button = driver.find_element(By.CSS_SELECTOR, "a.button-send")
        send_button.click()
        print("   ✓ Email sent")

        # Mark as read (implicit)
        # After clicking .forwardFlag and subsequent actions (opening editor, sending),
        # the email is likely already marked as read by the system.
        # To explicitly mark it, one could use the "Mark as Read" command for the selected email.
        # However, after sending an email from the editor, it usually returns to the list.
        # Check if we returned to the list (messageList is visible).
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "messageList")))
            print("   ✓ Returned to email list. Email likely marked as read.")
        except:
            print("   ⚠ Could not confirm return to email list.")

        # Short pause between processing emails
        time.sleep(1)

    print("\n✅ Processing of unread emails completed")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    print("📋 Detailed traceback:")
    traceback.print_exc()

finally:
    driver.quit()
