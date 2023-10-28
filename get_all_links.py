import os
import argparse
import requests
import threading
import sys
from bs4 import BeautifulSoup
from tqdm import tqdm

# Function to get all links from a URL
def get_all_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all <a> tags with href attribute
    links = soup.find_all('a', href=True)
    
    # Extract the actual link using list comprehension
    link_list = [link['href'] for link in links]

    return link_list

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

# Exit checker function to allow quitting with 'q'
exit_signal = False
def exit_checker():
    global exit_signal
    while True:
        if input("Press 'q' to quit: ").lower() == 'q':
            exit_signal = True
            break

def main():
    # Command line argument setup
    parser = argparse.ArgumentParser(description='Download files from a website.')
    parser.add_argument('--filtered_name', type=str, required=True, help='Filter for file name')
    parser.add_argument('--website_url', type=str, required=True, help='URL of the website')
    parser.add_argument('--download_path', type=str, required=True, help='Path for downloaded files')
    args = parser.parse_args()

    # Get all links from the website
    link_list = get_all_links(args.website_url)

    base_url = args.website_url.rstrip('/')  # Make sure there's no trailing slash

    # Filtering and formatting the list
    allowed_extensions = ['.zip', '.cue', '.iso', '.bin']
    filtered_files = [
        base_url + '/' + link.replace('%20', ' ')
        for link in link_list
        if any(link.endswith(ext) for ext in allowed_extensions) and args.filtered_name in link
    ]

    # Printing and downloading the filtered files
    for file_url in filtered_files:
        print(f"Downloading {file_url}...")
        download_file(file_url, args.download_path)

    print("All downloads completed.")

if __name__ == "__main__":
    # Starting the exit checker in a separate thread
    threading.Thread(target=exit_checker, daemon=True).start()
    main()
