import os
import sys
import csv
import random
import string
from datetime import datetime
from tzlocal import get_localzone

HTML_TEMPLATE_PATH = "TEMPLATE.html"
URL_CSV_PATH = "URL.csv"
URL_HEADER = "https://benjiah.gitee.io/r/r"
TIP = "Usage:\tpython redirect.py www.example.com [xxx]"
DEFAULT_MIN_LENGTH = 3
DEFAULT_GENERATE_CNT_THRESHOLD = 100


def url_csv(path):
    if not os.path.exists(path):
        headers = ['ORIGINAL_URL,REDIRECT_URL,RECORD_TIME', '\n']
        example = ['www.example.com,xxx,2022-08-08 00:00:00 Asia/Shanghai', '\n']
        with open(path, 'w', encoding='utf8', newline='') as f:
            f.writelines(headers)
            f.writelines(example)
    return read_csv(path)


def read_csv(path):
    del_rows = []
    csv_url_no_prefix = []
    csv_redirect = []
    csv_file = csv.reader(open(path, encoding='utf-8'))
    csv_dict = csv.DictReader(open(path, encoding='utf-8'))
    for i, row in enumerate(csv_file):
        if row == [] or "#" in row[0]:
            del_rows.append(i + 1)
        else:
            csv_url_no_prefix.append(row[0].replace("http://", "").replace("https://", ""))
            csv_redirect.append(row[1].lower())
    return csv_url_no_prefix[1:], csv_redirect[1:], csv_dict


def fetch_record(records, url):
    records = list(records)
    for row in records:
        if row["ORIGINAL_URL"] == url:
            return row["REDIRECT_URL"]


def generate_random_str(length):
    if length <= 0:
        length = DEFAULT_MIN_LENGTH
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, length))
    return random_str.lower()


def load_tmpl(path):
    os.chdir(os.path.dirname(__file__))
    with open(path, "r", encoding="utf-8") as f:
        mail_payload = f.read()
        return mail_payload


def make_page(file_name, payload, url, time):
    os.chdir(os.path.dirname(__file__))
    with open(f"r/{file_name}", "w", encoding="utf-8") as f:
        f.write(payload.format(redirect_url=url, time=time))


def append_record(path, data, time):
    with open(path, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        data.append(time)
        writer.writerow(data)


def main():
    generate_cnt = 0
    try:
        input_original_url = sys.argv[1]
        if input_original_url == "-h" or input_original_url == "--help":
            print(TIP)
            return
        if "http" not in input_original_url:
            input_original_url = f"http://{input_original_url}"
        input_original_url_no_prefix = input_original_url.replace("http://", "").replace("https://", "")
    except IndexError:
        print("\033[31mInputError: Missing parameters!\nUse -h or --help for more information\033[0m")
        return
    try:
        input_redirect = sys.argv[2].lower()
    except IndexError:
        input_redirect = ""
    csv_data = url_csv(URL_CSV_PATH)
    if input_original_url_no_prefix in csv_data[0]:
        redirect = fetch_record(csv_data[2], input_original_url)
        msg = f"This URL {input_original_url} is existed: {URL_HEADER}/{redirect}"
    else:
        try:
            max_length = max(len(s) for s in csv_data[1][1:])
        except ValueError:
            max_length = DEFAULT_MIN_LENGTH
        while True:
            if input_redirect != "" and input_redirect not in csv_data[1]:
                redirect_url = input_redirect
                break
            else:
                while True:
                    if generate_cnt >= DEFAULT_GENERATE_CNT_THRESHOLD:
                        max_length += 1
                    random_redirect = generate_random_str(max_length)
                    if random_redirect not in csv_data[1]:
                        redirect_url = random_redirect
                        print(f"The specified redirect URL {URL_HEADER}/{input_redirect} already exists.")
                        print(f"New redirect URL: {URL_HEADER}/{redirect_url}")
                        break
                    else:
                        generate_cnt += 1
                break
        now = datetime.now()
        str_now_time = now.strftime("%Y-%m-%d %H:%M:%S %Z") + str(get_localzone())
        make_page(f"{redirect_url}.html", load_tmpl(HTML_TEMPLATE_PATH), input_original_url, str_now_time)
        append_record(URL_CSV_PATH, [input_original_url, redirect_url], str_now_time)
        msg = f"Successful to make the page and append the record. {URL_HEADER}/{redirect_url} -> {input_original_url}"
    print(msg)


if __name__ == '__main__':
    main()
