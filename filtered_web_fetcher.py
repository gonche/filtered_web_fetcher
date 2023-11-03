import os
import sys
import requests
from bs4 import BeautifulSoup
import hashlib
from tqdm import tqdm
import argparse
import threading

def get_all_links(url):
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    return [a['href'] for a in soup.find_all('a', href=True) if a.text]

def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

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
            size = file.write(data)
            bar.update(size)

    return filename

def generate_md5(filename, block_size=2**20):
    md5 = hashlib.md5()
    with open(filename, 'rb') as file, tqdm(
            desc=f"Generating MD5 for {filename}",
            total=os.path.getsize(filename),
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        while True:
            data = file.read(block_size)
            if not data:
                break
            md5.update(data)
            bar.update(len(data))
    return md5.hexdigest()

def main():
    parser = argparse.ArgumentParser(description='Download and verify files from a URL.')
    parser.add_argument('--website_url', type=str, required=True, help='URL to fetch links from')
    parser.add_argument('--download_path', type=str, required=True, help='Path to download files to')
    parser.add_argument('--filtered_name', type=str, required=True, help='String to filter desired files')
    parser.add_argument('--md5', action='store_true', help='Enable MD5 generation and verification')
    args = parser.parse_args()

    base_url = args.website_url.rstrip('/')
    link_list = get_all_links(args.website_url)

    allowed_extensions = ['.zip', '.cue', '.iso', '.bin']
    filtered_files = [
        base_url + '/' + link.replace('%20', ' ')
        for link in link_list
        if any(link.endswith(ext) for ext in allowed_extensions) and args.filtered_name in link
    ]

    md5sums = {}
    if args.md5:
        for file_url in filtered_files:
            downloaded_file = download_file(file_url, args.download_path)
            md5sums[downloaded_file] = generate_md5(downloaded_file)

        # You would replace this with how you retrieve your stored MD5 checksums.
        stored_md5s = {}  # Placeholder for stored MD5 values

        for file, md5 in tqdm(md5sums.items(), desc="Verifying MD5s"):
            if file in stored_md5s and md5 != stored_md5s[file]:
                print(f"MD5 mismatch for {file}. Expected {stored_md5s[file]} but got {md5}.")

if __name__ == '__main__':
    main()
