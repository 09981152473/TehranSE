from re import findall
from bs4 import BeautifulSoup
from requests import Session

session = Session()


def effective(market, number):
    url = "http://tsetmc.com/Loader.aspx"
    payload = {"Partree": "151316", "Flow": market}

    htmlfile = session.get(url, params=payload)
    htmlfile = htmlfile.text

    soup = BeautifulSoup(htmlfile, "html.parser")
    rows = soup.find("tbody").find_all("tr")

    theeffective = {}
    for row in rows[:number]:
        values = row.find_all("td")

        inscode = findall(r"i=(.+)", row.find("a").get("href"))[0]
        sharename = values[0].string
        companyname = values[1].string
        pc = int(values[2].string.replace(",", ""))
        effect = -1*float(values[3].string.replace("(", "").replace(")", "")) if "(" in values[3].string else float(values[3].string)

        theeffective.update({
            inscode: {
                "sharename": sharename,
                "companyname": companyname,
                "pc": pc,
                "effect": effect
            }
        })

    return theeffective

if __name__ == "__main__":
    pass
