import os
import sys
import csv
import random
import string
from datetime import datetime

HTML_TEMPLATE_PATH = "TEMPLATE.html"
DOMAIN_CSV_PATH = "DOMAIN.csv"


def read_csv(path):
    del_rows = []
    domain = []
    redirect = []
    csv_file = csv.reader(open(path, encoding='utf-8-sig'))
    csv_dict = csv.DictReader(open(path, encoding='utf-8-sig'))
    for i, row in enumerate(csv_file):
        if row == [] or "#" in row[0]:
            del_rows.append(i + 1)
        else:
            domain.append(row[0])
            redirect.append(row[1])
    return domain[1:], redirect[1:], csv_dict


def domain_csv(path):
    if not os.path.exists(path):
        headers = ['DOMAIN,REDIRECT,TIME', '\n']
        example = ['www.example.com,xxx,2022-08-08 00:00:00', '\n']
        with open(path, 'w', encoding='utf8', newline='') as f:
            f.writelines(headers)
            f.writelines(example)
    return read_csv(path)


def append_record(path, data):
    now = datetime.now()
    str_now_time = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(path, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        data.append(str_now_time)
        writer.writerow(data)


def fetch_record(records, domain):
    records = list(records)
    for row in records:
        if row["DOMAIN"] == domain:
            return row["REDIRECT"]


def generate_random_str(length):
    if length <= 0:
        length = 3
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, length))
    return random_str


def make_page(file_name, payload, domain):
    os.chdir(os.path.dirname(__file__))
    with open(f"r/{file_name}", "w", encoding="utf-8") as f:
        f.write(payload.format(redirect_url=domain))


def load_tmpl(path):
    os.chdir(os.path.dirname(__file__))
    with open(path, "r", encoding="utf-8") as f:
        mail_payload = f.read()
        return mail_payload


def main():
    domain = sys.argv[1]
    if "http" not in domain:
        domain = f"http://{domain}"
    try:
        random_redirect = sys.argv[2]
    except IndexError:
        random_redirect = ""
    ret = domain_csv(DOMAIN_CSV_PATH)
    if domain in ret[0]:
        ret = fetch_record(ret[2], domain)
        msg = f"This domain[{domain}] is existed: https://benjiah.gitee.io/r/{ret}"
    else:
        try:
            max_length = max(len(s) for s in ret[1])
        except ValueError:
            max_length = 3
        while True:
            if random_redirect != "":
                break
            random_redirect = generate_random_str(max_length)
            if random_redirect not in ret[1]:
                break
            else:
                max_length += 1
        make_page(f"{random_redirect}.html", load_tmpl(HTML_TEMPLATE_PATH), domain)
        append_record(DOMAIN_CSV_PATH, [domain, random_redirect])
        msg = f"Successful to make the page and append the record. https://benjiah.gitee.io/r/{random_redirect}"
    print(msg)


if __name__ == '__main__':
    """
    Usage:
    python .\redirect_url.py www.example.com [xxx]
    """
    main()
