from typing import List, Optional
import requests
from bs4 import BeautifulSoup


class Level:
    def __init__(self, letters: List[str]):
        self.letters = letters
        self.words = []
        self.unscramble_url = "https://www.allscrabblewords.com/unscramble/"
        self._unscramble()

    def _unscramble(self):
        url = self.unscramble_url + "".join(self.letters)
        html = requests.get(url).text
        # with open("allscrabblewords.html", "w") as file:
        #     file.write(html)

        soup = BeautifulSoup(html, 'html.parser')
        unscrambled_panels = soup.find_all("div", class_="panel-body unscrambled")
        # with open("unscrambled panels.html", "wb") as file:
        #     for panel in unscrambled_panels:
        #         file.write(panel.encode())
        #         file.write(b"\n")
        for panel in unscrambled_panels:
            for word in panel.findAll("a"):
                text = word.text
                if len(text) < 3 or len(text) > len(self.letters):
                    break
                self.words.append(text.upper())
        # print(self.words)

    def get_word(self) -> Optional[str]:
        try:
            return self.words.pop(0)
        except IndexError:
            return None
