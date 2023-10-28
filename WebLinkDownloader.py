import requests
from bs4 import BeautifulSoup
import os
import argparse
import hashlib
import json
from tqdm import tqdm
import sys
import threading

def md5(fname, progress_label):
    """Calculate md5 checksum for a file with a progress bar."""
    hash_md5 = hashlib.md5()
    file_size = os.path.getsize(fname)
    with open(fname, "rb") as f:
        with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, desc=progress_label) as bar:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
                bar.update(len(chunk))
    return hash_md5.hexdigest()

# Function to download a file with a progress bar
def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = os.path.join(dest_folder, url.split('/')[-1].replace('%20', ' '))
    r = requests.get(url, stream=True)
    file_size = int(r.headers.get('content-length', 0))

    with open(filename, 'wb') as file, tqdm(
            desc=filename,
            total=file_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in r.iter_content(chunk_size=1024):
            if exit_signal:
                print("Download interrupted!")
                sys.exit(1)  # exit the program
            size = file.write(data)
            bar.update(size)
    return filename.split('/')[-1]  # return the file name for further processing

# Exit checker function to allow quitting with 'q'
exit_signal = False
def exit_checker():
    global exit_signal
    while True:
        if input("Press 'q' to quit: ").lower() == 'q':
            exit_signal = True
            break

def get_all_links(url):
    """Retrieve all links from the specified website."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [link.get('href') for link in soup.find_all('a') if link.get('href')]
    return links

def main():
    parser = argparse.ArgumentParser(description='Download files from a website based on a filtered name.')
    parser.add_argument('--filtered_name', type=str, required=True, help='Name filter for the files to download.')
    parser.add_argument('--website_url', type=str, required=True, help='Website URL to fetch files from.')
    parser.add_argument('--download_path', type=str, required=True, help='Path to save the downloaded files.')
    args = parser.parse_args()

    # Load existing checksums
    if os.path.exists("checksums.json"):
        with open("checksums.json", "r") as f:
            checksums = json.load(f)
    else:
        checksums = {}

    link_list = get_all_links(args.website_url)

    base_url = args.website_url.rstrip('/')  # Make sure there's no trailing slash

    # Filtering and formatting the list
    allowed_extensions = ['.zip', '.cue', '.iso', '.bin']
    filtered_files = [
        base_url + '/' + link.replace('%20', ' ')
        for link in link_list
        if any(link.endswith(ext) for ext in allowed_extensions) and args.filtered_name in link
    ]

    # Start the exit checker in another thread
    thread = threading.Thread(target=exit_checker)
    thread.start()

    # Downloading the filtered files
    for file_url in filtered_files:
        print(f"Downloading {file_url}...")
        downloaded_file_name = download_file(file_url, args.download_path)

        # Generate and verify md5 checksum with progress bar
        print(f"Generating checksum for {downloaded_file_name}...")
        generated_md5 = md5(os.path.join(args.download_path, downloaded_file_name), f"Checksumming {downloaded_file_name}")

        # Compare generated md5 with stored md5, if any ded_file_name] != generated_md5:
            print(f"Checksum mismatch for {downloaded_file_name}. You may want to redownload.")
        else:
            checksums[downloaded_file_name] = generated_md5
            with open("checksums.json", "w") as f:
                json.dump(checksums, f)

    # After all downloads, you can stop the exit checker thread
    thread.join()

if __name__ == "__main__":
    main()
