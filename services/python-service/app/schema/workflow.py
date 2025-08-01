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
    public_university: bool = Field(..., description="Trường công lập hay tư", example=True)
    major_category: str = Field(..., description="Nhóm ngành học", example="STEM")
    gpa_normalized: float = Field(..., ge=0.0, le=1.0, description="Điểm trung bình chuẩn hóa (0-1)", example=0.85)
    study_year: int = Field(..., ge=1, le=6, description="Năm học hiện tại", example=3)
    club: Optional[str] = Field(None, description="Câu lạc bộ đang tham gia", example="Câu lạc bộ IT")
    
    # Financial Info
    family_income: int = Field(..., ge=0, description="Thu nhập hộ gia đình (VND/tháng)", example=15000000)
    has_part_time_job: bool = Field(..., description="Có việc làm thêm", example=True)
    existing_debt: bool = Field(..., description="Có nợ hiện tại", example=False)
    guarantor: Optional[str] = Field(None, description="Người bảo lãnh ('Không có' nếu không có bảo lãnh)", example="Cha mẹ")
    
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

class AgentResponse(BaseModel):
    """Individual agent response model"""
    decision: Optional[str] = Field(None, description="Agent decision: approve or reject")
    reason: Optional[str] = Field(None, description="Agent reasoning")

class CriticalResponse(BaseModel):
    """Critical agent response model"""
    critical_response: Optional[str] = Field(None, description="Critical analysis text")
    recommended_decision: Optional[str] = Field(None, description="Recommended decision: approve or reject")

class FinalDecision(BaseModel):
    """Final decision from DecisionAgent"""
    decision: str = Field(..., description="Final decision: approve or reject")
    reason: str = Field(..., description="Final reasoning")

class AgentResponses(BaseModel):
    """4 main responses from the multi-agent system"""
    academic_repredict: Optional[AgentResponse] = Field(None, description="Academic agent repredict response")
    finance_repredict: Optional[AgentResponse] = Field(None, description="Finance agent repredict response")
    critical_academic: Optional[CriticalResponse] = Field(None, description="Critical response to academic")
    critical_finance: Optional[CriticalResponse] = Field(None, description="Critical response to finance")
    final_decision: FinalDecision = Field(..., description="Final decision from DecisionAgent")

class RuleBased(BaseModel):
    """Rule-based system information"""
    total_passed_count: int = Field(..., description="Number of features passed")
    special_violations_count: int = Field(..., description="Number of special feature violations")
    rule_based_decision: str = Field(..., description="Rule-based decision before agent consensus")
    rule_based_reason: str = Field(..., description="Rule-based reasoning")
    features_analysis: dict = Field(..., description="Analysis of all 7 features")

class AgentStatus(BaseModel):
    """Status of agent decisions"""
    academic_approve: bool = Field(..., description="Academic agent approved")
    finance_approve: bool = Field(..., description="Finance agent approved")
    at_least_one_agent_approve: bool = Field(..., description="At least one agent approved")
    both_conditions_met: bool = Field(..., description="Both rule-based and agent conditions met")

class FinalResult(BaseModel):
    """Final result summary"""
    decision: str = Field(..., description="Final decision: approve or reject")
    reason: str = Field(..., description="Final reasoning")
    rule_based_pass: bool = Field(..., description="Rule-based system passed")
    agent_support_available: bool = Field(..., description="Agent support available")
    hybrid_approach: str = Field(..., description="Hybrid approach used")
    error: Optional[str] = Field(None, description="Error message if any")

class LoanDecisionResponse(BaseModel):
    """Response model for loan decision with structured MAS output"""
    responses: AgentResponses = Field(..., description="4 main responses from agents")
    rule_based: RuleBased = Field(..., description="Rule-based system information")
    agent_status: AgentStatus = Field(..., description="Agent decision status")
    final_result: FinalResult = Field(..., description="Final result summary")
    request_metadata: dict = Field(..., description="Metadata about the request")
    processing_time_seconds: float = Field(..., description="Time taken to process the request")
    request_id: str = Field(..., description="Unique identifier for this request") 