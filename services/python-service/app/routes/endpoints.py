from fastapi import Request, HTTPException
from app.core.a2a_workflow import debate_to_decide_workflow
import pickle
import os
from fastapi import APIRouter
import json 
from pydantic import BaseModel, Field, validator
from typing import Optional
import time
import uuid

router = APIRouter()

class LoanApplicationRequest(BaseModel):
    """
    Updated model based on dataset schema (excluding student_id, national_id, province)
    """
    # Demographics
    age_group: str = Field(..., description="Nhóm tuổi", example="18-22")
    age: int = Field(..., ge=16, le=30, description="Tuổi sinh viên", example=20)
    gender: str = Field(..., description="Giới tính", example="Nam")
    province_region: str = Field(..., description="Miền (Bắc/Trung/Nam)", example="Bắc")
    
    # Academic Info
    university_tier: int = Field(..., ge=1, le=5, description="Xếp hạng đại học (1-5)", example=1)
    major_category: str = Field(..., description="Nhóm ngành học", example="STEM")
    gpa_normalized: float = Field(..., ge=0.0, le=1.0, description="Điểm trung bình chuẩn hóa (0-1)", example=0.85)
    study_year: int = Field(..., ge=1, le=6, description="Năm học hiện tại", example=3)
    club: Optional[str] = Field(None, description="Câu lạc bộ đang tham gia", example="Câu lạc bộ IT")
    
    # Financial Info
    family_income: int = Field(..., ge=0, description="Thu nhập hộ gia đình (VND/tháng)", example=15000000)
    has_part_time_job: bool = Field(..., description="Có việc làm thêm", example=True)
    existing_debt: bool = Field(..., description="Có nợ hiện tại", example=False)
    
    # Loan Request
    loan_amount_requested: int = Field(..., ge=1000000, le=500000000, description="Số tiền đề nghị vay (VND)", example=50000000)
    loan_purpose: str = Field(..., description="Mục đích vay", example="Học phí")
    
    @validator('gender')
    def validate_gender(cls, v):
        valid_genders = ['Nam', 'Nữ', 'Khác']
        if v not in valid_genders:
            raise ValueError(f'Gender must be one of: {valid_genders}')
        return v
    
    @validator('province_region')
    def validate_province_region(cls, v):
        valid_regions = ['Bắc', 'Trung', 'Nam']
        if v not in valid_regions:
            raise ValueError(f'Province region must be one of: {valid_regions}')
        return v

class LoanDecisionResponse(BaseModel):
    """Response model for loan decision"""
    decision: str = Field(..., description="Decision result: approve or reject")
    reason: str = Field(..., description="Detailed reasoning for the decision")
    request_metadata: dict = Field(..., description="Metadata about the request")
    logs: list = Field(..., description="Detailed conversation logs from agent workflow")
    processing_time_seconds: float = Field(..., description="Time taken to process the request")
    request_id: str = Field(..., description="Unique identifier for this request")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the loan decision service
    """
    return {
        "status": "healthy",
        "service": "loan-decision-a2a",
        "version": "1.0.0",
        "timestamp": time.time(),
        "endpoints": [
            "/api/v1/debate-loan",
            "/api/v1/health",
            "/api/v1/example-request"
        ]
    }


@router.post("/debate-loan", response_model=LoanDecisionResponse)
async def debate_loan(request: LoanApplicationRequest):
    """
    Nhận dữ liệu hồ sơ theo schema mới, chạy workflow tranh luận agent và trả về kết quả cùng log các vòng tranh luận.
    
    This endpoint evaluates loan applications using a multi-agent debate system:
    1. Academic Agent: Evaluates academic potential and achievements
    2. Finance Agent: Analyzes financial risk and repayment capability  
    3. Critical Agent: Provides critical analysis and feedback
    4. Decision Agent: Makes final decision based on all inputs
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Tạo profile text từ dữ liệu đầu vào mới
        profile = (
            f"Hồ sơ sinh viên vay vốn (ID: {request_id}):\n"
            f"- Thông tin cá nhân: {request.age} tuổi, {request.gender}, nhóm tuổi {request.age_group}, khu vực {request.province_region}\n"
            f"- Thông tin học tập: Đại học tier {request.university_tier}, ngành {request.major_category}, "
            f"năm {request.study_year}, GPA chuẩn hóa: {request.gpa_normalized:.2f}/1.0\n"
            f"- Hoạt động ngoại khóa: {request.club if request.club else 'Không tham gia CLB nào'}\n"
            f"- Tài chính gia đình: Thu nhập {request.family_income:,} VND/tháng\n"
            f"- Tình hình cá nhân: {'Có việc làm thêm' if request.has_part_time_job else 'Không có việc làm thêm'}, "
            f"{'Đang có nợ' if request.existing_debt else 'Không có nợ'}\n"
            f"- Yêu cầu vay: {request.loan_amount_requested:,} VND cho mục đích '{request.loan_purpose}'"
        )
        
        print(f"\n🚀 Processing loan application {request_id}")
        print(f"📋 Profile: {profile}")
        
        # Chạy workflow debate
        result = debate_to_decide_workflow(profile, return_log=True)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Add request metadata to result
        result["request_metadata"] = {
            "request_id": request_id,
            "loan_amount": request.loan_amount_requested,
            "loan_purpose": request.loan_purpose,
            "gpa_normalized": request.gpa_normalized,
            "university_tier": request.university_tier,
            "family_income": request.family_income,
            "has_existing_debt": request.existing_debt,
            "age": request.age,
            "gender": request.gender,
            "major_category": request.major_category,
            "processing_time_seconds": round(processing_time, 2),
            "timestamp": time.time()
        }
        
        result["processing_time_seconds"] = round(processing_time, 2)
        result["request_id"] = request_id
        
        print(f"✅ Decision: {result.get('decision', 'unknown')} (took {processing_time:.2f}s)")
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Workflow execution failed: {str(e)}"
        
        print(f"❌ Error processing {request_id}: {error_msg}")
        
        # Return structured error response
        raise HTTPException(
            status_code=500,
            detail={
                "error": "workflow_execution_failed",
                "message": error_msg,
                "request_id": request_id,
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": time.time()
            }
        )


