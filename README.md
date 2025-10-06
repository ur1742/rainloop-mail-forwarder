# RainLoop Mail Forwarder

This Python script automates the process of forwarding unread emails from a RainLoop webmail interface to another email address using Selenium WebDriver.

## Features

*   **Automated Login**: Logs into RainLoop using provided credentials.
*   **Unread Email Detection**: Finds emails marked as unread (using the `.unseen` CSS class).
*   **Forwarding**: Initiates the forwarding process for each unread email by clicking the forward button within the email list item.
*   **Form Population**: Fills the "To" field in the forwarding form with a specified email address.
*   **Sending**: Submits the forwarding form to send the email.
*   **Headless Operation**: Runs in headless mode by default, suitable for background execution.
*   **Periodic Execution**: Designed to be run periodically (e.g., via `cron`) to check for new emails.

## Prerequisites

*   Python 3.x
*   `selenium`
*   `webdriver-manager`
*   Chrome or Chromium browser installed (for `chromedriver` managed by `webdriver-manager`)

## Installation

1.  **Clone the repository or download the script.**
2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (Ensure `requirements.txt` contains `selenium` and `webdriver-manager` as specified earlier).

## Configuration

1.  **Edit the script (`mail.py`):**
    *   Set the `login_url` to your RainLoop instance (e.g., `https://your-webmail-domain.com`).
    *   Set the `username` and `password` for your RainLoop account.
    *   Set the `yandex_email` (or any other email address) to which you want to forward the emails.
    *   Adjust the `chrome_options` if needed (currently configured for headless operation).
    *   Adjust the `wait` timeout values if necessary for your network/system speed.

2.  **(Optional) Create a `cron` job:**
    *   To run the script every 10 minutes, add the following line to your crontab (`crontab -e`):
        ```cron
        */10 * * * * /path/to/your/python /path/to/this/script/mail.py >> /path/to/logfile.log 2>&1
        ```
        Replace `/path/to/your/python`, `/path/to/this/script/mail.py`, and `/path/to/logfile.log` with the actual paths on your system.

## Usage

### Direct Execution

Run the script directly using Python:

```bash
python mail.py
