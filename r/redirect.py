import os
import sys
import csv
import random
import string
from datetime import datetime
from tzlocal import get_localzone

HTML_TEMPLATE_PATH = "TEMPLATE.html"
DOMAIN_CSV_PATH = "DOMAIN.csv"
URL_HEADER = "https://benjiah.gitee.io/r/r"
TIP = "Usage:\tpython redirect.py www.example.com [xxx]"


def domain_csv(path):
    if not os.path.exists(path):
        headers = ['DOMAIN,REDIRECT,TIME', '\n']
        example = ['www.example.com,xxx,2022-08-08 00:00:00', '\n']
        with open(path, 'w', encoding='utf8', newline='') as f:
            f.writelines(headers)
            f.writelines(example)
    return read_csv(path)


def read_csv(path):
    del_rows = []
    csv_domain_no_prefix = []
    csv_redirect = []
    csv_file = csv.reader(open(path, encoding='utf-8'))
    csv_dict = csv.DictReader(open(path, encoding='utf-8'))
    for i, row in enumerate(csv_file):
        if row == [] or "#" in row[0]:
            del_rows.append(i + 1)
        else:
            csv_domain_no_prefix.append(row[0].replace("http://", "").replace("https://", ""))
            csv_redirect.append(row[1])
    return csv_domain_no_prefix[1:], csv_redirect[1:], csv_dict


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


def load_tmpl(path):
    os.chdir(os.path.dirname(__file__))
    with open(path, "r", encoding="utf-8") as f:
        mail_payload = f.read()
        return mail_payload


def make_page(file_name, payload, domain, time):
    os.chdir(os.path.dirname(__file__))
    with open(f"r/{file_name}", "w", encoding="utf-8") as f:
        f.write(payload.format(redirect_url=domain, time=time))


def append_record(path, data, time):
    with open(path, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        data.append(time)
        writer.writerow(data)


def main():
    try:
        domain = sys.argv[1]
        if domain == "-h" or domain == "--help":
            print(TIP)
            return
        if "http" not in domain:
            domain = f"http://{domain}"
        domain_no_prefix = domain.replace("http://", "").replace("https://", "")
    except IndexError:
        print("Missing domain name parameter!\nUse -h or --help for more information")
        return
    try:
        random_redirect = sys.argv[2]
    except IndexError:
        random_redirect = ""
    csv_data = domain_csv(DOMAIN_CSV_PATH)
    print(csv_data[1][1:])
    if domain_no_prefix in csv_data[0]:
        redirect = fetch_record(csv_data[2], domain)
        msg = f"This domain[{domain}] is existed: {URL_HEADER}/{redirect}"
    else:
        try:
            max_length = max(len(s) for s in csv_data[1][1:])
        except ValueError:
            max_length = 3
        while True:
            if random_redirect != "":
                break
            random_redirect = generate_random_str(max_length)
            if random_redirect not in csv_data[1]:
                break
            else:
                max_length += 1
        now = datetime.now()
        str_now_time = now.strftime("%Y-%m-%d %H:%M:%S %Z") + str(get_localzone())
        make_page(f"{random_redirect}.html", load_tmpl(HTML_TEMPLATE_PATH), domain, str_now_time)
        append_record(DOMAIN_CSV_PATH, [domain, random_redirect], str_now_time)
        msg = f"Successful to make the page and append the record. {URL_HEADER}/{random_redirect} -> {domain}"
    print(msg)


if __name__ == '__main__':
    main()
