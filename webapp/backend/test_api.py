"""
Backend API Tests - Unit & Integration

Tests all API endpoints:
- Unit tests (individual endpoints)
- Integration tests (full workflow)
- Error handling
- Edge cases

Run: pytest test_api.py -v
"""

import sys
from pathlib import Path
import tempfile
import os

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from main import app

# Test client
client = TestClient(app)


# ============================================================================
# UNIT TESTS - Individual Endpoints
# ============================================================================

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_root_endpoint(self):
        """Test GET / returns health status"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["service"] == "Nesting SAAS API"
        assert data["version"] == "1.0.0"


class TestUploadEndpoint:
    """Test file upload endpoint"""
    
    def test_upload_valid_dxf(self):
        """Test uploading a valid DXF file"""
        # Use actual test file
        test_file = Path(__file__).parent.parent.parent / "Test files" / "01_simple" / "rectangles.dxf"
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("rectangles.dxf", f, "application/dxf")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "job_id" in data
        assert data["filename"] == "rectangles.dxf"
        assert data["num_parts"] > 0
        assert data["total_area"] > 0
        assert data["message"] == "File uploaded successfully"
    
    def test_upload_non_dxf_file(self):
        """Test uploading non-DXF file should fail"""
        # Create a dummy text file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"This is not a DXF file")
            temp_path = f.name
        
        try:
            with open(temp_path, "rb") as f:
                response = client.post(
                    "/api/upload",
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 400
            assert "Only DXF files are supported" in response.json()["detail"]
        finally:
            os.unlink(temp_path)
    
    def test_upload_invalid_dxf(self):
        """Test uploading invalid DXF content"""
        # Create a file with .dxf extension but invalid content
        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
            f.write(b"This is not valid DXF content")
            temp_path = f.name
        
        try:
            with open(temp_path, "rb") as f:
                response = client.post(
                    "/api/upload",
                    files={"file": ("invalid.dxf", f, "application/dxf")}
                )
            
            assert response.status_code == 400
            assert "Invalid DXF file" in response.json()["detail"]
        finally:
            os.unlink(temp_path)


class TestNestEndpoint:
    """Test nesting endpoint"""
    
    @pytest.fixture
    def uploaded_job_id(self):
        """Upload a file and return job_id for testing"""
        test_file = Path(__file__).parent.parent.parent / "Test files" / "01_simple" / "rectangles.dxf"
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("rectangles.dxf", f, "application/dxf")}
            )
        
        return response.json()["job_id"]
    
    def test_nest_valid_job(self, uploaded_job_id):
        """Test nesting with valid job ID"""
        response = client.post(
            f"/api/nest/{uploaded_job_id}",
            data={
                "sheet_width": 600,
                "sheet_height": 400,
                "margin": 5,
                "algorithm": "fast"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["job_id"] == uploaded_job_id
        assert "utilization" in data
        assert "parts_placed" in data
        assert "total_parts" in data
        assert "processing_time" in data
        assert data["download_url"] == f"/api/download/{uploaded_job_id}"
    
    def test_nest_multipass_algorithm(self, uploaded_job_id):
        """Test nesting with multipass algorithm"""
        response = client.post(
            f"/api/nest/{uploaded_job_id}",
            data={
                "sheet_width": 600,
                "sheet_height": 400,
                "margin": 5,
                "algorithm": "multipass"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_nest_invalid_job_id(self):
        """Test nesting with non-existent job ID"""
        response = client.post(
            "/api/nest/invalid-job-id-12345",
            data={
                "sheet_width": 600,
                "sheet_height": 400,
                "margin": 5,
                "algorithm": "fast"
            }
        )
        
        assert response.status_code == 404
        assert "Job not found" in response.json()["detail"]
    
    def test_nest_custom_sheet_size(self, uploaded_job_id):
        """Test nesting with custom sheet dimensions"""
        response = client.post(
            f"/api/nest/{uploaded_job_id}",
            data={
                "sheet_width": 1220,
                "sheet_height": 2440,
                "margin": 10,
                "algorithm": "fast"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestDownloadEndpoint:
    """Test download endpoint"""
    
    @pytest.fixture
    def nested_job_id(self):
        """Upload and nest a file, return job_id"""
        # Upload
        test_file = Path(__file__).parent.parent.parent / "Test files" / "01_simple" / "rectangles.dxf"
        with open(test_file, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("rectangles.dxf", f, "application/dxf")}
            )
        
        job_id = upload_response.json()["job_id"]
        
        # Nest
        client.post(
            f"/api/nest/{job_id}",
            data={
                "sheet_width": 600,
                "sheet_height": 400,
                "margin": 5,
                "algorithm": "fast"
            }
        )
        
        return job_id
    
    def test_download_nested_file(self, nested_job_id):
        """Test downloading nested DXF"""
        response = client.get(f"/api/download/{nested_job_id}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/dxf"
        assert len(response.content) > 0
    
    def test_download_before_nesting(self):
        """Test downloading before nesting should fail"""
        # Upload but don't nest
        test_file = Path(__file__).parent.parent.parent / "Test files" / "01_simple" / "rectangles.dxf"
        with open(test_file, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("rectangles.dxf", f, "application/dxf")}
            )
        
        job_id = upload_response.json()["job_id"]
        
        # Try to download without nesting
        response = client.get(f"/api/download/{job_id}")
        
        assert response.status_code == 404
        assert "Nested file not found" in response.json()["detail"]


class TestCleanupEndpoint:
    """Test cleanup endpoint"""
    
    def test_cleanup_job(self):
        """Test cleaning up job files"""
        # Upload a file
        test_file = Path(__file__).parent.parent.parent / "Test files" / "01_simple" / "rectangles.dxf"
        with open(test_file, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("rectangles.dxf", f, "application/dxf")}
            )
        
        job_id = upload_response.json()["job_id"]
        
        # Cleanup
        response = client.delete(f"/api/cleanup/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert "deleted" in data
        assert data["message"] == "Cleanup completed"


# ============================================================================
# INTEGRATION TESTS - Full Workflow
# ============================================================================

class TestFullWorkflow:
    """Test complete upload → nest → download workflow"""
    
    def test_complete_workflow_fast_algorithm(self):
        """Test full workflow with fast algorithm"""
        # 1. Upload
        test_file = Path(__file__).parent.parent.parent / "Test files" / "01_simple" / "rectangles.dxf"
        with open(test_file, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("rectangles.dxf", f, "application/dxf")}
            )
        
        assert upload_response.status_code == 200
        job_id = upload_response.json()["job_id"]
        
        # 2. Nest
        nest_response = client.post(
            f"/api/nest/{job_id}",
            data={
                "sheet_width": 600,
                "sheet_height": 400,
                "margin": 5,
                "algorithm": "fast"
            }
        )
        
        assert nest_response.status_code == 200
        nest_data = nest_response.json()
        assert nest_data["success"] is True
        assert nest_data["parts_placed"] > 0
        
        # 3. Download
        download_response = client.get(f"/api/download/{job_id}")
        
        assert download_response.status_code == 200
        assert len(download_response.content) > 0
        
        # 4. Cleanup
        cleanup_response = client.delete(f"/api/cleanup/{job_id}")
        
        assert cleanup_response.status_code == 200
    
    def test_complete_workflow_multipass_algorithm(self):
        """Test full workflow with multipass algorithm"""
        # Upload
        test_file = Path(__file__).parent.parent.parent / "Test files" / "01_simple" / "rectangles.dxf"
        with open(test_file, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("rectangles.dxf", f, "application/dxf")}
            )
        
        job_id = upload_response.json()["job_id"]
        
        # Nest with multipass
        nest_response = client.post(
            f"/api/nest/{job_id}",
            data={
                "sheet_width": 600,
                "sheet_height": 400,
                "margin": 5,
                "algorithm": "multipass"
            }
        )
        
        assert nest_response.status_code == 200
        assert nest_response.json()["success"] is True
        
        # Download
        download_response = client.get(f"/api/download/{job_id}")
        assert download_response.status_code == 200


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test API performance"""
    
    def test_nesting_performance(self):
        """Test that nesting completes in reasonable time"""
        # Upload
        test_file = Path(__file__).parent.parent.parent / "Test files" / "01_simple" / "rectangles.dxf"
        with open(test_file, "rb") as f:
            upload_response = client.post(
                "/api/upload",
                files={"file": ("rectangles.dxf", f, "application/dxf")}
            )
        
        job_id = upload_response.json()["job_id"]
        
        # Nest and check processing time
        nest_response = client.post(
            f"/api/nest/{job_id}",
            data={
                "sheet_width": 600,
                "sheet_height": 400,
                "margin": 5,
                "algorithm": "fast"
            }
        )
        
        processing_time = nest_response.json()["processing_time"]
        
        # Fast algorithm should complete in < 5 seconds for small files
        assert processing_time < 5.0, f"Nesting took {processing_time}s, expected < 5s"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

