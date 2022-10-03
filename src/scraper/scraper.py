import os
from time import sleep
from typing import List

import numpy as np
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

from constants import ROOT_URL, SEED_URL


def get_soup(page_url: str):
    try:
        response = requests.get(page_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    soup = bs(response.content, 'html.parser')

    sleep(np.random.randint(1, 5))

    return soup


def collect_page_links(
        target_filename: str = '../data/page_links.txt',
        write_links_to_file: bool = True,
) -> List[str]:
    """
    Collects links to pages with questions or returns them from the existing file.

    Parameters
    ----------
    write_links_to_file
    target_filename

    Returns
    -------

    """
    if os.path.exists(target_filename):
        with open(target_filename) as f:
            return f.read().splitlines()

    seed_soup = get_soup(SEED_URL)

    page_links = []

    for link in seed_soup.findAll('a', href=True):
        if link.attrs.get('href', "").startswith('/tour/'):
            page_links.append(ROOT_URL + link.attrs['href'] + '/print')

    # manually crafted list of exceptions
    exceptions = {
        'https://db.chgk.info/tour//print',
        'https://db.chgk.info/tour/SVOYAK/xml/print',
        'https://db.chgk.info/tour/SVTEMA/print',
    }

    if write_links_to_file:
        with open(target_filename, 'w', encoding='utf-8') as links_file:
            for page_link in page_links:
                if page_link not in exceptions:
                    links_file.write(page_link + '\n')

    return page_links


def extract_txt_page_links(
        source_links: List[str],
        target_filename: str = '../data/txt_page_links.txt'
) -> List[str]:
    if os.path.exists(target_filename):
        with open(target_filename) as f:
            return f.read().splitlines()

    txt_links = []

    with open(target_filename, 'w', encoding='utf-8') as links_file:
        for link in tqdm(source_links):
            page_soup = get_soup(page_url=link)

            for link in page_soup.findAll('a', href=True):
                if link.attrs.get('href', "").startswith('/txt/'):
                    txt_link = ROOT_URL + link.attrs.get('href')
                    txt_links.append(txt_link)
                    links_file.write(txt_link + '\n')

    return txt_links


def download_data(txt_links: List[str], root_folder: str = '../data/source_files') -> List[str]:
    local_paths = []
    if not os.path.exists(root_folder):
        os.mkdir(root_folder)
    else:
        return [os.path.join(root_folder, f) for f in os.listdir(root_folder) if f.endswith('.txt')]

    for link in tqdm(txt_links):
        page_text = get_soup(link).text
        local_filepath = os.path.join('..', 'data', 'source_files', link.split('/')[-1])
        with open(local_filepath, 'w', encoding='utf-8') as f:
            f.write(page_text)
        local_paths.append(local_filepath)

    return local_paths
