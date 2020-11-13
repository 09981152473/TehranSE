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


def trends(market, number):
    url = "http://tsetmc.com/Loader.aspx"
    payload = {"Partree": "151317", "Type": "MostVisited", "Flow": market}

    htmlfile = session.get(url, params=payload)
    htmlfile = htmlfile.text

    soup = BeautifulSoup(htmlfile, "html.parser")
    rows = soup.find("tbody").find_all("tr")

    mostvisited = {}
    for row in rows[:number]:
        values = row.find_all("td")

        inscode = findall(r"i=(.+)", values[0].find("a").get("href"))[0]
        sharename = values[0].string
        companyname = values[1].string
        py = int(values[2].string.replace(",", ""))
        pc = int(values[3].string.replace(",", ""))
        pcc = int(values[4].string) if values[4].div and values[4].div["class"][0] == "pn" else -1*(int(values[4].string.replace(")", "").replace("(", "")))
        pcp = float(values[5].string) if values[5].div and values[5].div["class"][0] == "pn" else -1*(float(values[5].string.replace(")", "").replace("(", "")))
        pl = int(values[6].string.replace(",", ""))
        plc = int(values[7].string) if values[7].div and values[7].div["class"][0] == "pn" else -1*(int(values[7].string.replace(")", "").replace("(", "")))
        plp = float(values[8].string) if values[8].div and values[8].div["class"][0] == "pn" else -1*(float(values[8].string.replace(")", "").replace("(", "")))
        pmin = int(values[9].string.replace(",", ""))
        pmax = int(values[10].string.replace(",", ""))
        tno = int(values[11].string.replace(",", ""))
        tvol = int(values[12].div["title"].replace(",", "")) if values[12].div else int(values[12].string.replace(",", ""))
        tval = int(values[13].div["title"].replace(",", "")) if values[13].div else int(values[13].string.replace(",", ""))

        mostvisited.update({
            inscode: {
                "sharename": sharename,
                "companyname": companyname,
                "py": py,
                "pc": pc,
                "pcc": pcc,
                "pcp": pcp,
                "pl": pl,
                "plc": plc,
                "plp": plp,
                "pmin": pmin,
                "pmax": pmax,
                "tno": tno,
                "tvol": tvol,
                "tval": tval,
            }
        })

    return mostvisited

if __name__ == "__main__":
    pass
