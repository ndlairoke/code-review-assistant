from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from main import form_report  # Импортируем вашу функцию
import os
from dotenv import load_dotenv
from fastapi.responses import FileResponse

# Инициализация приложения
app = FastAPI()

# Загрузка переменных окружения
load_dotenv()

# Модель запроса
class ReportRequest(BaseModel):
    github_url: str
    email: str
    start_date: datetime
    end_date: datetime
    access_token: Optional[str] = None

@app.post("/generate-report")
async def generate_report(
    request: ReportRequest,
    authorization: Optional[str] = Header(None)
):
    # Получаем токен из: тела запроса, заголовка или переменных окружения
    access_token = (
        request.access_token or
        (authorization.split(" ")[1] if authorization and authorization.startswith("Bearer ") else None) or
        os.getenv("GITHUB_TOKEN")
    )
    
    try:
        report_path = form_report(
            github_url=request.github_url,
            email=request.email,
            start_date=request.start_date,
            end_date=request.end_date,
            access_token=access_token
        )
        return FileResponse(
            report_path,
            filename=os.path.basename(report_path),  # Имя файла для клиента
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Для запуска через python api.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)