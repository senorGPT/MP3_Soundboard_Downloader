import os
import re
import sys
import requests
from typing import List
from bs4 import BeautifulSoup

BASE_URL = "https://www.realmofdarkness.net"
TARGET_URL = "https://www.realmofdarkness.net/sb/soundboards/"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Length": "164",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "__utmc=96992031; __utmz=96992031.1649729265.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); csrftoken=XEhQotC9KXDt2aUweeKuhNbkCDJD0RDDtbrmTyRA1v1QnmZNzntlQxCSIg32wcrB; sessionid=6z5clvhmck08jz88o1covty67sq81arp; __utma=96992031.269134897.1649729265.1649729265.1649739572.2; __utmt=1; __utmb=96992031.35.10.1649739572",
    "sec-ch-ua": '"Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}
UNWANTED_URLS = [
    "https://www.realmofdarkness.net/sb/",
    "https://www.realmofdarkness.net/sb/soundboards",
    "https://www.realmofdarkness.net/sb/contact",
    "https://www.realmofdarkness.net/sb/privacy",
]

# TODO: document code
# TODO: improve UI output of console
# TODO: document code examples
# TODO: rename file to main.py
# TODO: log functionality
# TODO: command line functionality
# TODO: format file properly
# TODO: sanitize names properly
# TODO: try/catch to not error out?

MATCHING_SCRIPT_REGEX = r'<script src="\/scripts\/sb\/.*?\/sounds\.js">'


def get_website_title(title_text: str) -> str:
    """
    Return the first 250 characters of `title_text` with colons removed

    Parameters:
        title_text (str): Current title of webpage as a string

    Returns:
        str: first 250 characters of `title_text` with colons removed

    Example:
        get_website_title('Hank Hill Soundboard: King of the Hill - Season 1 - Realm of Darkness.net - Soundboards for Mobile, Android, iPhone, iPad, iOS, Tablet, PC, Sounds)
    """
    return title_text.split(" - Realm")[0][:250].replace(":", "")


def get_all_soundboard_file_names(sounds_js_url: str) -> List[str]:
    """
    Sanitize and clean JS containing all soundboard sound names and their path on target server within `sounds_js_url`

    Parameters:
        sounds_js_url (str): JSON containing soundboard sound names and their paths

    Returns:
        List[str]: Each element represents a sound and its path

    Example:
        get_all_soundboard_file_names('/scripts/sb/koth/hank/1/sounds.js')
    """
    # get the json from the endpoint & clean it up
    sounds_js_request = requests.get(BASE_URL + sounds_js_url)
    sounds = (
        sounds_js_request.content.decode("utf-8")
        .replace("\t", "")
        .replace("\r", "")
        .replace(",", "")
        .replace('"', "")
        .split("\n")
    )

    # pop the first, second and last line as they dont contain any name
    sounds.pop(0)
    sounds.pop(0)
    sounds.pop()

    return sounds


