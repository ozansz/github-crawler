import requests as req
from lxml import html
import random
import threading
import os
import re

class JobIsDoneExc(Exception):
    pass

class GitHubUserCrawler(threading.Thread):
    base_url = "https://github.com/search?o=desc&q=location%3A{0}" + \
               "&s=followers&type=Users&p={1}"

    # location_data as dict or str, default output on screen
    def __init__(self, tid, location_data, out, proxy_file, uagents_file):
        threading.Thread.__init__(self)

        self.id = tid

        if type(location_data) != dict:
            if type(location_data) == str:
                _ld = dict()
                with open(location_data, 'r') as dF:
                    elems = dF.readline().split(" ")
                    _ld[elems[0]] = (elems[1], elems[2])

                location_data = _ld

            else:
                raise TypeError('[Th#{}] The argument '.format(self.id) +
                                'location_data MUST be type dict or str.')

        self.loc = location_data
        self.out = out
        self.save = open(self.out, 'a')

        self.crawlog = dict()
        self.devs = dict()

        self.uagents = list()
        with open(uagents_file, 'r') as uf:
            for line in uf:
                self.uagents.append(line[:-1])

        self.uagent = random.choice(self.uagents)
        self.session = req.Session()
        self.session.headers.update({'User-agent' : self.uagent})

        self.proxies = list()
        with open(proxy_file, 'r') as pf:
            for p in pf.readlines():
                self.proxies.append(p[:-1])

        self.curr_proxy = 'http://' + random.choice(self.proxies)

    def run(self):
        while True:
            try:
                self.fuckit()
                self.renew_proxy()

            except (req.exceptions.ProxyError, req.exceptions.SSLError):
                self.renew_proxy()

            except (req.exceptions.Timeout, req.exceptions.ConnectionError):
                print('[Th#{}][!] Got timeout error!'.format(self.id))
                print('[Th#{}][+] Renewing proxy.'.format(self.id))
                self.renew_proxy()

            except (JobIsDoneExc, KeyboardInterrupt):
                self.save.close()
                break

            finally:
                self.renew_uagent()

    def fuckit(self):
        for loc in self.loc.keys():
            self.crawlog[loc] = None
            self.devs[loc] = list()

            for page in range(self.loc[loc][0], self.loc[loc][1] + 1):
                print('\n[Th#{}][i] Page'.format(self.id), page)
                self.loc[loc] = (page, self.loc[loc][1])

                tree = self.gettree(GitHubUserCrawler.base_url.format(
                    loc, page))

                if tree == None:
                    print('[Th#{}][!] Request limits '.format(self.id) + \
                          'fucked us in page #{}!'.format(page))
                    return self.crawlog

                self.crawlog[loc] = page

                for dev in tree.xpath('//div[@class="user-list-info ml-2"]/a'):
                    self.devs[loc].append('https://github.com/' + dev.text)
                    self.save.write(dev.text + '\n')
                    print('[Th#{2}][+] Crawled {0} from {1}'.format(
                        dev.text, loc, self.id))

                    self.save.flush()
                    os.fsync(self.save.fileno())

                if page == self.loc[loc][1]:
                    raise JobIsDoneExc()

    def gettree(self, url):
        pg = self.session.get(url, proxies={'https' : self.curr_proxy},
                              timeout=5)

        if pg.status_code != 200:
            return None

        return html.fromstring(pg.content.decode('utf-8'))

    def renew_uagent(self):
        new_agent = self.uagent
        while new_agent == self.uagent:
            new_agent = random.choice(self.uagents)

        self.session.headers.update({'User-agent' : self.uagent})
        print('\t[Th#{}][i] User agent has been renewed.'.format(self.id))

    def renew_proxy(self):
        new_proxy = self.curr_proxy
        while new_proxy == self.curr_proxy:
            new_proxy = random.choice(self.proxies)

        self.curr_proxy = 'http://' + new_proxy

        print('\t[Th#{}][i] Proxy settings has been changed.'.format(self.id))

class GitHubMailCrawler(threading.Thread):
    rex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    base_url = 'https://api.github.com/users/{}/events/public'

    # location_data as dict or str, default output on screen
    def __init__(self, tid, userlist, out, proxy_file, uagents_file):
        threading.Thread.__init__(self)

        self.id = tid

        if type(userlist) != list:
            if type(userlist) == str:
                _ld = dict()
                with open(userlist, 'r') as dF:
                    elems = dF.readline().split(" ")
                    _ld[elems[0]] = (elems[1], elems[2])

                userlist = _ld

            else:
                raise TypeError('[Th#{}] The argument '.format(self.id) +
                                'userlist MUST be type list or str.')

        self.users = userlist
        self.out = out
        self.save = open(self.out, 'a')

        self.uagents = list()
        with open(uagents_file, 'r') as uf:
            for line in uf:
                self.uagents.append(line[:-1])

        self.uagent = random.choice(self.uagents)
        self.session = req.Session()
        self.session.headers.update({'User-agent' : self.uagent})

        self.proxies = list()
        with open(proxy_file, 'r') as pf:
            for p in pf.readlines():
                self.proxies.append(p[:-1])

        self.curr_proxy = 'http://' + random.choice(self.proxies)

        self.last_usr_indx = 0
        self.losers = dict()

    def run(self):
        while True:
            try:
                self.fuckit()
                self.renew_proxy()

            except (req.exceptions.ProxyError, req.exceptions.SSLError):
                self.renew_proxy()

            except (req.exceptions.Timeout, req.exceptions.ConnectionError):
                print('[Th#{}][!] Got timeout error!'.format(self.id))
                print('[Th#{}][+] Renewing proxy.'.format(self.id))
                self.renew_proxy()

            except (JobIsDoneExc, KeyboardInterrupt):
                self.save.close()
                break

            finally:
                self.renew_uagent()

    def fuckit(self):
        while self.last_usr_indx < len(self.users):
            user = self.users[self.last_usr_indx]

            print('[Th#{}][==>] Looking for'.format(self.id), user)

            pg = self.session.get(GitHubMailCrawler.base_url.format(user),
                                  proxies={'https' : self.curr_proxy})

            if pg.status_code != 200:
                print('[Th#{}][!] User'.format(self.id), user, 'fucked us!')

                try:
                    self.losers[user] += 1
                except KeyError:
                    self.losers[user] = 1

                if self.losers[user] >= 3:
                    self.last_usr_indx += 1

                self.renew_proxy()
                self.renew_uagent()

                continue

            found = list(set(re.findall(GitHubMailCrawler.rex,
                                        pg.content.decode('utf-8'))))

            if found:
                if self.out:
                    self.save.writelines(list(map(lambda s: s+"\n", found)))
                    self.save.flush()
                    os.fsync(self.save.fileno())

                for m in found:
                    print('[Th#{}][+] Found'.format(self.id), m)

            if self.last_usr_indx == len(self.users) - 1:
                raise JobIsDoneExc()

            self.last_usr_indx += 1

    def renew_uagent(self):
        new_agent = self.uagent
        while new_agent == self.uagent:
            new_agent = random.choice(self.uagents)

        self.session.headers.update({'User-agent' : self.uagent})
        print('\t[Th#{}][i] User agent has been renewed.'.format(self.id))

    def renew_proxy(self):
        new_proxy = self.curr_proxy
        while new_proxy == self.curr_proxy:
            new_proxy = random.choice(self.proxies)

        self.curr_proxy = 'http://' + new_proxy

        print('\t[Th#{}][i] Proxy settings has been changed.'.format(self.id))

def crawl_users():
    cities = {"ist" : {'Istanbul' : (1,100)}, "ank" : {'Ankara' : (1,100)},
              "izm" : {'Izmir' : (1,100)}}

    cr1 = GitHubUserCrawler("IST", cities["ist"],
                            out='developers_istanbul.txt',
                            proxy_file='proxies.txt',
                            uagents_file='uagents.txt')
    cr2 = GitHubUserCrawler("ANK", cities["ank"], out='developers_ankara.txt',
                            proxy_file='proxies.txt',
                            uagents_file='uagents.txt')
    cr3 = GitHubUserCrawler("IZM", cities["izm"], out='developers_izmir.txt',
                            proxy_file='proxies.txt',
                            uagents_file='uagents.txt')

    cr1.start()
    cr2.start()
    cr3.start()

    cr1.join()
    cr2.join()
    cr3.join()

def crawl_user_mails():
    users_ist = list()

    with open("developers_istanbul.txt", "r") as df:
        for ln in df:
            users_ist.append(ln[:-1])

    users_ank = list()

    with open("developers_ankara.txt", "r") as df:
        for ln in df:
            users_ank.append(ln[:-1])

    users_izm = list()

    with open("developers_izmir.txt", "r") as df:
        for ln in df:
            users_izm.append(ln[:-1])

    users_ist.reverse()
    users_ank.reverse()
    users_izm.reverse()

    mc_ist = GitHubMailCrawler("IST", users_ist, "istanbul_mails.txt",
                               "proxies.txt", "uagents.txt")
    mc_ank = GitHubMailCrawler("ANK", users_ank, "ankara_mails.txt",
                               "proxies.txt", "uagents.txt")
    mc_izm = GitHubMailCrawler("IZM", users_izm, "izmir_mails.txt",
                               "proxies.txt", "uagents.txt")

    mc_ist.start()
    mc_ank.start()
    mc_izm.start()

    mc_ist.join()
    mc_ank.join()
    mc_izm.join()

if __name__ == '__main__':
    crawl_users()
    crawl_user_mails()
