import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Steam 크롤러 함수 가져오기
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

# 구글 시트 인증 및 설정
def connect_to_google_sheet(sheet_id):
    print("Connecting to Google Sheet...")  # 진행 상태 출력
    # credentials.json 파일 경로
    credentials_path = "C:/Users/ellen/Downloads/credentials.json"
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1  # 파일 이름 대신 ID로 접근
    print("Connected to Google Sheet successfully.")  # 연결 완료 메시지 출력
    return sheet

# 구글 시트 업데이트
def update_google_sheet(sheet, data):
    print("Google Sheet를 업데이트하는 중...")  # 진행 상태 출력
    updates = []
    for idx, item in enumerate(data, start=2):  # 시작 행 번호 설정
        print(f"아이템: {item['name']}에 대한 {idx}번째 행 업데이트 중...")  # 각 항목 업데이트 상태 출력
        # 아이템 이름, 가격, 수량 업데이트
        updates.append({'range': f"A{idx}", 'values': [[item['name']]]})
        updates.append({'range': f"B{idx}", 'values': [[item['price']]]})
        updates.append({'range': f"C{idx}", 'values': [[item['quantity']]]})
        # 수식을 R1C1 형식으로 입력하여 수식이 제대로 계산되도록 수정
        updates.append({'range': f"D{idx}", 'values': [[f"=B{idx}*C{idx}"]]})  # 수식 업데이트
    sheet.batch_update(updates)  # batch_update를 사용하여 한 번에 여러 셀을 업데이트
    print("Google Sheet 업데이트 완료.")  # 완료 메시지 출력

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

    print("Google Sheet updated successfully!") # 모든 작업 완료 메시지
    
    input("\nPress Enter to exit...")
