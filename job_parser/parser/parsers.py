import requests
from bs4 import BeautifulSoup as bs


# TODO Реализовать смену user-agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Accept": "text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8",
}


def get_jobs_from_superjob(url, city=None, language=None):
    domain = "https://superjob.ru"
    response = requests.get(url=url, headers=headers)

    jobs = []
    errors = []
    if url:
        if response.status_code == 200:
            soup = bs(response.content, "html.parser")
            main_div = soup.find("div", attrs={"class": "_2zPWM _9n5R- _1GAZu"})
            if main_div:
                div_lst = main_div.find_all(
                    "div",
                    attrs={
                        "class": "_2zPWM f-test-vacancy-item _3HN9U gMlhN _1yHIx I2gCw _1Qy3a"
                    },
                )
                for div in div_lst:
                    title = div.find(
                        "span",
                        attrs={
                            "class": "_2s70W _31udi _7mW5l _17ECX _1B2ot _3EXZS _3pAka ofdOE"
                        },
                    )

                    href = title.a["href"]

                    company_div = div.find(
                        "span",
                        attrs={
                            "class": "_3nMqD f-test-text-vacancy-item-company-name _3NJ1T _3EXZS _3pAka _3GChV _2GgYH"
                        },
                    )

                    if company_div is None:
                        company = "Не указано"
                    else:
                        company = company_div.text

                    desc_div = div.find(
                        "span", attrs={"class": "_1G5lt _3EXZS _3pAka _3GChV _2GgYH"}
                    )
                    desc = desc_div.text

                    jobs.append(
                        {
                            "title": title.text,
                            "url": domain + href,
                            "company": company,
                            "description": desc,
                            "city_id": city,
                            "language_id": language,
                        }
                    )
            else:
                errors.append({"url": url, "title": "Div doesn`t exists"})
        else:
            errors.append({"url": url, "title": "Page do not response"})

    return jobs, errors


if __name__ == "__main__":
    url = "https://superjob.ru/vacancy/search/?keywords=java"
    jobs, errors = get_jobs_from_superjob(url)
    with open("work.txt", "w", encoding="utf-8") as file:
        file.write(str(jobs))
