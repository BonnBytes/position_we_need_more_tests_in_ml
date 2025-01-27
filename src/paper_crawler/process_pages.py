"""This module allows parsing the github pages. It extracts file and folder names."""

import pickle
from collections import Counter

from tqdm import tqdm

from ._argparse_code import _parse_args

# def search_folders_and_files(str) -> list[str]:
#    pass

def extract_stats(paper_soup_and_link) -> list[dict[str, bool]]:
    # Second position is the page link, use for debugging.
    soup, _ = paper_soup_and_link

    # filter language, find spans first
    python_span = list(
        filter(
            lambda span: "Python" in str(span),
            soup.find_all("span"),
        )
    )

    folders_and_files = list(
        filter(
            lambda table: "folders-and-files" in str(table),
            soup.find_all("table"),
        )
    )[0]
    cells = list(
        filter(
            lambda td: "row-name-cell" in str(td),
            folders_and_files.find_all("td"),
        )
    )

    folders = []
    files = []
    for cell in cells:
        if "icon-directory" in str(cell):
            folders.append(cell.text)
        else:
            files.append(cell.text)

    interesting_files = [
        "requirements.txt",
        "noxfile.py",
        "LICENSE",
        "README.md",
        "README.rst",
        "tox.toml",
        "tox.ini",
        "setup.py",
        "setup.cfg",
        "pyproject.toml",
    ]
    interesting_folders = ["test", "tests", ".github/workflows"]

    result_dict = {}
    result_dict["files"] = {}
    result_dict["folders"] = {}
    result_dict["python"] = {}
    for interesting_file in interesting_files:
        result_dict["files"][interesting_file] = interesting_file in files

    for interesting_folder in interesting_folders:
        result_dict["folders"][interesting_folder] = (
            interesting_folder in folders
        )
    if python_span:
        result_dict["python"]["uses_python"] = True

    results.append(result_dict)
    return results


if __name__ == "__main__":
    args = _parse_args()
    id = "_".join(args.id.split("/"))
    print(f"./storage/{id}_filtered.pkl")

    with open(f"./storage/{id}_filtered.pkl", "rb") as f:
        paper_pages = pickle.load(f)

    results = []

    # todo remove after recrawl.
    paper_pages2 = []
    for pp in paper_pages:
        paper_pages2.extend(pp)
    paper_pages = paper_pages2

    error_counter = 0
    for paper_soup_and_link in tqdm(paper_pages):
        # folders and files exists once per page.
        try:
            results = extract_stats(paper_soup_and_link)
        except Exception as e:
            print(f"Error: {e}")
            error_counter += 1

    print(f"Problems {error_counter}.")
    files = []
    for res in results:
        files.extend(
            list(filter(lambda res: res[1] is True, list(res["files"].items())))
        )

    python_use = []
    for res in results:
        python_use.extend(
            list(filter(lambda res: res[1] is True, list(res["python"].items())))
        )
    python_counter = Counter(python_use)
    python_total = list(python_counter.items())[0][1]

    file_counter = Counter(files)
    page_total = len(results)

    print(f"Python total: {python_total}.")
    print(f"Python share: {python_total / float(page_total)}.")

    print("Files:")
    print(f"total: {file_counter.items()} of {page_total}")
    print(
        f"ratios: {[(mc[0], mc[1] / float(page_total)) for mc in file_counter.items()]}"
    )
    print(
        f"python-ratios: {[(mc[0], mc[1] / float(python_total)) for mc in file_counter.items()]}"
    )    

    folders = []
    for res in results:
        folders.extend(
            list(filter(lambda res: res[1] is True, list(res["folders"].items())))
        )

    folders_counter = Counter(folders)
    print("Folders")
    print(f"total: {folders_counter.items()} of {page_total}")
    print(
        f"ratios: {[(mc[0], mc[1] / float(page_total))
                   for mc in folders_counter.items()]}"
    )

    with open(f"./storage/stored_counters_{id}.pkl", "wb") as f:
        pickle.dump({"files": file_counter,
                     "folders": folders_counter,
                     "language":  python_counter}, f)
