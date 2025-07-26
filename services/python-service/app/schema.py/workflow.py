from pydantic import BaseModel, Field, validator
from typing import Optional

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