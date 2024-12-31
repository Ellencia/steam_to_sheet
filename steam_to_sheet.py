import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

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
            print(f"Price for {market_hash_name}: {price}")
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
    credentials_path = "C:/Users/ellen/Downloads/credentials.json"
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1  # 파일 이름 대신 ID로 접근
    print("Connected to Google Sheet successfully.")
    return sheet

def update_google_sheet(sheet, data):
    print("Updating Google Sheet...")
    updates = []
    for idx, item in enumerate(data, start=2):  # 시작 행 조정
        print(f"Updating row {idx} for item: {item['name']}...")
        updates.append({'range': f"A{idx}", 'values': [[item['name']]]})
        updates.append({'range': f"B{idx}", 'values': [[item['price']]]})
        updates.append({'range': f"C{idx}", 'values': [[item['quantity']]]})

    sheet.batch_update(updates)
    print("Google Sheet updated successfully.")

def update_formulas(sheet, data):
    print("Updating formulas...")
    for idx in range(2, len(data) + 2):  # 시작 행 조정
        formula = f"=B{idx}*C{idx}"
        print(f"Updating formula in D{idx}: {formula}")
        sheet.update_cell(idx, 4, formula)  # D열에 수식 개별적으로 업데이트
    print("Formulas updated successfully.")

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

    # 아이템 수량 가져오기
    for target_item_name in target_item_names:  # 각 아이템에 대해 처리
        quantity = get_item_quantity(steam_id, app_id, context_id, target_item_name)
        print(f"Found {target_item_name} with quantity: {quantity}")
    
    # 반복문을 통해 각 아이템을 처리
    data = []
    for item_name in target_item_names:
        # 각 아이템의 가격을 가져오기
        price = get_steam_item_price(app_id, item_name)
        if price:
            # 가격을 구글 시트에 업데이트할 데이터에 추가
            data.append({"name": item_name, "price": price, "quantity": quantity}) 

    print(data) # 디버그
    
    # Google Sheet 업데이트
    sheet_id = "1Jyb1W-sO5jiE-ESE3WLsb5rRfUTkXhwSDBHDzRSQJCE"  # Google Sheet ID
    sheet = connect_to_google_sheet(sheet_id)


    # 구글 시트에 아이템 정보 업데이트
    update_google_sheet(sheet, data)

    # 수식 업데이트
    update_formulas(sheet, data)

    print("Google Sheet updated successfully!")
    
    input("\nPress Enter to exit...")