def download_and_save_mp3s(dir: str, audio_url: str, file_names: List[str]) -> None:
    """
    Download all soundboard files `file_names` from endpoint `audio_url` and save them in a folder named `dir`.

    Parameters:
        dir (str): Name for folder in which all soundboard files will be downloaded to
        audio_url (str): Target endpoint for current soundboard. MUST contain a string formatter '%s' to function correctly
        file_names (List[str]): Soundboard file names to download from `audio_url` endpoint

    Returns:
        None

    Example:
        download_and_save_mp3s(
            'Hank Hill Soundboard King of the Hill - Season 1',
            '/audio/koth/hank/1/%s.mp3',
            [
                '1-st-a', '1-st-b', '1-st-c', '1-st', '113', '13', '1995', '2', '3', '30', '75gall', 'abs', 'ahh',
                'alrighty', 'anyharder', 'apologize-2', 'apologize-3', 'apologize-4', 'apologize', 'baby', 'bacongrease',
                'beer', 'bestburger', 'betsy', 'betsyhs-2', 'betsyhs', 'bill', 'bobby-2', ...
            ])
    """
    print("Downloading to:", os.path.join(os.getcwd(), f"sounds/{dir}/"))
    # fancy downloading bar
    sys.stdout.write(
        f"\r[{100*' '}] {0:0>{len(str(len(file_names)))}}/{len(file_names):0>{len(str(len(file_names)))}}"
    )
    for index, sound_file in enumerate(file_names):
        int_percentage = int((((index + 1) / len(file_names)) * 100) // 1)

        sys.stdout.flush()
        sys.stdout.write(
            f"\r[{int_percentage*'='}{(100-int_percentage)*' '}] {(index + 1):0>{len(str(len(file_names)))}}/{len(file_names):0>{len(str(len(file_names)))}}"
        )

        req = requests.get(BASE_URL + (audio_url % sound_file))
        with open(
            os.path.join(os.getcwd(), f"sounds/{dir}/{sound_file}.mp3"), "wb"
        ) as f:
            f.write(req.content)
    print("")


def download_all_soundboard_files(dir: str, audio_url: str, file_names: List[str]) -> None:
    """
    Download all soundboard files. Check /sounds directory for matching soundboard files prior to attempting download.
    Removing any matching files from `file_names` if found
    
    Parameters:
        dir (str): Name for folder in which all soundboard files will be downloaded to
        audio_url (str): Target endpoint for current soundboard. MUST contain a string formatter '%s' to function correctly
        file_names (List[str]): Soundboard file names to download from `audio_url` endpoint

    Returns:
        None

    Example:
        download_all_soundboard_files(
            'Hank Hill Soundboard King of the Hill - Season 1',
            '/audio/koth/hank/1/%s.mp3',
            [
                '1-st-a', '1-st-b', '1-st-c', '1-st', '113', '13', '1995', '2', '3', '30', '75gall', 'abs', 'ahh',
                'alrighty', 'anyharder', 'apologize-2', 'apologize-3', 'apologize-4', 'apologize', 'baby', 'bacongrease',
                'beer', 'bestburger', 'betsy', 'betsyhs-2', 'betsyhs', 'bill', 'bobby-2', ...
            ])
    """
    # keep track of the number of songs skipped
    skipped_files = 0
    # make the directory if it doesnt exist
    if not os.path.isdir(os.path.join(os.getcwd(), f"sounds/{dir}/")):
        os.makedirs(os.path.join(os.getcwd(), f"sounds/{dir}/"))
    else:
        # skip and remove any files that already exist
        for x in range(len(file_names) - 1, -1, -1):
            if os.path.isfile(
                os.path.join(os.getcwd(), f"sounds/{dir}/{file_names[x]}.mp3")
            ):
                skipped_files += 1
                file_names.pop(x)
        if skipped_files > 0:
            print(f"Skipped {skipped_files} Sounds : Files already exist")
    # dont proceed if we dont have any files to download left
    if len(file_names) == 0:
        return

    download_and_save_mp3s(dir, audio_url, file_names)
    

def scrape_soundboard(url: str) -> None:
    """
    Find and download all soundboard files for target soundboard `url`

    Parameters:
        url (str): URL for target soundboard

    Returns:
        None

    Example:
        scrape_soundboard('https://www.realmofdarkness.net/sb/koth-hank/')
    """
    soundboard_request = requests.get(url)
    matches = re.findall(
        MATCHING_SCRIPT_REGEX, soundboard_request.content.decode("utf-8")
    )

    soup = BeautifulSoup(soundboard_request.content, "html.parser")
    soundboard_name = get_website_title(soup.find("title").text)
    # skip if we found no matching JSON to request
    if not len(matches):
        return

    sounds_js_url = matches[0].split('"')[1]
    audio_file_url = (
        "/audio/"
        + sounds_js_url.replace("/scripts/sb/", "").replace("/sounds.js", "")
        + "/%s.mp3"
    )

    sounds = get_all_soundboard_file_names(sounds_js_url)
    print(f"\n\nFound {len(sounds)} sound files for {url}")
    download_all_soundboard_files(soundboard_name, audio_file_url, sounds)


# TODO: possibly break this function up into smaller functions
def get_all_categories(target_url: str, soundboard_list: List[str], visited_list: List[str]) -> None:
    """
    Recursive function to go through soundboard categories on realmofdarkness website to discover all
    soundboards in order to download them.

    Parameters:
        target_url (str): Target url to check
        soundboard_list (List[str]): List of soundboards that have been scraped
        visited_list (List[str]): List of pages that this function has already visited as to not double dip

    Returns:
        None

    Example:

    """
    html = requests.get(target_url)
    soup = BeautifulSoup(html.content, "html.parser")
    found_a_tags = soup.find_all("a")

    print(f"SCRAPING {target_url} | Current Found Soundboards: {len(soundboard_list)}")
    # remove any <a> tag elements for un-necessary pages that were picked up,; such as; contact, privacy, home
    for x in range(len(found_a_tags) - 1, -1, -1):
        for unwanted_url in UNWANTED_URLS:
            if f'<a href="{unwanted_url}">' in str(found_a_tags[x]):
                found_a_tags.pop(x)
                continue

    for a_tag in found_a_tags:
        # extract only the information that we are looking for which is contained within the href
        matches = re.findall(
            r'<a href="https://www\.realmofdarkness\.net/sb/.*?">', str(a_tag)
        )
        if len(matches) == 0:
            continue

        soundboard_url = matches[0].split('"')[1]
        # skip any soundboards that we've already scraped
        # visited_list are the pages we've visited that arent soundboards taht we dont want to double back to
        if soundboard_url in soundboard_list or soundboard_url in visited_list:
            continue

        # check if url is a soundboard or a category page by title
        if "Soundboards" in get_website_title(soup.find("title").text):
            visited_list.append(soundboard_url)
            # for match in matches:
            get_all_categories(soundboard_url, soundboard_list, visited_list)
        elif "Soundboard" in get_website_title(soup.find("title").text):
            soundboard_list.append(soundboard_url)
            scrape_soundboard(soundboard_url)


def scrap_soundboard_website() -> None:
    """
    Start scraping realmofdarkness soundboards and download them

    Returns:
        None

    Example:
        scrap_soundboard_website()
    """
    soundboard_list, category_list = [], []
    # TODO: remove me
    print(f"get_all_categories({TARGET_URL}, {soundboard_list}, {category_list})")
    get_all_categories(TARGET_URL, soundboard_list, category_list)


if __name__ == "__main__":
    # scrap_soundboard_website()

    # scrape single soundboard
    scrape_soundboard("https://www.realmofdarkness.net/sb/koth-hank/")
