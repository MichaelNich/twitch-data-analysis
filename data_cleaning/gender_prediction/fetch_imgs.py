import requests
from bs4 import BeautifulSoup
import time
import json


def fetch_images():
    streamers_dict = {}

    with open("all_streamers_names.txt", "r", encoding="UTF-8") as file:
        names = [line.strip() for line in file.readlines()]
        count = 0
        for name in names:
            time.sleep(0.35)
            url = (
                f'https://www.google.com/search?q="{name}"+twitch&tbm=isch&sclient=img'
            )
            r = requests.get(url)
            print(
                f"{count}/{len(names)} - Fetching images for streamer: {name} | status code: {r.status_code}"
            )
            count += 1
            soup = BeautifulSoup(r.text, "html.parser")

            img_tags = soup.find_all("img")

            images_list = []
            for n, img_tag in enumerate(img_tags):
                if 0 < n < 6:
                    images_list.append(img_tag["src"])

            streamers_dict[name] = [images_list]

            # write the dict into a json file
        with open("streamers.json", "w") as json_file:
            json.dump(streamers_dict, json_file)


if __name__ == "__main__":
    fetch_images()
