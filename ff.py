#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 Chrome/120 Safari/537.36",
}

SEAT_ID_PATTERN = re.compile(r"^seat-\d+$")

# Hardcoded clubs and seat page URLs (replace with correct blocks_id / references)
clubs = [
    ("Telford Tigers (Block 5)", "https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=977&stage=2&Reference=tigers-7PR75"),
    ("Bristol Pitbulls (Block 6)", "https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=978&stage=2&Reference=pitbulls-V285C"),
    ("Sheffield Steeldogs (Block 13)", "https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=984&stage=2&Reference=steeldogs-9WQ39"),
    ("Hull Seahawks (Block 4)","https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=976&stage=2&Reference=seahawks-H1524"),
    ("Bees (Block 10)","https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=982&stage=2&Reference=bees-91MT1"),    
    ("Swindon Wildcats (Block 11)","https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=999&stage=2&Reference=wildcats-73V4F"),
    ("Swindon Wildcats (Block 12)","https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=983&stage=2&Reference=wildcats-73V4F"),
    ("Basingstoke Bison (Block 15)","https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=986&stage=2&Reference=bison-9NN48"),
    ("Peterborough Phantoms (Block 9)","https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=981&stage=2&Reference=phantoms-76EC2"),
    ("Solway Sharks (Block 1)","https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=973&stage=2&Reference=sharks-65A4G"),
    ("Leeds Knights (Block 7)","https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=979&stage=2&Reference=knights-9V7Y8"),
    ("Leeds Knights (Block 8)","https://iceaccount.co.uk/nihl-play-off-weekend/event-tickets/?event_id=8367&blocks_id=980&stage=2&Reference=knights-9V7Y8"),
 
]

def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def extract_row(el):
    for key in ["data-row", "data-rowname", "data-row-id"]:
        if el.has_attr(key):
            return str(el[key])
    for c in el.get("class", []):
        if c.startswith("row-"):
            return c.split("-", 1)[1]
    return "UNKNOWN"


def extract_seat_number(el):
    for key in ["data-seat", "data-seatnumber", "data-seat-id"]:
        if el.has_attr(key):
            try:
                return int(el[key])
            except:
                pass
    m = re.search(r"\d+", el.text)
    if m:
        return int(m.group())
    return None


def largest_contiguous_block(row_map):
    largest = 0
    for seats in row_map.values():
        seq = sorted(seats)
        current = 1
        best = 1
        for i in range(1, len(seq)):
            if seq[i] == seq[i - 1] + 1:
                current += 1
                best = max(best, current)
            else:
                current = 1
        largest = max(largest, best)
    return largest


def analyse_seats_html(html):
    soup = BeautifulSoup(html, "html.parser")
    sold = 0
    available = 0
    row_map = defaultdict(list)

    for el in soup.find_all(id=SEAT_ID_PATTERN):
        classes = el.get("class", [])
        if "sold" in classes:
            sold += 1
        elif "available" in classes:
            available += 1
            row = extract_row(el)
            seat_num = extract_seat_number(el)
            if seat_num is not None:
                row_map[row].append(seat_num)

    total = sold + available
    pct_sold = (sold / total * 100) if total else 0
    largest_block = largest_contiguous_block(row_map)

    return total, sold, available, pct_sold, largest_block


def main():
    print("Fetching seat data for all clubs...\n")

    for club_name, seat_url in clubs:
        try:
            seat_html = fetch_html(seat_url)
            total, sold, available, pct_sold, largest_block = analyse_seats_html(seat_html)
        except Exception as e:
            print(f"\n{club_name} - ERROR fetching seats: {e}")
            continue

        print(f"\n{club_name}")
        print("-" * len(club_name))
        print(f"Total Seats: {total}")
        print(f"Sold Seats: {sold}")
        print(f"Available Seats: {available}")
        print(f"% Sold: {pct_sold:.2f}%")
        print(f"Largest Contiguous Block: {largest_block}")


if __name__ == "__main__":
    main()

