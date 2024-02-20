import sys
import re
import time
import requests
from termcolor import colored
from datetime import datetime

domain = r'(.*\.com\/.*)'
url = 'http://bora.poodo.site/get_core.php'

def read_config(path):
    config = ['', '']
    file = open(path, 'rt')
    data = file.read()
    file.close
    token = re.compile(r'TOKEN\s+=\s+\"(.*)\"')
    id = re.compile(r'ID\s+=\s+\"(.*)\"')
    config[0] = str(token.findall(data)[0])
    config[1] = id.findall(data)[0]
    return config


def start_scan(ip, tg):
    send_to_tg(f"""
BOROSCANNER
Started scan at {ip}
Target: {url}
               """, tg)


def get_my_addr():
    responce = requests.get("https://ifconfig.me/ip")
    return responce.text


def send_to_tg(data, tg):
    url = f"https://api.telegram.org/bot{tg[0]}/sendMessage?chat_id={tg[1]}&text={data}"
    requests.get(url).json()


def daily_report(tryes, count, date, addr, tg):
    send_to_tg(f"""
BOROSCANNER at {addr}
\U0001F50EMaded {count} scans today!
\U00002705Sucseeded: {tryes['Sucseeded']}
\U0000274CNot Founded: {tryes['NotFounded']}
\U000026A0Site Down: {tryes['SiteDown']}            
Reported: {date}""", tg)
    print(f"Scans today - {count}. Counter dropped!")

    tryes['NotFounded'] = 0
    tryes['SiteDown'] = 0
    tryes['Sucseeded'] = 0

    count = 0
    return count, tryes


def main(addr, tg):
    tryes = {'Sucseeded' : 0, 'SiteDown' : 0, 'NotFounded' : 0}

    if len(sys.argv) < 2:
        print("Please chose scan time!")
        exit()
    counter = 0
    print(colored(rf"""
 ____                 ____                                  
| __ )  ___  _ __ ___/ ___|  ___ __ _ _ __  _ __   ___ _ __ 
|  _ \ / _ \| '__/ _ \___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
| |_) | (_) | | | (_) |__) | (_| (_| | | | | | | |  __/ |   
|____/ \___/|_|  \___/____/ \___\__,_|_| |_|_| |_|\___|_|   
                                          At {addr}
                                          
Target: {url}
""", 'magenta', attrs=['bold']))
    while True:
        current_time = datetime.now()

        if current_time.hour == 0 and current_time.minute == 0 and current_time.second == 0:
            counter, tryes = daily_report(tryes, counter, datetime.now().strftime("%Y-%m-%d %H:%M"), addr, tg)

        print(colored("SEARCHING! - " + str(datetime.now().strftime("%Y-%m-%d %H:%M")), 'cyan', attrs=['bold']))
        try:
            counter += 1
            responce = requests.get(url)
            regex = re.compile(domain)
            if responce.status_code == 200:
                result = re.findall(regex, responce.text)
                if result:
                    size = len(result)
                    string_finded = "FOUNDED! [" + str(size) + "]- " + str(datetime.now().strftime("%Y-%m-%d %H:%M"))
                    print(colored(string_finded, 'green', attrs=['bold']))
                    
                    tryes['Sucseeded'] += 1
                    file = open("output/boro-finded.txt", 'at')
                    to_tg = ''
                    for data in result:
                        file.write(data + '\n')
                        print(colored(data, 'green'))
                        to_tg += data + '\n'
                    send_to_tg('\U00002757' + string_finded + '\n' + to_tg.replace(".", "[.]"), tg)

                    file.close
                else:
                    tryes['NotFounded'] += 1
                    print(colored("NOT FOUNDED!", 'yellow', attrs=['bold']))
            else:
                tryes['SiteDown'] += 1
                print(colored("SITE NOT WORKING - " + str(datetime.now().strftime("%Y-%m-%d %H:%M")), 'red', attrs=['bold']))
            time.sleep(int(sys.argv[1]))
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            exit()
        except:
            send_to_tg("SOME ERROR WHILE WORKING!", tg)
            print(Exception)


if __name__ == "__main__":
    config = 'boro.conf'
    tg = read_config(config)
    if not tg[0] or not tg[1]:
        print(f"Config error! Check config-file {config}")
        exit()
    start_scan(get_my_addr(), tg)
    main(get_my_addr(), tg)