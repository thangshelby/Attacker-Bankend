"""
MAS Test Runner - UPDATED for 7 Features Schema
===============================================
Test runner cho Multi-Agent System với schema mới:
- Thêm 2 trường: public_university, guarantor 
- Mapping chính xác với 7 features trong decision_agent.py
- Schema validation để đảm bảo data quality
- Enhanced reporting với all fields
"""
import pandas as pd
import requests
import json
import time
import os
from datetime import datetime
import csv

class MASTestRunner:
    def __init__(self, api_base_url="http://localhost:8000/api/v1", csv_file_path="test.csv"):
        self.api_base_url = api_base_url
        self.csv_file_path = csv_file_path
        self.results = []
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "approve_count": 0,
            "reject_count": 0,
            "total_processing_time": 0,
            "start_time": None,
            "end_time": None
        }
        
    def load_csv_data(self):
        """Load and validate CSV data"""
        try:
            if not os.path.exists(self.csv_file_path):
                print(f"❌ CSV file not found: {self.csv_file_path}")
                return None
                
            df = pd.read_csv(self.csv_file_path)
            print(f"📊 Loaded {len(df)} records from {self.csv_file_path}")
            
            # Display column info
            print(f"📋 Columns: {list(df.columns)}")
            print(f"📏 Shape: {df.shape}")
            
            return df
        except Exception as e:
            print(f"❌ Error loading CSV: {str(e)}")
            return None
    
    def validate_request_schema(self, request_data):
        """Validate request data matches API schema"""
        required_fields = [
            "age_group", "age", "gender", "province_region", "university_tier", 
            "public_university", "major_category", "gpa_normalized", "study_year",
            "family_income", "has_part_time_job", "existing_debt", "guarantor",
            "loan_amount_requested", "loan_purpose"
        ]
        
        missing_fields = [field for field in required_fields if field not in request_data]
        if missing_fields:
            print(f"⚠️ Missing fields: {missing_fields}")
            return False
        
        # Validate data types and ranges
        validations = [
            (request_data["age"] >= 16 and request_data["age"] <= 30, "age must be 16-30"),
            (request_data["university_tier"] >= 1 and request_data["university_tier"] <= 5, "university_tier must be 1-5"),
            (request_data["gpa_normalized"] >= 0.0 and request_data["gpa_normalized"] <= 1.0, "gpa_normalized must be 0.0-1.0"),
            (request_data["study_year"] >= 1 and request_data["study_year"] <= 6, "study_year must be 1-6"),
            (request_data["family_income"] >= 0, "family_income must be >= 0"),
            (request_data["loan_amount_requested"] >= 1000000, "loan_amount must be >= 1M"),
            (request_data["province_region"] in ["Bắc", "Trung", "Nam"], "province_region invalid"),
            (request_data["gender"] in ["Nam", "Nữ", "Khác"], "gender invalid")
        ]
        
        for is_valid, error_msg in validations:
            if not is_valid:
                print(f"❌ Validation error: {error_msg}")
                return False
        
        return True

    def csv_row_to_request(self, row):
        """Convert CSV row to API request format"""
        try:
            # Fix province_region mapping
            raw_province = str(row.get("province_region", "Bắc"))
            province_mapping = {
                "Miền Bắc": "Bắc",
                "Miền Trung": "Trung", 
                "Miền Nam": "Nam",
                "Bắc": "Bắc",
                "Trung": "Trung",
                "Nam": "Nam"
            }
            fixed_province = province_mapping.get(raw_province, "Bắc")
            
            # Fix GPA normalization (convert thang 10 → thang 1)
            raw_gpa = float(row.get("gpa_normalized", 0.5))
            if raw_gpa > 1:  # Thang 10 (like 7.25, 6.42, 8.5)
                fixed_gpa = raw_gpa / 10.0
            else:  # Đã là thang 1 (like 0.725, 0.85)
                fixed_gpa = raw_gpa
            
            # Map CSV columns to API schema (UPDATED với 2 trường mới)
            request_data = {
                "age_group": str(row.get("age_group", "18-22")),
                "age": int(row.get("age", 20)),
                "gender": str(row.get("gender", "Nam")),
                "province_region": fixed_province,
                "university_tier": int(row.get("university_tier", 1)),
                "public_university": bool(row.get("public_university", row.get("public_uni", True))),  # NEW FIELD
                "major_category": str(row.get("major_category", "STEM")),
                "gpa_normalized": fixed_gpa,
                "study_year": int(row.get("study_year", 3)),
                "club": str(row.get("club", "")) if pd.notna(row.get("club")) else "",
                "family_income": int(row.get("family_income", 8000000)),
                "has_part_time_job": bool(row.get("has_part_time_job", False)),
                "existing_debt": bool(row.get("existing_debt", False)),
                "guarantor": str(row.get("guarantor", "Cha mẹ")) if pd.notna(row.get("guarantor")) and str(row.get("guarantor")) != "nan" else "Không có",  # NEW FIELD
                "loan_amount_requested": int(row.get("loan_amount_requested", 45000000)),
                "loan_purpose": str(row.get("loan_purpose", "Học phí"))
            }
            
            print(f"🔧 Fixed: province='{raw_province}'→'{fixed_province}', gpa={raw_gpa}→{fixed_gpa}")
            print(f"📋 New fields: public_uni={request_data['public_university']}, guarantor='{request_data['guarantor']}'")
            
            # Validate schema
            if not self.validate_request_schema(request_data):
                print(f"❌ Schema validation failed for row")
                return None
            
            return request_data
        except Exception as e:
            print(f"❌ Error converting row to request: {str(e)}")
            return None
    
    def call_mas_api(self, request_data):
        """Call the multi-agent system API"""
        try:
            url = f"{self.api_base_url}/debate-loan"
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, json=request_data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {
                    "error": f"HTTP {response.status_code}",
                    "detail": response.text
                }
        except requests.exceptions.Timeout:
            return False, {"error": "Request timeout"}
        except requests.exceptions.ConnectionError:
            return False, {"error": "Connection error - API server may be down"}
        except Exception as e:
            return False, {"error": str(e)}
    
    def run_batch_test(self, limit=None, delay_between_requests=1):
        """Run test on entire CSV dataset"""
        print(f"\n🚀 Starting MAS Batch Test - {datetime.now()}")
        print("=" * 60)
        
        # Load CSV data
        df = self.load_csv_data()
        if df is None:
            return
        
        # Limit records if specified
        if limit and limit < len(df):
            df = df.head(limit)
            print(f"📊 Limited to first {limit} records")
        
        self.stats["total_requests"] = len(df)
        self.stats["start_time"] = time.time()
        
        # Process each row
        for index, row in df.iterrows():
            print(f"\n📋 Processing record {index + 1}/{len(df)}")
            
            # Convert to API request
            request_data = self.csv_row_to_request(row)
            if request_data is None:
                self.stats["failed_requests"] += 1
                continue
            
            # Call API
            start_time = time.time()
            success, result = self.call_mas_api(request_data)
            processing_time = time.time() - start_time
            
            # Store result
            test_result = {
                "row_index": index,
                "input_data": request_data,
                "success": success,
                "result": result,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(test_result)
            
            # Update stats
            if success:
                self.stats["successful_requests"] += 1
                self.stats["total_processing_time"] += processing_time
                
                # Count decisions
                decision = result.get("decision", "").lower()
                if decision == "approve":
                    self.stats["approve_count"] += 1
                elif decision == "reject":
                    self.stats["reject_count"] += 1
                
                print(f"✅ SUCCESS: {decision} ({processing_time:.2f}s)")
            else:
                self.stats["failed_requests"] += 1
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            
            # Progress update
            if (index + 1) % 10 == 0:
                self.print_progress_stats()
            
            # Delay between requests to avoid overwhelming the server
            if delay_between_requests > 0 and index < len(df) - 1:
                time.sleep(delay_between_requests)
        
        self.stats["end_time"] = time.time()
        self.print_final_stats()
        self.save_results()
    
    def print_progress_stats(self):
        """Print current progress statistics"""
        total = self.stats["total_requests"]
        completed = self.stats["successful_requests"] + self.stats["failed_requests"]
        success_rate = (self.stats["successful_requests"] / completed * 100) if completed > 0 else 0
        
        print(f"📊 Progress: {completed}/{total} ({completed/total*100:.1f}%) | "
              f"Success: {success_rate:.1f}% | "
              f"Approve: {self.stats['approve_count']} | "
              f"Reject: {self.stats['reject_count']}")
    
    def print_final_stats(self):
        """Print final test statistics"""
        print("\n" + "=" * 60)
        print("📊 FINAL TEST STATISTICS")
        print("=" * 60)
        
        total_time = self.stats["end_time"] - self.stats["start_time"]
        avg_processing_time = (self.stats["total_processing_time"] / 
                             self.stats["successful_requests"]) if self.stats["successful_requests"] > 0 else 0
        
        print(f"📋 Total Requests: {self.stats['total_requests']}")
        print(f"✅ Successful: {self.stats['successful_requests']}")
        print(f"❌ Failed: {self.stats['failed_requests']}")
        print(f"📈 Success Rate: {self.stats['successful_requests']/self.stats['total_requests']*100:.2f}%")
        print(f"")
        print(f"⚖️ DECISIONS:")
        print(f"   ✅ Approve: {self.stats['approve_count']}")
        print(f"   ❌ Reject: {self.stats['reject_count']}")
        if self.stats['successful_requests'] > 0:
            approve_rate = self.stats['approve_count'] / self.stats['successful_requests'] * 100
            print(f"   📊 Approval Rate: {approve_rate:.2f}%")
        print(f"")
        print(f"⏱️ TIMING:")
        print(f"   Total Test Time: {total_time:.2f}s")
        print(f"   Total Processing Time: {self.stats['total_processing_time']:.2f}s")
        print(f"   Average Per Request: {avg_processing_time:.2f}s")
        print(f"   Requests Per Minute: {self.stats['successful_requests']/(total_time/60):.1f}")
    
    def save_results(self):
        """Save detailed results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = f"mas_test_results_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "stats": self.stats,
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        
        # Save summary CSV
        summary_file = f"mas_test_summary_{timestamp}.csv"
        summary_data = []
        for result in self.results:
            if result["success"]:
                r = result["result"]
                summary_data.append({
                    "row_index": result["row_index"],
                    "decision": r.get("decision", ""),
                    "reason": r.get("reason", ""),
                    "processing_time": result["processing_time"],
                    "gpa": result["input_data"]["gpa_normalized"],
                    "income": result["input_data"]["family_income"],
                    "loan_amount": result["input_data"]["loan_amount_requested"],
                    "existing_debt": result["input_data"]["existing_debt"],
                    "university_tier": result["input_data"]["university_tier"],
                    "public_university": result["input_data"]["public_university"],  # NEW FIELD
                    "guarantor": result["input_data"]["guarantor"],  # NEW FIELD
                    "major_category": result["input_data"]["major_category"],
                    "has_part_time_job": result["input_data"]["has_part_time_job"]
                })
        
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_csv(summary_file, index=False)
        
        print(f"\n💾 Results saved:")
        print(f"   📄 Detailed: {results_file}")
        print(f"   📊 Summary: {summary_file}")
    
    def test_api_connection(self):
        """Test if API is accessible"""
        try:
            url = f"{self.api_base_url}/health"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ API connection successful: {url}")
                print(f"📡 API Response: {response.json()}")
                return True
            else:
                print(f"❌ API connection failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API connection error: {str(e)}")
            print(f"💡 Make sure the FastAPI server is running on {self.api_base_url}")
            return False

def main():
    """Main test execution"""
    print("🧪 Multi-Agent System (MAS) Batch Tester")
    print("=" * 50)
    
    # Initialize tester
    tester = MASTestRunner(
        api_base_url="http://localhost:8000/api/v1",
        csv_file_path="test.csv"
    )
    
    # Test API connection first
    if not tester.test_api_connection():
        print("\n🚨 Cannot proceed without API connection!")
        print("💡 Run: python main_fastapi.py")
        return
    
    # Run the batch test
    print(f"\n🤖 Starting batch test...")
    
    # You can customize these parameters:
    # - limit: Number of records to process (None = all)
    # - delay_between_requests: Seconds to wait between API calls
    tester.run_batch_test(
        limit=None,  # Process all records, or set to e.g., 50 for testing
        delay_between_requests=0.5  # Small delay to avoid overwhelming the API
    )

if __name__ == "__main__":
    main()
