import requests
import time
import random
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import signal
from threading import Event

# Load the .env file
load_dotenv()

### Load env variables here ###
links_file = os.getenv("LINKS_FILE", "output.txt")
session_cookies = os.getenv("SESSION_COOKIES")
download_directory = os.getenv("DOWNLOAD_DIRECTORY", "ResourceDownloads")
output_file = os.getenv("OUTPUT_FILE", "output.txt")
processed_file = os.getenv("PROCESSED_FILE", "processed_output.txt")
log_download_path = os.getenv("LOG_DOWNLOAD_PATH", "download.log")
log_skip_path = os.getenv("LOG_SKIP_PATH", "skip.log")
max_threads = int(os.getenv("MAX_THREADS", 4))  # Default to 4 threads if not specified

game_id = os.getenv("GAME_ID", "1704")
nexus_download_url = os.getenv(
    "NEXUS_DOWNLOAD_URL",
    "https://www.nexusmods.com/Core/Libs/Common/Managers/Downloads?GenerateDownloadUrl",
)
### END - Load env variables here ###

# Shared dictionary to track download statuses
download_status = {}
remaining_files = 0

# Global abort flag
abort_requested = Event()

# Function to handle CTRL+C interrupts
def handle_abort_signal(signum, frame):
    print("\nAborting script... Cleaning up.")
    abort_requested.set()  # Signal all threads to stop immediately

# Register signal handlers
signal.signal(signal.SIGINT, handle_abort_signal)

# Function to read links from the file
def read_links(file_path):
    with open(file_path, 'r') as file:
        links = [line.strip() for line in file.readlines()]
    return links

# Function to extract file_id and game_id from the URL
def extract_ids_from_url(url):
    match = re.search(r"file_id=(\d+)", url)
    if match:
        file_id = match.group(1)
        game_id = game_id
        return file_id, game_id
    else:
        return None, None

# Function to make the POST request and get the download URL
def make_post_request(referer_url, file_id, game_id):
    if abort_requested.is_set():
        return None  # Stop if abort is requested

    url = nexus_download_url
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en,de;q=0.9,de-DE;q=0.8,en-US;q=0.7",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.nexusmods.com",
        "Referer": referer_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": session_cookies,
    }
    data = {"fid": file_id, "game_id": game_id}

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        try:
            response_data = response.json()
            if isinstance(response_data, list):
                return response_data[0].get("url", "")
            else:
                return response_data.get("url", "")
        except ValueError:
            pass
    return None

# Function to download a file and update progress
def download_file(download_url, referer_url, link):
    global download_status

    try:
        os.makedirs(download_directory, exist_ok=True)
        file_name = download_url.split("/")[-1].split("?")[0]
        file_path = os.path.join(download_directory, file_name)

        if os.path.exists(file_path):
            with open(log_skip_path, "a") as skip_log:
                skip_log.write(f"Skipped: {file_name} (already exists) - URL: {referer_url}\n")
            download_status[link] = {"status": "Skipped", "percentage": 100, "speed": 0}
            return

        response = requests.get(download_url, stream=True)

        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            start_time = time.time()

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if abort_requested.is_set():
                        download_status[link] = {"status": f"Aborted", "percentage": 0, "speed": 0}
                        return  # Stop downloading immediately if abort is requested

                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)

                        # Update progress and speed
                        elapsed_time = time.time() - start_time
                        percentage = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                        speed = (downloaded_size / elapsed_time) / 1024 if elapsed_time > 0 else 0

                        download_status[link] = {
                            "status": f"Downloading...",
                            "percentage": percentage,
                            "speed": speed,
                        }

            with open(log_download_path, "a") as download_log:
                download_log.write(f"{referer_url}\n")

            download_status[link] = {"status": "Completed", "percentage": 100, "speed": 0}

        else:
            download_status[link] = {"status": f"Failed (HTTP {response.status_code})", "percentage": 0, "speed": 0}

    except Exception as e:
        download_status[link] = {"status": f"Error: {str(e)}", "percentage": 0, "speed": 0}

# Function to process a single link
def process_link(link):
    global remaining_files

    # Reset download status before starting
    download_status[link] = {"status": "Requesting URL...", "percentage": 0, "speed": 0}

    referer_url = link
    file_id, game_id = extract_ids_from_url(referer_url)
    if file_id and game_id:
        download_url = make_post_request(referer_url, file_id, game_id)
        if download_url:
            download_file(download_url, referer_url, link)
    else:
        download_status[link] = {"status": f"Invalid URL", "percentage": 0, "speed": 0}

    remaining_files -= 1

# Function to render the status lines in the console
def render_console(links):
    global remaining_files

    os.system("cls" if os.name == "nt" else "clear")  # Clear console for clean output

    # Calculate total combined speed across all active downloads
    total_speed = sum(status.get("speed", 0) for status in download_status.values())

    # Line 1: Remaining files count and combined speed
    print(f"{remaining_files}/{len(links)} remaining | Total Speed: {total_speed:.2f} KB/s")

    # Lines 2–5: Display up to four active downloads with their stats
    active_links = [link for link in list(download_status.keys()) if not download_status[link]["status"] in ["Skipped", "Completed"]][:4]
    for link in active_links:
        status_info = download_status.get(link, {})
        status_text = status_info.get("status", "")
        percentage_text = f"{status_info.get('percentage', 0):.2f}%"
        speed_text = f"{status_info.get('speed', 0):.2f} KB/s"
        print(f"[{link}] {status_text} | {percentage_text} | {speed_text}")

if __name__ == "__main__":
    links = read_links(links_file)
    remaining_files = len(links)

    # Initialize all links with a default status
    for link in links:
        download_status[link] = {"status": "Pending", "percentage": 0, "speed": 0}

    with ThreadPoolExecutor(max_threads) as executor:
        futures = [executor.submit(process_link, link) for link in links]
        
        while any(future.running() for future in futures):  
            render_console(links)
            time.sleep(1)

            # Stop rendering if abort is requested.
            if abort_requested.is_set():
                break
        
