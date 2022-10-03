import pandas as pd
from tqdm import tqdm

from parser import parse_local_txt_page
from scraper import collect_page_links, extract_txt_page_links, download_data

if __name__ == '__main__':
    page_links = collect_page_links()
    txt_page_links = extract_txt_page_links(page_links)
    local_filepaths = download_data(txt_page_links)
    global_df = pd.DataFrame()
    global_questions = []
    for i, path in enumerate(tqdm(local_filepaths)):  # ['sample_file2.txt', 'sample_file.txt']:
        # print(f"Started parsing {path}...", flush=True)
        file_questions, file_df = parse_local_txt_page(path)
        global_df = global_df.append(file_df, ignore_index=True)
        global_questions.extend(file_questions)
        # print(f"Finished parsing {path}.", flush=True)

    global_df.to_csv('../data/yoga_questions.csv', index=False)
