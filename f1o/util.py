import urllib.request


async def check_f1owebite_status():
    code = urllib.request.urlopen("https://www.f1-onlineliga.com/").getcode()
    return code

