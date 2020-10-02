from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
import time

global TEST_MODE
TEST_MODE = False

global dataListDict
dataListDict = []

global keysList
keysList = ["Enroll date", "URL", "Register no.", "Given Name", "Profile Name", "Labs", "Quests"]


def addError(err, data):
    global dataListDict
    err = "E: " + err
    dataListDict.append({"Enroll date": data[0], "URL": data[3], "Register no.": data[2], "Given Name": data[1], "Profile Name": err})


def getDetailsForProfile(data):
    try:
        r = requests.get(data[3])
    except:
        addError("Invalid URL", data)
        return

    soup = BeautifulSoup(r.content, 'html.parser')

    name_h1 = soup.find("h1", {"class": "l-mbm"})
    labs_quests_p = soup.find("p", {"class": "public-profile__hero__details"})
    badges_divs = soup.find_all("div", {"class": "public-profile__badge"})

    if name_h1 is None:
        addError("Not found", data)
        return

    global dataListDict
    global keysList
    
    temp_dict = {}
    temp_dict["Enroll date"] = data[0]
    temp_dict["Given Name"] = data[1]
    temp_dict["Register no."] = data[2]
    temp_dict["URL"] = data[3]

    name = name_h1.text.strip()
    labs_quests = labs_quests_p.text.strip().rsplit("\n")

    temp_dict["Profile Name"] = name[:-1]
    temp_dict["Labs"] = labs_quests[0]
    temp_dict["Quests"] = labs_quests[3]
    
    for badge in badges_divs:
        b_arr = badge.text.strip().rsplit("\n")
        temp_dict[b_arr[0]] = b_arr[4]
        if b_arr[0] not in keysList:
            keysList.append(b_arr[0])
    
    dataListDict.append(temp_dict)


if __name__ == "__main__":
    start_time = time.time()
    if TEST_MODE:
        print("TEST_MODE: ON")
        file_name = 'test_urls.csv'
    else:
        file_name = 'profile_urls.csv'

    total_count = 0
    with open(file_name, mode ='r') as file:
        csvFile = csv.reader(file)
        next(csvFile)
        total_count = sum(1 for row in csvFile)
        print("Total entries:", total_count)

    with open(file_name, mode ='r') as file:  
        csvFile = csv.reader(file)
        next(csvFile)
        
        i = 0
        for lines in csvFile:
            getDetailsForProfile(lines)
            i += 1
            if i % 5 == 0:
                print(i, "/", total_count, "profiles analysed")
    
    
    print("Saving data")

    todayFileName = datetime.today().strftime('%Y-%m-%d')
    if TEST_MODE:
        todayFileName = todayFileName + "-test.csv"
    else:
        todayFileName = ".\\CSV\\" + todayFileName + ".csv"

    with open(todayFileName, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = keysList)
        writer.writeheader()
        writer.writerows(dataListDict)
    
    diff = time.time() - start_time
    print("Finished in", int(diff/60), "min", "{:7.4f}".format(float(diff%60)), "sec")