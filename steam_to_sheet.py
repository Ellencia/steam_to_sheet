import gspread
import requests
import time
import sys
import io
import threading
from oauth2client.service_account import ServiceAccountCredentials
from tabulate import tabulate
from pathlib import Path
from datetime import datetime # Import datetime for timestamps

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def loading_dots(text, stop_event):
    print(text, end="")
    while not stop_event.is_set():  # stop_event가 set되기 전까지 계속 점 출력
        time.sleep(1)  # 1초마다 점을 추가
        print(".", end="", flush=True)
   
def get_steam_item_price(appid, market_hash_name):
    base_url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        "appid": appid,
        "currency": 1,  # USD
        "market_hash_name": market_hash_name
    }
    
    try:
        # 가격 정보 가져오기
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # 요청이 성공적인지 확인
        
        data = response.json()  # JSON 형식으로 응답 데이터 받기
        
        # 가격 정보가 있으면 반환
        if "lowest_price" in data:
            price = data["lowest_price"]
            # '$' 기호 제거하고 숫자 값만 반환
            return float(price.replace('$', '').replace(',', ''))
        else:
            print(f"No price data available for {market_hash_name}")
            return None
    except Exception as e:
        print(f"Error fetching price for {market_hash_name}: {e}")
        return None
        
def get_item_quantity(steam_id, app_id, context_id, target_item_name):
    url = f"https://steamcommunity.com/inventory/{steam_id}/{app_id}/{context_id}/"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        item_counts = {}
        
        # assets에서 각 아이템의 수량 계산
        for asset in data["assets"]:
            item_id = asset["classid"]
            amount = int(asset["amount"]) if isinstance(asset["amount"], str) else asset["amount"]
            
            if item_id not in item_counts:
                item_counts[item_id] = 0
            item_counts[item_id] += amount
        
        # descriptions에서 아이템을 찾아 수량 반환
        for item in data["descriptions"]:
            if item["market_hash_name"] == target_item_name:
                item_id = item["classid"]
                quantity = item_counts.get(item_id, 0)  # 해당 아이템의 수량
                return quantity
    else:
        print(f"Failed to fetch inventory: {response.status_code}")
        return 0

def connect_to_google_sheet(sheet_id):
    print("Connecting to Google Sheet...")
    
    # 현재 스크립트의 디렉토리 기준으로 credentials.json 경로 설정
    BASE_DIR = Path(__file__).resolve().parent
    credentials_path = BASE_DIR / "credentials.json"
    
    scope = [
        "https://spreadsheets.google.com/feeds", 
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file", 
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1  # 파일 이름 대신 ID로 접근
    print("Connected to Google Sheet successfully.")
    return sheet

# Function to get exchange rate
def get_exchange_rate():
    # Replace YOUR_EXCHANGERATE_API_KEY with your actual API key
    api_key = "eecf69a8652bc196cc7b53cf" 
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["result"] == "success" and "conversion_rates" in data:
            return data["conversion_rates"]["KRW"]
        else:
            print(f"Error fetching exchange rate: {data.get('error-type', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

# Modified function to append data
def append_data_to_sheet(sheet, data):
    print("Appending data to Google Sheet...")
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get exchange rate
    exchange_rate = get_exchange_rate()
    if exchange_rate is None:
        print("Could not fetch exchange rate. KRW values will be 0.")
        exchange_rate = 0 # Default to 0 if exchange rate cannot be fetched
    
    rows_to_append = []
    total_profit_for_run_usd = 0 # Total profit in USD for this run
    total_profit_for_run_krw = 0 # Total profit in KRW for this run
    
    for item in data:
        calculated_value_usd = item['price'] * item['quantity']
        calculated_value_krw = calculated_value_usd * exchange_rate
        
        rows_to_append.append([
            timestamp, # Add timestamp to each row
            item['name'], 
            item['price'], 
            item['quantity'], 
            calculated_value_usd,
            exchange_rate, # Add exchange rate
            calculated_value_krw # Add KRW value
        ])
        total_profit_for_run_usd += calculated_value_usd
        total_profit_for_run_krw += calculated_value_krw
        
    # Append all item data rows
    if rows_to_append:
        sheet.append_rows(rows_to_append)
        print(f"Appended {len(rows_to_append)} item rows.")
    
    # Append a summary row for total profit of this run
    # Note: Adjust column indices if you change the sheet structure
    sheet.append_row(['Total Profit for this run (USD)', '', '', '', total_profit_for_run_usd, '', ''])
    sheet.append_row(['Total Profit for this run (KRW)', '', '', '', '', '', total_profit_for_run_krw])
    print(f"Appended total profit for this run: USD {total_profit_for_run_usd}, KRW {total_profit_for_run_krw}")
    
    print("Google Sheet updated successfully with appended data.")
        
if __name__ == "__main__":
    steam_id = "76561198030635599"  # 자신의 Steam ID
    app_id = "570"  # Dota 2의 App ID
    context_id = "2"  # Dota 2 보관함의 Context ID
    target_item_names = [
        "Trust of the Benefactor 2020",
        "Immortal Treasure I 2020",
        "Immortal Treasure II 2020",
        "Immortal Treasure III 2020"
    ]
    
    stop_event = threading.Event() # 종료 이벤트 정의
    
    loading_thread = threading.Thread(target=loading_dots, args=("Fetching prices", stop_event))
    loading_thread.daemon = True # 메인 프로그램 종료 시 스레드 종료
    loading_thread.start()

    # 일치하는 아이템의 정보를 딕셔너리 형태로 저장하기
    data = []
    for item_name in target_item_names:
        quantity = get_item_quantity(steam_id, app_id, context_id, item_name)
        price = get_steam_item_price(app_id, item_name)
        if price is not None:
            data.append({"name": item_name, "price": price, "quantity": quantity}) 
    
    stop_event.set() # 종료 이벤트
    time.sleep(1)
    print() # 줄바꿈
    print(tabulate(data, headers="keys", tablefmt="fancy_grid"))
    
    # Google Sheet 업데이트
    sheet_id = "1Jyb1W-sO5jiE-ESE3WLsb5rRfUTkXhwSDBHDzRSQJCE"  # Google Sheet ID
    sheet = connect_to_google_sheet(sheet_id)

    # 구글 시트에 아이템 정보 업데이트 (덮어쓰기 대신 추가)
    append_data_to_sheet(sheet, data)

    print("Google Sheet update process completed!")
