import urllib
import urllib.request
from bs4 import BeautifulSoup
from tqdm import tqdm
from multiprocessing import Pool
import time
import pickle
import json


from ._argparse_code import _parse_args

def process_paper_links(links: list[str]) -> list[str]:
    """
    Processes a list of paper links, filters out those that contain a branch picker on GitHub, 
    and returns the filtered list of links.
    Args:
        links (list[str]): A list of URLs to process.
    Returns:
        list[str]: A list of filtered URLs that contain a branch picker on GitHub.
    Raises:
        Exception: If an error occurs while processing a link, it will be caught and printed.
    """
    filtered = []
    github_link = None
    try:
        for paper_link in links:
            github_link = urllib.parse.urlunparse(paper_link)
            page = urllib.request.urlopen(github_link)
            soup = BeautifulSoup(page, 'html.parser')
            # look for the branch picker.
            buttons = soup.find_all("button")
            has_branch_picker = any(map(lambda bs: "branch-picker" in str(bs), buttons))
            if has_branch_picker:
                filtered.append(soup)
    except Exception as e:
        if github_link:
            print(f"Page {github_link} produced an error {e}.")
        else:
            print(f"Error: {e}.")
    # prevent too many requests compaint from GitHub
    time.sleep(.5)
    return filtered



if __name__ == '__main__':
    args = _parse_args()
    id = "_".join(args.id.split("/"))
    print(f"Loading from: ./storage/{id}.json")

    with open(f"./storage/{id}.json", 'r') as f:
        links = json.load(f)


    # clean the data.
    filtered_pages = []
    # for papers_links in tqdm(links):
    #    filtered_pages.extend(process_paper_links(papers_links))

    with Pool(1) as p:
        # filtered_pages.extend(tqdm(p.imap(process_paper_links, links), total=len(links)))
        filtered_pages = []
        for link in links:
            filtered_pages.extend(process_paper_links(link))

    with open(f"./storage/{id}_filtered.pkl", 'wb') as f:
        pickle.dump(filtered_pages, f)
