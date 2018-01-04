# github-crawler
A basic utility for crawling users and e-mails of users

## Usage Example
```
$ python crawl.py --config example/users.txt --proxies example/proxies.txt --uagents example/uagents.txt
```

You can change the directory where all files will be saved:
```
$ python crawl.py --config example/users.txt --proxies example/proxies.txt --uagents example/uagents.txt --dir CustomDir
```

### About User Configuration File
The syntax for the conf file is as following:
```
city_id::city_name::starting_page::ending_page
```
