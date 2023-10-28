# WebLinkDownloader

WebLinkDownloader is a Python script that allows users to easily extract and download files from a webpage based on specific filters like file extension and filename substring. The downloads are shown with a progress bar that displays the download speed and the percentage of the file that has been downloaded.

## Dependencies

- `requests`: Used for making HTTP requests and downloading files.
- `beautifulsoup4`: Used for parsing HTML and extracting links.
- `tqdm`: Used for displaying the download progress bar.

## Setup

1. Ensure you have Python 3 installed. You can download it from [Python's official website](https://www.python.org/downloads/).

2. Clone the repository:

    ```bash
    git clone [your_repository_link]
    cd [repository_directory]
    ```

3. Create a virtual environment (optional but recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```

4. Install the required dependencies:

    ```bash
    pip install requests beautifulsoup4 tqdm
    ```

## Usage

Use the script by providing the necessary arguments:

```bash
python get_all_links.py --filtered_name="<filtered_string>" --website_url="<website_url>" --download_path="/path/to/download/folder/"
```

## Arguments

--filtered_name: A substring of the filenames you're interested in downloading.
--website_url: The webpage from which you want to download files.
--download_path: The local directory where the downloaded files should be saved.
During the download, you can view the progress of each file. To quit the download prematurely, press 'q' or 'esc'.

## Author

Andy Gardner
