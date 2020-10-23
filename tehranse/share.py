from csv import reader
from datetime import datetime
from json import loads
from io import StringIO
from os.path import dirname
from re import findall
from xml.etree import ElementTree
from bs4 import BeautifulSoup
from requests import Session


def _fixorders(iorders):
    if len(iorders) < 18:
        iorderslen = 18 - len(iorders)

        for i in range(iorderslen):
            iorders.append("0")

        for iorder in iorders:
            if not iorder.strip():
                iorders.remove(iorder)
                iorders.append("0")

    return iorders


def _strtime(itime):
    itime = str(itime)

    if len(itime) == 5:
        itime = "0" + itime

    itime = itime[:2] + ":" + itime[2:4] + ":" + itime[4:]
    return itime


def _allcorrect(response):
    if response.status_code == 200:
        return response.text

    else:
        raise RuntimeError("Server Does Not Respond")

path = dirname(__file__)
with open(path+"/cache/freefloat.json") as file:
    freefloats = loads(file.read())

session = Session()


class Share:

    def __init__(self, inscode):
        url = "http://tsetmc.com/Loader.aspx"
        payload = {"partree": "15131M", "i": inscode}

        htmlfile = session.get(url, params=payload)
        htmlfile = _allcorrect(htmlfile)

        soup = BeautifulSoup(htmlfile, "html.parser")
        values = soup.find("table").find_all("td")

        self.inscode = inscode
        self.instrumentid = values[1].string
        self.cvalmne = values[3].string
        self.companylatinname = values[5].string  # self naming
        self.csoccsac = values[7].string
        self.companyname = values[9].string  # self naming
        self.sharename = values[11].string.strip()  # self naming
        self.lval30 = values[13].string
        self.cisin = values[15].string
        self.market = values[17].string  # self naming
        self.ccomval = values[19].string
        self.csecval = values[21].string
        self.lsecval = values[23].string
        self.csosecval = values[25].string
        self.lsosecval = values[27].string

    def __str__(self):
        return f"{self.inscode}S"

    def __len__(self):
        return len(self.available())

    @classmethod
    def search(cls, sharename):
        url = "http://tsetmc.com/tsev2/data/search.aspx"
        payload = {"skey": sharename}

        csvfile = session.get(url, params=payload)
        csvfile = _allcorrect(csvfile).replace(";", "\n")
        csvfile = list(reader(StringIO(csvfile)))

        if csvfile:
            inscode = csvfile[0][2]
            return cls(inscode)

        raise ValueError()

    def available(self):
        url = "http://tsetmc.com/tsev2/data/InstTradeHistory.aspx"
        payload = {"i": self.inscode, "Top": 1000000, "A": 0}

        csvfile = session.get(url, params=payload)
        csvfile = _allcorrect(csvfile).replace("@", ",").replace(";", "\n")
        csvfile = list(reader(StringIO(csvfile)))

        dates = []
        for line in csvfile:
            dates.insert(0, int(line[0]))

        return dates

    def inst(self, extra=False):
        url = "http://tsetmc.com/tsev2/data/instinfodata.aspx"
        payload = {"i": self.inscode, "c": self.csecval}

        csvfile = session.get(url, params=payload)
        csvfile = _allcorrect(csvfile).replace(";", "\n").replace("@", ",")
        csvfile = list(reader(StringIO(csvfile)))

        csvfile[2] = _fixorders(csvfile[2])

        theinst = {
            "heven": csvfile[0][0],
            "cetaval": csvfile[0][1].strip(),  # not sure about name maybe it is "cgdsval"
            "pl": int(csvfile[0][2]),
            "pc": int(csvfile[0][3]),
            "pf": int(csvfile[0][4]),
            "py": int(csvfile[0][5]),
            # "unknown": int(csvfile[0][6]),
            # "unknown": int(csvfile[0][7]),
            "tno": int(csvfile[0][8]),
            "tvol": int(csvfile[0][9]),
            "tval": int(csvfile[0][10]),
            # "unknown": csvfile[0][11],
            "deven": int(csvfile[0][12]),
            "ltt": int(csvfile[0][13]),  # self naming
            "plp": round(((int(csvfile[0][2]) - int(csvfile[0][5])) * 100) / int(csvfile[0][5]), 2),
            "pcp": round(((int(csvfile[0][3]) - int(csvfile[0][5])) * 100) / int(csvfile[0][5]), 2),
            "orders": [
                {
                    "zd": int(csvfile[2][0]),
                    "qd": int(csvfile[2][1]),
                    "pd": int(csvfile[2][2]),
                    "po": int(csvfile[2][3]),
                    "qo": int(csvfile[2][4]),
                    "zo": int(csvfile[2][5]),
                },
                {
                    "zd": int(csvfile[2][6]),
                    "qd": int(csvfile[2][7]),
                    "pd": int(csvfile[2][8]),
                    "po": int(csvfile[2][9]),
                    "qo": int(csvfile[2][10]),
                    "zo": int(csvfile[2][11]),
                },
                {
                    "zd": int(csvfile[2][12]),
                    "qd": int(csvfile[2][13]),
                    "pd": int(csvfile[2][14]),
                    "po": int(csvfile[2][15]),
                    "qo": int(csvfile[2][16]),
                    "zo": int(csvfile[2][17]),
                }
            ],
        }

        if csvfile[4]:
            theinst.update({
                "buyivolume": int(csvfile[4][0]),
                "buynvolume": int(csvfile[4][1]),
                "sellnvolume": int(csvfile[4][2]),
                "sellivolume": int(csvfile[4][3]),
                # "unknown": csvfile[4][4],
                "buycounti": int(csvfile[4][5]),
                "buycountn": int(csvfile[4][6]),
                "sellcountn": int(csvfile[4][7]),
                "sellcounti": int(csvfile[4][8]),
                # "unknown": csvfile[4][9],
            })

        if extra:
            url = "http://tsetmc.com/Loader.aspx"
            payload = {"ParTree": "151311", "i": self.inscode}

            htmlfile = session.get(url, params=payload)
            htmlfile = _allcorrect(htmlfile)

            if self.inscode in freefloats:
                freefloat = freefloats[self.inscode]

            else:
                freefloat = findall(r"KAjCapValCpsIdx='(.*?)',", htmlfile)[0].strip()

            eps = findall(r"EstimatedEPS='(.*?)',", htmlfile)[0].strip()
            sectorpe = findall(r"SectorPE='(.*?)',", htmlfile)[0].strip()

            theinst.update({
                "bvol": int(findall(r"BaseVol=(.*?),", htmlfile)[0]),
                "eps": float(eps) if eps else 0,
                "z": int(findall(r"ZTitad=(.*?),", htmlfile)[0]),
                "psgelstamax": float(findall(r"PSGelStaMax='(.*?)',", htmlfile)[0]),
                "psgelstamin": float(findall(r"PSGelStaMin='(.*?)',", htmlfile)[0]),
                "minweek": float(findall(r"MinWeek='(.*?)',", htmlfile)[0]),
                "maxweek": float(findall(r"MaxWeek='(.*?)',", htmlfile)[0]),
                "minyear": float(findall(r"MinYear='(.*?)',", htmlfile)[0]),
                "maxyear": float(findall(r"MaxYear='(.*?)',", htmlfile)[0]),
                "sectorpe": float(sectorpe) if sectorpe else 0,
                "freefloat": float(freefloat) if freefloat else 0,  # self naming
            })

        return theinst

    def clientes(self, number=1):
        url = "http://www.tsetmc.com/tsev2/data/clienttype.aspx"
        payload = {"i": self.inscode}

        csvfile = session.get(url, params=payload)
        csvfile = _allcorrect(csvfile).replace(";", "\n")
        csvfile = list(reader(StringIO(csvfile)))

        theclientes = {}
        for row in csvfile[:number]:
            theclientes.update({
                row[0]: {
                    "buycounti": int(row[1]),
                    "buycountn": int(row[2]),
                    "sellcounti": int(row[3]),
                    "sellcountn": int(row[4]),
                    "buyivolume": int(row[5]),
                    "buynvolume": int(row[6]),
                    "sellivolume": int(row[7]),
                    "sellnvolume": int(row[8]),
                    "buyival": int(row[9]),
                    "buynval": int(row[10]),
                    "sellival": int(row[11]),
                    "sellnval": int(row[12]),
                }
            })

        return theclientes

    def shareholders(self):
        url = "http://www.tsetmc.com/Loader.aspx"
        payload = {"partree": "15131T", "c": self.cisin}

        htmlfile = session.get(url, params=payload)
        htmlfile = _allcorrect(htmlfile)

        soup = BeautifulSoup(htmlfile, "html.parser")
        rows = soup.find_all("tr")

        theshareholders = {}
        holdernumber = 1
        for row in rows[1:]:
            values = row.find_all("td")
            shareholderid = findall(r"'(.+?)'", row.get("onclick"))[0]

            url = "http://www.tsetmc.com/tsev2/data/ShareHolder.aspx"
            payload = {"i": shareholderid}

            csvfile = session.get(url, params=payload)
            csvfile = _allcorrect(csvfile)[:_allcorrect(csvfile).index("#")].replace(";", "\n")
            csvfile = list(reader(StringIO(csvfile)))

            duration = len(csvfile)
            percent = float(values[2].string)

            div = values[1].find('div')
            if div:
                sharevalue = int(div.get("title").replace(",", ""))

            else:
                sharevalue = int(values[1].string.replace(",", ""))

            div = values[3].find('div')
            if div:
                change = int(div.get("title").replace(",", ""))

            else:
                change = int(values[3].string.replace(",", ""))

            theshareholders.update({
                values[0].string+str(holdernumber): {
                    "shareholderid": shareholderid,
                    "sharevalue": sharevalue,
                    "percent": percent,
                    "change": change,
                    "duration": duration,
                }
            })

            holdernumber += 1

        return theshareholders

    def pricehistory(self, number=1):
        url = "http://tsetmc.com/tsev2/data/InstTradeHistory.aspx"
        payload = {"i": self.inscode, "Top": number, "A": 0}

        csvfile = session.get(url, params=payload)
        csvfile = _allcorrect(csvfile).replace("@", ",").replace(";", "\n")
        csvfile = list(reader(StringIO(csvfile)))

        thepricehistory = {}
        for row in csvfile[:number]:
            thepricehistory.update({
                row[0]: {
                    "high": float(row[1]),
                    "low": float(row[2]),
                    "close": float(row[3]),
                    "last": float(row[4]),
                    "first": float(row[5]),
                    "open": float(row[6]),
                    "value": float(row[7]),
                    "volumn": int(row[8]),
                    "openint": int(row[9]),
                }
            })

        return thepricehistory

    def transactions(self, date=0):
        date = int(date)
        dates = self.available()

        today = datetime.now()
        today = int(today.strftime("%Y") + today.strftime("%m") + today.strftime("%d"))

        if date == 0 or date == today:
            date = today

        elif date > 0:
            date = min(dates, key=lambda close: abs(close - date))

        elif date < 0:
            if dates[-1] == today:
                date = dates[date-1]

            else:
                date = dates[date]

        thetransactions = []

        if date == today:
            url = "http://tsetmc.com/tsev2/data/TradeDetail.aspx"
            payload = {"i": self.inscode}

            xmlfile = session.get(url, params=payload)
            xmlfile = _allcorrect(xmlfile)
            xmlfile = ElementTree.fromstring(xmlfile)

            for row in xmlfile:
                # number = int(row[0].text)
                time = row[1].text
                volume = int(row[2].text)
                price = float(row[3].text)

                thetransactions.append({
                    "time": time,
                    "volume": volume,
                    "price": price
                })

        else:
            url = "http://cdn.tsetmc.com/Loader.aspx"
            payload = {"ParTree": "15131P", "i": self.inscode, "d": date}

            htmlfile = session.get(url, params=payload)
            htmlfile = _allcorrect(htmlfile)

            listfile = loads(findall(r"IntraTradeData=(.+?);", htmlfile)[0].replace("'", '"'))

            for row in listfile:
                number = int(row[0])
                time = row[1]
                volume = int(row[2])
                price = int(row[3])
                valid = int(row[4])

                if not valid:

                    thetransactions.insert(number-1, {
                        "time": time,
                        "volume": volume,
                        "price": price
                    })

        return thetransactions

    def orders(self, date=0):
        date = int(date)
        dates = self.available()

        today = datetime.now()
        today = int(today.strftime("%Y") + today.strftime("%m") + today.strftime("%d"))

        if date == 0 or date == today:
            date = today

        elif date > 0:
            date = min(dates, key=lambda close: abs(close - date))

        elif date < 0:
            if dates[-1] == today:
                date = dates[date-1]

            else:
                date = dates[date]

        theorders = {}

        one = {"zd": 0, "qd": 0, "pd": 0, "po": 0, "qo": 0, "zo": 0}
        two = {"zd": 0, "qd": 0, "pd": 0, "po": 0, "qo": 0, "zo": 0}
        three = {"zd": 0, "qd": 0, "pd": 0, "po": 0, "qo": 0, "zo": 0}

        if date == today:
            url = "http://cdn.tsetmc.com/Loader.aspx"
            payload = {'partree': '151321', 'i': self.inscode}

            htmlfile = session.get(url, params=payload)
            htmlfile = _allcorrect(htmlfile)

            listfile = loads(findall(r"BestLimitData=(.+?);", htmlfile)[0].replace("'", '"'))

            if not listfile:
                date = dates[-1]

                url = "http://cdn.tsetmc.com/Loader.aspx"
                payload = {"ParTree": "15131P", "i": self.inscode, "d": date}

                htmlfile = session.get(url, params=payload)
                htmlfile = _allcorrect(htmlfile)
                listfile = loads(findall(r"BestLimitData=(.+?);", htmlfile)[0].replace("'", '"'))

        else:
            url = "http://cdn.tsetmc.com/Loader.aspx"
            payload = {"ParTree": "15131P", "i": self.inscode, "d": date}

            htmlfile = session.get(url, params=payload)
            htmlfile = _allcorrect(htmlfile)

            listfile = loads(findall(r"BestLimitData=(.+?);", htmlfile)[0].replace("'", '"'))

        for row in listfile:
            if int(row[0]) > 83000:
                time = _strtime(row[0])
                place = int(row[1])

                if place == 1:
                    one.update({
                        "zd": int(row[2]),
                        "qd": int(row[3]),
                        "pd": float(row[4]),
                        "po": float(row[5]),
                        "qo": int(row[6]),
                        "zo": int(row[7]),
                    })

                elif place == 2:
                    two.update({
                        "zd": int(row[2]),
                        "qd": int(row[3]),
                        "pd": float(row[4]),
                        "po": float(row[5]),
                        "qo": int(row[6]),
                        "zo": int(row[7]),
                    })

                else:
                    three.update({
                        "zd": int(row[2]),
                        "qd": int(row[3]),
                        "pd": float(row[4]),
                        "po": float(row[5]),
                        "qo": int(row[6]),
                        "zo": int(row[7]),
                    })

                if time in theorders:
                    theorders[time][0].update(one)
                    theorders[time][1].update(two)
                    theorders[time][2].update(three)

                else:
                    theorders.update({
                        time: [{}, {}, {}]
                    })

                    theorders[time][0].update(one)
                    theorders[time][1].update(two)
                    theorders[time][2].update(three)

        return theorders

if __name__ == "__main__":
    pass
