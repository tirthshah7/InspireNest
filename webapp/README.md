# 🚀 Nesting SAAS - Web Application

**Status**: MVP Development  
**Goal**: Turn proven nesting engine into SAAS product  
**Timeline**: Week 1-2 (MVP)

---

## 📁 **Project Structure**

```
webapp/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── requirements.txt # Python dependencies
│   └── README.md
├── frontend/            # React frontend
│   ├── src/            # React components
│   ├── package.json    # Node dependencies
│   └── README.md
├── docker-compose.yml   # Docker setup (coming soon)
└── README.md           # This file
```

---

## 🚀 **Quick Start**

### **Backend (FastAPI)**

```bash
# 1. Navigate to backend
cd webapp/backend

# 2. Activate virtual environment
source ../../venv/bin/activate

# 3. Install dependencies (if needed)
pip install -r requirements.txt

# 4. Run server
python main.py

# Server runs on: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### **Frontend (React)** [Coming Soon]

```bash
# 1. Navigate to frontend
cd webapp/frontend

# 2. Install dependencies
npm install

# 3. Run dev server
npm run dev

# Frontend runs on: http://localhost:5173
```

---

## 🔌 **API Endpoints**

### **1. Health Check**
```
GET /
```

### **2. Upload DXF**
```
POST /api/upload
Content-Type: multipart/form-data

Form Data:
  file: <DXF file>

Response:
  {
    "job_id": "uuid",
    "filename": "parts.dxf",
    "num_parts": 24,
    "total_area": 76567.5,
    "message": "File uploaded successfully"
  }
```

### **3. Run Nesting**
```
POST /api/nest/{job_id}
Content-Type: multipart/form-data

Form Data:
  sheet_width: 600 (mm)
  sheet_height: 400 (mm)
  margin: 5 (mm)
  algorithm: "fast" or "multipass"

Response:
  {
    "job_id": "uuid",
    "success": true,
    "message": "Nesting completed successfully",
    "utilization": 21.5,
    "parts_placed": 12,
    "total_parts": 24,
    "processing_time": 8.3,
    "download_url": "/api/download/{job_id}"
  }
```

### **4. Download Nested DXF**
```
GET /api/download/{job_id}

Returns: DXF file
```

### **5. Cleanup**
```
DELETE /api/cleanup/{job_id}

Response:
  {
    "job_id": "uuid",
    "deleted": ["upload", "output"],
    "message": "Cleanup completed"
  }
```

---

## 🧪 **Testing**

### **Manual Test (using curl)**

```bash
# 1. Start backend
cd webapp/backend
python main.py

# 2. Upload DXF (in another terminal)
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@../../Test files/01_simple/rectangles.dxf"

# Response: {"job_id":"abc-123",...}

# 3. Run nesting
curl -X POST "http://localhost:8000/api/nest/abc-123" \
  -F "sheet_width=600" \
  -F "sheet_height=400" \
  -F "margin=5" \
  -F "algorithm=fast"

# Response: {"utilization":9.17,...}

# 4. Download result
curl "http://localhost:8000/api/download/abc-123" \
  -o nested_output.dxf
```

### **Browser Test**

Visit: http://localhost:8000/docs

Interactive API documentation (Swagger UI)

---

## 📋 **Development Roadmap**

### **✅ Week 1: Backend MVP**
- [x] FastAPI setup
- [x] Upload endpoint
- [x] Nesting endpoint
- [x] Download endpoint
- [x] Integration with engine
- [ ] Error handling
- [ ] Logging

### **⏳ Week 1-2: Frontend MVP**
- [ ] React + Vite setup
- [ ] File upload UI
- [ ] Sheet config form
- [ ] Progress indicator
- [ ] Results display
- [ ] Download button
- [ ] Error messages

### **⏳ Week 2: Integration & Deploy**
- [ ] Connect frontend to backend
- [ ] End-to-end testing
- [ ] Docker setup
- [ ] Deploy to Railway/Heroku
- [ ] Domain setup

---

## 🎯 **Next Steps**

1. **Test backend** ✅
2. **Build frontend** ⏳
3. **Integration** ⏳
4. **Deploy** ⏳

---

**Last Updated**: 2025-10-20  
**Status**: Backend Complete, Frontend Next

