from fastapi import Request
from app.core.a2a_workflow import debate_to_decide_workflow
import pickle
import os
from fastapi import APIRouter
import json 
from pydantic import BaseModel
router = APIRouter()
class LoanApplicationRequest(BaseModel):
    name: str
    gpa: float
    achievement: str
    family_income: int
    debt: bool
    extra: str = ""

@router.post("/debate-loan")
async def debate_loan(request: LoanApplicationRequest):
    """
    Nhận dữ liệu hồ sơ, chạy workflow tranh luận agent và trả về kết quả cùng log các vòng tranh luận.
    """
    # Tạo profile text từ dữ liệu đầu vào
    profile = (
        f"Khách hàng: {request.name}, GPA: {request.gpa}, Thành tích: {request.achievement}, "
        f"Thu nhập gia đình: {request.family_income} triệu/tháng, Nợ xấu: {'Có' if request.debt else 'Không'}, "
        f"Thông tin thêm: {request.extra}"
    )
    # Chạy workflow debate
    result = debate_to_decide_workflow(profile, return_log=True)
    return result


