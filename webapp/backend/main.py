"""
FastAPI Backend for Nesting SAAS

Simple web API for DXF nesting:
- Upload DXF file
- Configure sheet size & algorithm
- Run nesting
- Download nested DXF

Author: Laser Cutting Nesting System
Date: 2025-10-20
"""

import sys
import os
from pathlib import Path
from typing import Optional
import tempfile
import uuid
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add parent directory to path to import our engine
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from file_io.dxf_importer import import_dxf_file
from engine.config import NestingConfig
from optimization.fast_optimal_nester import fast_nest
from optimization.multipass_nester import MultiPassNester
from optimization.iterative_nester import iterative_nest
from optimization.ai_intelligent_nester import ai_intelligent_nest
from scoring.multi_objective import NestingSolution

# Initialize FastAPI app
app = FastAPI(
    title="Nesting SAAS API",
    description="AI-Powered Laser Cutting Nesting Tool",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary storage for uploaded/processed files
UPLOAD_DIR = Path(tempfile.gettempdir()) / "nesting_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path(tempfile.gettempdir()) / "nesting_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# Helper functions
def create_config(sheet_width: float, sheet_height: float, margin: float) -> NestingConfig:
    """Create a NestingConfig from sheet parameters"""
    from constraints.sheet import SheetConstraints
    from constraints.spacing import SpacingConstraints
    from constraints.rotation import RotationConstraints
    
    return NestingConfig(
        sheet=SheetConstraints(
            width=sheet_width,
            height=sheet_height,
            margin_left=margin,
            margin_right=margin,
            margin_top=margin,
            margin_bottom=margin
        ),
        spacing=SpacingConstraints(
            kerf_width=0.2,
            min_web=0.5
        ),
        rotation=RotationConstraints(
            allowed_angles=[0, 90, 180, 270]
        )
    )


# Models
class NestingRequest(BaseModel):
    """Nesting job configuration"""
    sheet_width: float = 600
    sheet_height: float = 400
    margin: float = 5
    algorithm: str = "fast"  # "fast" or "multipass"


class NestingResponse(BaseModel):
    """Nesting job result"""
    job_id: str
    success: bool
    message: str
    utilization: Optional[float] = None
    parts_placed: Optional[int] = None
    total_parts: Optional[int] = None
    processing_time: Optional[float] = None
    download_url: Optional[str] = None


# Routes
@app.get("/")
async def root():
    """API root - health check"""
    return {
        "status": "online",
        "service": "Nesting SAAS API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint for deployment platforms"""
    return {
        "status": "healthy",
        "service": "inspirenest-backend",
        "version": "1.0.0"
    }


@app.post("/api/upload", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a DXF file for nesting.
    
    Returns job_id for tracking.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.dxf'):
            raise HTTPException(status_code=400, detail="Only DXF files are supported")
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded file
        upload_path = UPLOAD_DIR / f"{job_id}.dxf"
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Quick validation - try to load it
        try:
            polygons, stats = import_dxf_file(str(upload_path))
            num_parts = len(polygons)
            total_area = sum(p.area for p in polygons)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid DXF file: {str(e)}")
        
        return {
            "job_id": job_id,
            "filename": file.filename,
            "num_parts": num_parts,
            "total_area": round(total_area, 2),
            "message": "File uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/nest/{job_id}", response_model=NestingResponse)
async def nest_parts(
    job_id: str,
    sheet_width: float = Form(600),
    sheet_height: float = Form(400),
    margin: float = Form(5),
    algorithm: str = Form("fast")
):
    """
    Run nesting on uploaded file.
    
    Args:
        job_id: Job ID from upload
        sheet_width: Sheet width in mm
        sheet_height: Sheet height in mm
        margin: Margin in mm (applied to all sides)
        algorithm: "fast" or "multipass"
    """
    import time
    
    try:
        # Check if file exists
        upload_path = UPLOAD_DIR / f"{job_id}.dxf"
        if not upload_path.exists():
            raise HTTPException(status_code=404, detail="Job not found. Please upload file first.")
        
        # Load DXF file
        start_time = time.time()
        polygons, stats = import_dxf_file(str(upload_path))
        
        # Create config (using helper function)
        config = create_config(sheet_width, sheet_height, margin)
        
        # Run nesting
        if algorithm == "multipass":
            nester = MultiPassNester(config, verbose=False)
            solution = nester.nest(polygons)
        elif algorithm == "iterative":
            solution = iterative_nest(polygons, config, verbose=False)
        elif algorithm == "ai":
            solution = ai_intelligent_nest(polygons, config, verbose=False)
        else:  # "fast" (default) - now uses Minkowski collision detection by default
            solution = fast_nest(polygons, config, verbose=False, use_minkowski=True)
        
        processing_time = time.time() - start_time
        
        # Export nested DXF
        output_path = OUTPUT_DIR / f"{job_id}_nested.dxf"
        export_nested_dxf(solution, str(output_path))
        
        return NestingResponse(
            job_id=job_id,
            success=True,
            message="Nesting completed successfully",
            utilization=round(solution.utilization, 2),
            parts_placed=len(solution.placed_parts),
            total_parts=len(polygons),
            processing_time=round(processing_time, 2),
            download_url=f"/api/download/{job_id}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Nesting failed: {str(e)}")


@app.get("/api/download/{job_id}")
async def download_nested_file(job_id: str):
    """
    Download the nested DXF file.
    """
    output_path = OUTPUT_DIR / f"{job_id}_nested.dxf"
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Nested file not found. Please run nesting first.")
    
    return FileResponse(
        path=str(output_path),
        filename=f"nested_{job_id}.dxf",
        media_type="application/dxf"
    )


@app.delete("/api/cleanup/{job_id}")
async def cleanup_job(job_id: str):
    """
    Clean up temporary files for a job.
    """
    upload_path = UPLOAD_DIR / f"{job_id}.dxf"
    output_path = OUTPUT_DIR / f"{job_id}_nested.dxf"
    
    deleted = []
    if upload_path.exists():
        upload_path.unlink()
        deleted.append("upload")
    if output_path.exists():
        output_path.unlink()
        deleted.append("output")
    
    return {
        "job_id": job_id,
        "deleted": deleted,
        "message": "Cleanup completed"
    }


def export_nested_dxf(solution: NestingSolution, output_path: str):
    """
    Export nested solution to DXF file.
    
    Places all parts in their nested positions on a single sheet.
    """
    import ezdxf
    from ezdxf import units
    
    # Create new DXF document
    doc = ezdxf.new('R2010', setup=True)
    doc.units = units.MM
    msp = doc.modelspace()
    
    # Add sheet boundary (for reference)
    sheet_rect = [
        (0, 0),
        (solution.sheet_width, 0),
        (solution.sheet_width, solution.sheet_height),
        (0, solution.sheet_height),
        (0, 0)
    ]
    msp.add_lwpolyline(sheet_rect, dxfattribs={'layer': 'SHEET', 'color': 8})
    
    # Add each placed part
    for poly, x, y, rotation in solution.placed_parts:
        # Create a PlacedPart to get the properly transformed polygon
        from geometry.collision import PlacedPart
        placed_part = PlacedPart(poly, x, y, rotation)
        transformed_poly = placed_part.get_transformed_polygon()
        
        # Add outer boundary
        outer_boundary = [(v.x, v.y) for v in transformed_poly.vertices]
        msp.add_lwpolyline(outer_boundary, close=True, dxfattribs={'layer': 'PARTS', 'color': 1})
        
        # Add holes if they exist
        if transformed_poly.has_holes:
            for hole in transformed_poly.holes:
                hole_boundary = [(v.x, v.y) for v in hole]
                msp.add_lwpolyline(hole_boundary, close=True, dxfattribs={'layer': 'HOLES', 'color': 2})
    
    # Save
    doc.saveas(output_path)


# Run server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )

