import sys
import os
import argparse
import crawler

def get_args():
    ap = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]))

    ap.add_argument("-c", "--copyright", help="show license info",
                    action="store_true", required=False)

    ap.add_argument("--config", help="configuration file", default=None)
    ap.add_argument("--proxies", help="proxy list file", default=None)
    ap.add_argument("--uagents", help="user agent list file", default=None)

    ap.add_argument("--dir", help="custom save directory", required=False,
                    default="GitHub_Crawler")

    return ap

if __name__ == '__main__':
    parser = get_args()
    args = parser.parse_args()

    if args.copyright:

        with open("LICENSE", "r") as licF:
            for line in licF:
                print(line[:-1])

        sys.exit(0)

    if not (args.config and args.proxies and args.uagents):
        print("[!] Arguments config, proxies and uagents are required " +
              "together!\n")
        parser.print_help()
        sys.exit(1)

    save_dir = args.dir
    while True:
        try:
            os.mkdir(save_dir)
        except FileExistsError:
            save_dir += "_"
        else:
            break

    os.chdir(save_dir)

    cities_conf = dict()
    with open(args.config, "r") as conF:
        for line in conF:
            elem = line[:-1].split("::")
            cities_conf[elem[0]] = {elem[1] : (elem[2], elem[3])}

    threads = list()
    dev_saves = list()
    for city, _ in cities.items():
        dev_saves.append("developers_{}.txt".format(city))
        threads.append(crawler.GitHubUserCrawler(city, cities_conf[city],
                       out="developers_{}.txt".format(city),
                       proxy_file=args.proxies, uagents_file=args.uagents))

    for thr in threads:
        thr.start()
        thr.join()

    threads = list()
    for city, dev_sf in zip(cities_conf, dev_saves):
        threads.append(crawler.GitHubMailCrawler(city, dev_sf,
                       "{}_mails.txt".format(city), args.proxies,
                       args.uagents))

    for thr in threads:
        thr.start()
        thr.join()

    sys.exit(0)
