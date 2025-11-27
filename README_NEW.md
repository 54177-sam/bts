# SIBERINDO BTS GUI - Complete Full-Stack GSM Management System

![SIBERINDO](https://img.shields.io/badge/SIBERINDO-BTS_GUI-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen?style=flat-square)

Aplikasi web manajemen jaringan GSM terpadu berbasis Flask yang menyediakan monitoring real-time, subscriber management, SMS operations, dan BTS scanning dengan antarmuka yang intuitif dan API yang robust.

## 🚀 Quick Start

### Opsi 1: Instalasi Manual (Recommended untuk Development)

```bash
# Clone repository
git clone https://github.com/54177-sam/bts.git
cd bts

# Buat dan aktifkan virtual environment
python3 -m venv siberindo-venv
source siberindo-venv/bin/activate  # atau: siberindo-venv\Scripts\activate (Windows)

# Install dependencies
pip install -r requirements.txt

# Inisialisasi database
python scripts/init_db.py

# Jalankan aplikasi
python app.py
```

Akses aplikasi di http://localhost:5000  
**Default Login**: admin / password123

### Opsi 2: Docker (Recommended untuk Production)

```bash
# Build dan jalankan dengan docker-compose
docker-compose up --build

# Atau hanya build
docker build -t siberindo-bts:latest .
docker run -p 5000:5000 siberindo-bts:latest
```

### Opsi 3: Menggunakan Make Commands

```bash
# Setup otomatis
make setup

# Inisialisasi database
make init-db

# Jalankan aplikasi
make run

# Jalankan dalam development mode
make dev

# Jalankan tests
make test

# Lihat semua commands
make help
```

## ✨ Fitur Utama

### 📊 Dashboard Management
- **Real-time Monitoring**: CPU, Memory, Disk, Network statistics
- **Health Score**: Penilaian kesehatan sistem keseluruhan (0-100)
- **Service Status**: Monitoring 6 layanan utama (SiberindoBTS, SiberindoBSC, SiberindoMSC, SiberindoHLR, SiberindoSGSN, SiberindoGGSN)
- **HackRF Detection**: Support mock dan real device detection

### 👥 Subscriber Management
- **Database Pelanggan**: IMSI, MSISDN, Lokasi, Status tracking
- **CRUD Operations**: Tambah, baca, update, hapus subscriber
- **Search & Filter**: Query berdasarkan IMSI, MSISDN, status
- **Pagination**: Handling data besar dengan efficient pagination
- **Statistics**: Analisis subscriber (active/inactive/suspended)
- **Caching**: 30-second cache untuk performance

### 💬 SMS Management
- **Send SMS**: Kirim SMS standard dan silent messages
- **Batch Operations**: Bulk SMS sending
- **History Tracking**: Riwayat lengkap dengan timestamp dan status
- **Analytics**: Statistik pengiriman SMS

### 🔍 BTS Scanner
- **Frequency Scanning**: GSM900, GSM1800, GSM850, GSM1900
- **Signal Detection**: Penilaian kualitas sinyal (Excellent/Good/Fair/Poor)
- **Real-time Results**: Hasil scanning dinamis
- **Export**: CSV export untuk analisis
- **Mock Mode**: Fallback untuk development tanpa perangkat

### 🔐 Security & Validation
- **Role-based Access Control (RBAC)**: Administrator, Operator, Viewer
- **Input Validation**: IMSI (15 digits), MSISDN (10-15 digits), Email
- **Data Sanitization**: Automatic XSS protection
- **Rate Limiting**: Protection against abuse (built-in & nginx)
- **Session Management**: Secure session handling
- **CSRF Protection**: Token-based CSRF defense

### ⚡ Performance
- **Result Caching**: Multi-level caching (5s-300s)
- **Database Optimization**: WAL mode, connection pooling
- **Batch Operations**: Bulk insert efficiency
- **Request Logging**: Comprehensive request/response logging

## 📁 Struktur Proyek

```
siberindo-bts-gui/
├── app.py                          # Flask application entry point
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker build configuration
├── docker-compose.yml              # Docker Compose configuration
├── nginx.conf                      # Nginx reverse proxy config
├── Makefile                        # Development commands
├── .env.example                    # Environment variables example
│
├── modules/                        # Application modules
│   ├── __init__.py
│   ├── auth.py                    # Authentication & authorization
│   ├── database.py                # Database operations & schema
│   ├── dashboard.py               # Dashboard & monitoring
│   ├── bts_scanner.py             # BTS scanning operations
│   ├── sms_manager.py             # SMS management
│   ├── subscribers.py             # Subscriber management
│   ├── service_manager.py         # Service management
│   ├── hackrf_manager.py          # HackRF device management
│   ├── validators.py              # Input validation & sanitization
│   ├── middleware.py              # API middleware & responses
│   └── helpers.py                 # Helper functions
│
├── templates/                      # Jinja2 templates
│   ├── base.html                  # Base template (layout)
│   ├── dashboard.html             # Dashboard page
│   ├── login.html                 # Login page
│   ├── subscribers.html           # Subscribers management
│   ├── sms_history.html           # SMS history view
│   ├── send_sms.html              # SMS sending form
│   ├── send_silent_sms.html       # Silent SMS form
│   ├── bts_scanner.html           # BTS scanner interface
│   └── error.html                 # Error display
│
├── static/                         # Static files
│   ├── css/                       # Stylesheets
│   ├── js/                        # JavaScript files
│   └── img/                       # Images & assets
│
├── scripts/                        # Utility scripts
│   └── init_db.py                 # Database initialization script
│
├── tests/                          # Test suite
│   └── test_suite.py              # Comprehensive unit tests
│
├── data/                           # Data files
│   └── siberindo_bts.db           # SQLite database (auto-created)
│
├── logs/                           # Application logs
│   └── siberindo_bts.log          # Main application log
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD
│
└── docs/
    ├── README.md                  # This file
    ├── SETUP_GUIDE.md             # Detailed setup instructions
    ├── API_REFERENCE.md           # API endpoint documentation
    ├── CHANGELOG.md               # Version history
    └── INDEX.md                   # Project index
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `GET /auth/profile` - User profile

### Dashboard
- `GET /dashboard/dashboard` - Main dashboard
- `GET /dashboard/api/dashboard/refresh` - Refresh dashboard data
- `GET /dashboard/api/hackrf/detect` - Detect HackRF device

### Subscribers
- `GET /subscribers/subscribers` - View subscribers
- `GET /api/subscribers?limit=10&offset=0` - List subscribers (JSON)
- `POST /api/subscribers` - Create subscriber
- `GET /api/subscribers/{id}` - Get subscriber details
- `PUT /api/subscribers/{id}` - Update subscriber
- `DELETE /api/subscribers/{id}` - Delete subscriber
- `GET /api/subscribers/count` - Get subscriber count
- `GET /api/subscribers/stats` - Get subscriber statistics

### SMS Management
- `GET /sms/send_sms` - SMS sending form
- `POST /api/sms/send` - Send SMS
- `POST /api/sms/batch` - Batch send SMS
- `GET /api/sms/history` - SMS history
- `GET /sms/sms_history` - View SMS history

### BTS Scanner
- `GET /scanner/bts_scanner` - BTS scanner interface
- `GET /api/scanner/scan` - Trigger BTS scan
- `GET /api/scanner/results` - Get scan results

### System
- `GET /health` - Health check endpoint
- `GET /api/services/status` - Services status

## 🛠️ Development

### Setup Development Environment

```bash
make setup      # Setup venv and install dependencies
make init-db    # Initialize database
make dev        # Run in development mode
```

### Run Tests

```bash
make test              # Run all tests
make test-coverage     # Run with coverage report
make lint              # Run linting (flake8)
make format            # Format code (black + isort)
```

### Database Management

```bash
make init-db           # Initialize database
make db-reset          # Reset database (WARNING: deletes all data!)
```

### Docker Development

```bash
make docker-build      # Build Docker image
make docker-up         # Start containers
make docker-down       # Stop containers
make docker-logs       # View container logs
```

## 📋 Database Schema

### users table
- `id` - Primary key
- `username` - Unique username
- `password_hash` - SHA-256 hashed password
- `email` - User email
- `full_name` - Full name
- `role` - User role (administrator/operator/viewer)
- `enabled` - Account status
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### subscribers table
- `id` - Primary key
- `imsi` - International Mobile Subscriber Identity (unique)
- `msisdn` - Phone number (unique)
- `name` - Subscriber name
- `status` - Account status (active/inactive/suspended/blocked)
- `network_type` - Network type (GSM/3G/4G/LTE)
- `location` - Subscriber location
- `operator` - Network operator
- `balance` - Account balance
- `last_activity` - Last activity timestamp
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### sms_history table
- `id` - Primary key
- `from_subscriber` - Sender IMSI
- `to_subscriber` - Receiver IMSI
- `message_text` - SMS content
- `message_type` - Message type (standard/silent/flash)
- `status` - Delivery status (pending/sent/delivered/failed)
- `error_code` - Error code if failed
- `error_message` - Error description
- `created_at` - Creation timestamp

### bts_scans table
- `id` - Primary key
- `band` - Frequency band (GSM900/GSM1800/GSM850/GSM1900)
- `frequency` - Frequency value
- `mcc` - Mobile Country Code
- `mnc` - Mobile Network Code
- `lac` - Location Area Code
- `cell_id` - Cell identifier
- `signal_strength` - Signal strength (-150 to 0 dBm)
- `signal_quality` - Quality assessment (excellent/good/fair/poor)
- `operator_name` - Operator name
- `scan_timestamp` - Scan time
- `created_at` - Creation timestamp

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t siberindo-bts:latest .
```

### Run Container
```bash
docker run -d \
  --name siberindo-bts \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  siberindo-bts:latest
```

### Docker Compose
```bash
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose logs -f            # View logs
docker-compose ps                 # Show status
```

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed installation & configuration
- **[API_REFERENCE.md](API_REFERENCE.md)** - API documentation with examples
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[INDEX.md](INDEX.md)** - Project index

## 🧪 Testing

### Run Full Test Suite
```bash
pytest tests/test_suite.py -v
```

### Run Specific Test
```bash
pytest tests/test_suite.py::TestFlaskRoutes::test_dashboard_endpoint -v
```

### Coverage Report
```bash
pytest tests/test_suite.py --cov=modules --cov-report=html
```

## 🔒 Security Considerations

1. **Environment Variables**: Gunakan `.env` file untuk sensitive data
   - Ubah `SECRET_KEY` di production
   - Set `DEBUG=False` di production
   - Set `SESSION_COOKIE_SECURE=True` untuk HTTPS

2. **Database**: 
   - Backup regular
   - Restrict file permissions
   - Use strong passwords

3. **API Security**:
   - Rate limiting enabled
   - CSRF protection active
   - Input validation on all endpoints
   - SQL injection prevention via parameterized queries

4. **SSL/TLS**:
   - Use HTTPS in production
   - Generate proper SSL certificates
   - Configure nginx for SSL

## 📦 Dependencies

- **Flask** - Web framework
- **SQLite3** - Database
- **psutil** - System monitoring
- **PyJWT** - JWT authentication
- **Flask-Session** - Session management
- **Werkzeug** - WSGI utilities

## 🚨 Known Issues & Limitations

- HackRF support requires libhackrf library (mocked in dev mode)
- SMS sending requires external SMS gateway (mocked in dev mode)
- Rate limiting uses in-memory store (use Redis in production)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feat/your-feature`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feat/your-feature`)
5. Create Pull Request

## 📞 Support

- Open an issue on GitHub
- Check existing issues for solutions
- Review documentation in `/docs` folder

## 🎯 Roadmap

### v2.1.0 (Next)
- [ ] Redis caching support
- [ ] PostgreSQL database support
- [ ] WebSocket real-time updates
- [ ] Mobile app API

### v3.0.0 (Future)
- [ ] Multi-tenant support
- [ ] Advanced analytics dashboard
- [ ] Machine learning-based anomaly detection
- [ ] Kubernetes deployment

---

**SIBERINDO BTS GUI** - Transforming GSM Network Management ✨

Made with ❤️ by the SIBERINDO Team
