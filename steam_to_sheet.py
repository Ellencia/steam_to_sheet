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
        print(f"Fetching price for {market_hash_name}...")  # 진행 상태 출력
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"Price for {market_hash_name}: {data['lowest_price']}")  # 가격 출력
        return float(data['lowest_price'].replace('$', '').replace(',', ''))
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def connect_to_google_sheet(sheet_id):
    print("Connecting to Google Sheet...")  # 진행 상태 출력
    credentials_path = "C:/Users/ellen/Downloads/credentials.json"
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1  # 파일 이름 대신 ID로 접근
    print("Connected to Google Sheet successfully.")  # 연결 완료 메시지 출력
    return sheet

def update_google_sheet(sheet, data):
    print("Updating Google Sheet...")  # 진행 상태 출력
    updates = []
    for idx, item in enumerate(data, start=2):  # 시작 행 조정
        print(f"Updating row {idx} for item: {item['name']}...")  # 각 항목 업데이트 상태 출력
        updates.append({'range': f"A{idx}", 'values': [[item['name']]]})
        updates.append({'range': f"B{idx}", 'values': [[item['price']]]})
        updates.append({'range': f"C{idx}", 'values': [[item['quantity']]]})
        # 수식이 포함된 셀 업데이트 (이 부분이 핵심)

    sheet.batch_update(updates)  # batch_update를 사용하여 여러 셀을 한 번에 업데이트
    print("Google Sheet updated successfully.")  # 완료 메시지 출력

    print("Formula values updated.")  # 값 업데이트 완료 메시지
    
    # 구글 시트 수식 업데이트 (독립 처리)
def update_formulas(sheet, data):
    print("Updating formulas...")  # 상태 출력
    for idx in range(2, len(data) + 2):  # 시작 행 조정
        formula = f"=B{idx}*C{idx}"  # 수식 생성
        print(f"Updating formula in D{idx}: {formula}")  # 디버깅
        sheet.update(range_name=f"D{idx}", values=[[formula]])  # 수식만 독립적으로 업데이트
    print("Formulas updated successfully.")  # 수식 업데이트 완료 메시지

# 실행 코드
if __name__ == "__main__":
    sheet_id = "1Jyb1W-sO5jiE-ESE3WLsb5rRfUTkXhwSDBHDzRSQJCE"  # Google Sheet ID
    sheet = connect_to_google_sheet(sheet_id)
    
    items = [
        {"name": "Trust of the Benefactor 2020", "quantity": 2},
        {"name": "Immortal Treasure I 2020", "quantity": 5},
        {"name": "Immortal Treasure II 2020", "quantity": 5},
        {"name": "Immortal Treasure III 2020", "quantity": 5}
    ]

    # 가격 크롤링 및 데이터 구성
    print("Fetching item prices...")  # 가격 크롤링 시작
    data = []
    for item in items:
        price = get_steam_item_price(appid=570, market_hash_name=item['name'])
        if price:
            data.append({"name": item['name'], "price": price, "quantity": item['quantity']})
    print("Item prices fetched.")  # 가격 크롤링 완료
    
    # 구글 시트 업데이트
    update_google_sheet(sheet, data)
    # 수식 독립 업데이트
    update_formulas(sheet, data)
    
    print("Google Sheet updated successfully!")  # 모든 작업 완료 메시지
    
    input("\nPress Enter to exit...")
