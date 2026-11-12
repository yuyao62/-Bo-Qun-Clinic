"""Read the same anonymous public endpoint used by the supplied clinic page."""
import argparse
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

SOURCE = 'https://wroom.vision.com.tw/MainPage/ClinicInfo.aspx?CliID=QCpjCdqyOd8V%2buKpwwfjbg=='
ENDPOINT = 'https://wroom.vision.com.tw/WServ/VWWL_Clinics.svc/GetWaitInfo'
TAIPEI = timezone(timedelta(hours=8))
# Anonymous routing fields from this clinic's supplied public page.
PUBLIC_PORTAL_ID = 'JjYAqpRdgjE='
PUBLIC_CLINIC_CODE = '88173'


class ClinicPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.vcode = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table' and attrs.get('id', '').endswith('visWInfos_gvwCRoom'):
            self.vcode = attrs.get('vcode')


def request(url, data=None):
    req = urllib.request.Request(url, data=data, headers={
        'User-Agent': 'Mozilla/5.0 (ClinicQueuePublicDisplay)',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': SOURCE,
    })
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read(1_000_001).decode('utf-8-sig')


def number(value):
    value = str(value).strip()
    return int(value) if re.fullmatch(r'\d{1,6}', value) else None


def parse_rooms(payload):
    if payload.get('Code') != '0000' or not isinstance(payload.get('Infos'), list):
        raise ValueError('Unexpected public queue response')
    rooms = []
    for info in payload['Infos']:
        if not isinstance(info, dict) or not all(k in info for k in ('RName', 'RTime', 'WRecs')):
            raise ValueError('Queue fields changed')
        # The original page clears every numeric cell for the XXXX sentinel.
        unavailable = str(info['RTime']).strip() == 'XXXX'
        stamp = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(info.get('MTime', '')))
        updated = datetime.strptime(stamp.group(), '%Y-%m-%d %H:%M:%S').replace(tzinfo=TAIPEI).isoformat() if stamp else None
        rooms.append({
            'room': str(info['RName'])[:100],
            'doctor': '' if unavailable else str(info.get('WDoct', ''))[:100],
            'period': '' if unavailable else str(info.get('WSect', ''))[:100],
            'current_number': None if unavailable else number(info['RTime']),
            'waiting_count': None if unavailable else number(info['WRecs']),
            'source_updated_at': updated,
            'status': 'unavailable' if unavailable else 'available',
        })
    return rooms


def fetch():
    # Read the same public JSON as the page, avoiding its unrelated slow HTML assets.
    # PortalID and Vcode identify the clinic, and are not authentication credentials.
    body = json.dumps({'PortalID': PUBLIC_PORTAL_ID, 'Vcode': PUBLIC_CLINIC_CODE, 'ReqFmt': 'LIST'}).encode()
    rooms = parse_rooms(json.loads(request(ENDPOINT, body)))
    return {'clinic': '博群診所', 'source_url': SOURCE, 'fetched_at': datetime.now(TAIPEI).isoformat(), 'fetch_ok': True, 'scheduled': os.environ.get('GITHUB_ACTIONS') == 'true', 'rooms': rooms}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='dist/queue.json')
    args = parser.parse_args()
    try:
        result = fetch()
        print('Public queue fetched successfully')
    except Exception as exc:
        # Publish a clear unavailable state instead of old numbers or invented zeroes.
        print('Queue unavailable:', type(exc).__name__, str(exc))
        result = {'clinic': '博群診所', 'source_url': SOURCE, 'fetched_at': datetime.now(TAIPEI).isoformat(), 'fetch_ok': False, 'rooms': []}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not result['fetch_ok']:
        sys.exit(1)


if __name__ == '__main__':
    main()
