from requests import post
from sys import argv

BASE_URL = "https://graphql.anilist.co"

class SortableAnime:
    def __init__(self, id, year, reltype, title, frmt):
        self.id = id
        self.year = year if year else 9999
        self.type = reltype
        self.title = title
        self.frmt = frmt

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id
    
    def __str__(self):
        return str(self.title)


def search(query):
    response = post(BASE_URL, json={
        'query': """
            query ($q: String) {
                Media (search: $q) {
                    id
                }
            }
        """,
        'variables': {"q": query}
    })
    if response.ok:
        return response.json()["data"]["Media"]["id"]
    raise ValueError("Show does not exist")

def get_show(id):
    response = post(BASE_URL, json={
        'query': """
            query ($id: Int) {
                Media (id: $id) {
                    id
                    title {
                        english
                        romaji
                    }
                    startDate {
                        year
                    }
                    format
                    relations {
                        nodes {
                            id
                            format
                            startDate {
                                year
                            }
                            title {
                                english
                                romaji
                            }
                        }
                        edges{
                            relationType
                        }
                    }
                }
            }
        """,
        'variables': {"id": id}
    })
    if response.ok:
        return response.json()
    raise ValueError("Bad show")

def get_base_show(res):
    base = res["data"]["Media"]
    return SortableAnime(base["id"], base["startDate"]["year"], "BASE", base["title"], base["format"])

def process_shows(res):
    ls = []
    ls.append(get_base_show(res))
    for i,v in enumerate(res["data"]["Media"]["relations"]["nodes"]):
        ls.append(SortableAnime(v["id"], v["startDate"]["year"], res["data"]["Media"]["relations"]["edges"][i]["relationType"], v["title"], v["format"]))
        pass
    return ls

def main(query):
    items = []
    show_id = search(query)
    res = get_show(show_id)
    items.extend(process_shows(res))
    base_show = get_base_show(res)

    if "PREQUEL" not in [i.type for i in items]:
        season = 1
    else:
        ignore = []
        while True:
            f = False
            for i in items:
                if i.type == "PREQUEL" and i not in ignore:
                    fi = [i for i in process_shows(get_show(i.id)) if i not in items]
                    items.extend(fi)
                    ignore.append(i)
                    f = True
            if not f:
                break
        items = [i for i in items if i.frmt == "TV"]
        items.sort(key=lambda i: i.year)
        season = items.index(base_show)+1
    return season

if __name__ == "__main__":
    print("Season {}".format(main(argv[1])))
