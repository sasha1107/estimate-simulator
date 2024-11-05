from fastapi import FastAPI
from fastapi.responses import JSONResponse
import openpyxl
import pandas as pd
import json

app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

@app.get("/api/py/helloFastApi")
def hello_fast_api():
    try:
        # 엑셀 파일 불러오기
        wb = openpyxl.load_workbook('api/data.xlsx', data_only=True)
        sheet = wb.active

        # DataFrame 생성
        df = pd.DataFrame(sheet.values)
        df.columns = df.iloc[0]  # 첫 번째 행을 컬럼명으로 설정
        df = df.iloc[1:].reset_index(drop=True)  # 첫 번째 행 제외하고 인덱스 재설정

        # 컬럼명이 제대로 설정되었는지 확인하는 코드
        expected_columns = {'category', 'name', 'unitPrice', 'quantity', '합계'}
        if not expected_columns.issubset(df.columns):
            return JSONResponse(status_code=400, content={"error": "엑셀 파일의 컬럼명이 올바르지 않습니다."})

        # 원하는 JSON 구조로 변환
        grouped_data = [
            {
                "category": category,
                "items": group[['name', 'unitPrice', 'quantity', '합계']].to_dict(orient='records')
            }
            for category, group in df.groupby('category')
        ]

        # JSON 형식으로 변환 (ensure_ascii=False와 indent=4 적용)
        json_output = json.dumps(grouped_data, ensure_ascii=False, indent=4)
        return JSONResponse(content=json.loads(json_output))  # 문자열을 JSON 형태로 변환 후 응답
    
    except Exception as e:
        # 예외가 발생한 경우 상세 오류 메시지 반환
        return JSONResponse(status_code=500, content={"error": str(e)})
