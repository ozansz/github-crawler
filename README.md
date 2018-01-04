# github-crawler
A basic utility for crawling users and e-mails of users

## Usage Example
Just type
```
$ python crawl.py --config example/users.txt --proxies example/proxies.txt --uagents example/uagents.txt
```
The script will create text files filled with user names according to the user configuration file, and then create text files filled with user e-mails (or maybe more...) usşng these user names.

The script will save these files within the directory "GitHub_Crawler" by default. You can also change the name of this directory passing an argument more:
```
$ python crawl.py --config example/users.txt --proxies example/proxies.txt --uagents example/uagents.txt --dir CustomDir
```

### About User Configuration File
The syntax for the conf file is as following:
```
city_id::city_name::starting_page::ending_page
```
