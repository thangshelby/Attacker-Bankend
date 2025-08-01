from fastapi import Request, HTTPException
from app.core.a2a_workflow import debate_to_decide_workflow
from app.schema.workflow import LoanApplicationRequest, LoanDecisionResponse
import pickle
import os
from fastapi import APIRouter
import json 
import time
import uuid

router = APIRouter()

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
            "/api/v1/health"
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
            f"- Thông tin học tập: Đại học tier {request.university_tier}, "
            f"{'trường công lập' if request.public_university else 'trường tư thục'}, ngành {request.major_category}, "
            f"năm {request.study_year}, GPA chuẩn hóa: {request.gpa_normalized:.2f}/1.0\n"
            f"- Hoạt động ngoại khóa: {request.club if request.club else 'Không tham gia CLB nào'}\n"
            f"- Tài chính gia đình: Thu nhập {request.family_income:,} VND/tháng\n"
            f"- Tình hình cá nhân: {'Có việc làm thêm' if request.has_part_time_job else 'Không có việc làm thêm'}, "
            f"{'Đang có nợ' if request.existing_debt else 'Không có nợ'}\n"
            f"- Bảo lãnh: {request.guarantor if request.guarantor else 'Không có'}\n"
            f"- Yêu cầu vay: {request.loan_amount_requested:,} VND cho mục đích '{request.loan_purpose}'"
        )
        
        print(f"\n🚀 Processing loan application {request_id}")
        print(f"📋 Profile: {profile}")
        
        # Chạy workflow debate
        result = debate_to_decide_workflow(profile, return_log=True)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Add request metadata to structured result
        result["request_metadata"] = {
            "request_id": request_id,
            "loan_amount": request.loan_amount_requested,
            "loan_purpose": request.loan_purpose,
            "gpa_normalized": request.gpa_normalized,
            "university_tier": request.university_tier,
            "public_university": request.public_university,
            "guarantor": request.guarantor,
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
        
        # Extract final decision for logging (compatible with new structure)
        final_decision = result.get("final_result", {}).get("decision", 
                                   result.get("responses", {}).get("final_decision", {}).get("decision", "unknown"))
        print(f"✅ Decision: {final_decision} (took {processing_time:.2f}s)")
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Workflow execution failed: {str(e)}"
        
        print(f"❌ Error processing {request_id}: {error_msg}")
        
        # Return structured error response (compatible with new schema)
        raise HTTPException(
            status_code=500,
            detail={
                "responses": {
                    "academic_repredict": None,
                    "finance_repredict": None,
                    "critical_academic": None,
                    "critical_finance": None,
                    "final_decision": {
                        "decision": "reject",
                        "reason": error_msg
                    }
                },
                "rule_based": {},
                "agent_status": {},
                "final_result": {
                    "decision": "reject",
                    "reason": error_msg,
                    "error": "workflow_execution_failed"
                },
                "request_metadata": {
                    "request_id": request_id,
                    "processing_time_seconds": round(processing_time, 2),
                    "timestamp": time.time()
                },
                "processing_time_seconds": round(processing_time, 2),
                "request_id": request_id
            }
        )


