# Library Management System

A comprehensive Django-based library management application for tracking books, members, and borrowing transactions with a complete CRUD interface and reporting capabilities.

## 📋 Features

### Core Functionality
- **Book Management**: Add, update, view, and delete books with detailed metadata
- **Member Management**: Register members, track membership types, and manage member profiles
- **Borrow Transactions**: Issue books to members, track return dates, and calculate overdue fines
- **Dashboard**: Real-time statistics showing total books, available inventory, issued count, members, and pending fines
- **Search & Filter**: Search books by title, author, or genre; filter members by name or email

### Book Management
- Track book status: Available, Issued, Rare, Reference Only, Lost
- Categorize by genre (Computer Science, AI, Mathematics, Literature, etc.)
- Store multiple copies per book title
- Prevent editing/deletion of Rare and Reference Only books
- View complete borrowing history for each book

### Member Management
- Support multiple membership tiers: Standard, Premium, Student
- Limit borrowing (max 3 active books per member)
- Track join date and contact information
- View member borrowing history and current active loans

### Transactions
- Issue books with customizable loan periods (default: 14 days)
- Automatic due date calculation
- Return books with automatic status updates
- Automatic fine calculation for overdue returns (₹2 per day)

### Reporting
- **Overdue Report**: Track all overdue items with outstanding fines
- **Borrow History**: Complete transaction log with status labels
- **Genre Analytics**: Visualize book distribution by genre
- **Dashboard Charts**: Genre-based bar chart showing inventory breakdown

### Authentication
- Secure login system with session management
- User-based access control
- Logout functionality with session cleanup

## 🛠️ Technology Stack

- **Backend**: Django 3.x/4.x
- **Database**: SQLite
- **Frontend**: Django Templates with Bootstrap styling
- **Authentication**: Django built-in auth system
- **ORM**: Django ORM for database operations

## 📁 Project Structure

```
library_project/
├── library/                 # Main Django app
│   ├── models.py           # Book, Member, BorrowRecord models
│   ├── views.py            # View functions for all features
│   ├── urls.py             # URL routing
│   ├── forms.py            # Django forms
│   ├── admin.py            # Django admin configuration
│   └── tests.py            # Test cases
├── library_project/        # Project settings
│   ├── settings.py         # Django configuration
│   ├── urls.py             # Root URL config
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
├── templates/              # HTML templates
│   └── library/            # App-specific templates
├── static/                 # Static files (CSS, JS, images)
├── manage.py               # Django management script
├── db.sqlite3              # SQLite database
└── README.md               # This file
```

## 📊 Database Models

### Book Model
- `book_id`: Unique identifier
- `title`: Book title
- `author`: Author name
- `genre`: Book category
- `year`: Publication year
- `copies`: Number of copies
- `status`: Current status (Available, Issued, Rare, Reference Only, Lost)
- `added_on`: Date added to library

### Member Model
- `member_id`: Unique member identifier
- `name`: Member name
- `email`: Email address (unique)
- `phone`: Contact number
- `membership`: Tier (Standard, Premium, Student)
- `joined_on`: Registration date

### BorrowRecord Model
- `book`: Foreign key to Book
- `member`: Foreign key to Member
- `issue_date`: When book was borrowed
- `due_date`: When book should be returned (default: 14 days)
- `return_date`: Actual return date (null if not returned)
- `fine`: Auto-calculated based on overdue days (₹2/day)

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Django 3.0+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd library_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Application: `http://localhost:8000/`
   - Admin panel: `http://localhost:8000/admin/`

## 📖 Usage Guide

### Dashboard
- View library statistics at a glance
- See recently issued/returned books
- Monitor pending fines and overdue items

### Managing Books
- **Add Book**: Navigate to Books → Add New Book
- **View Books**: Browse all books with search functionality
- **Edit Book**: Update book details (unavailable for protected books)
- **Delete Book**: Remove books (not issued, not protected)
- **Book Detail**: View complete borrowing history

### Managing Members
- **Register Member**: Navigate to Members → Register New Member
- **View Members**: Browse all registered members with search
- **Edit Member**: Update member information
- **Member Detail**: Check active loans and borrowing history
- **Remove Member**: Delete member (no active loans required)

### Borrowing Operations
- **Issue Book**: Select book and member, set loan period
- **View Issued Books**: See all currently borrowed items
- **Return Book**: Mark book as returned, check for fines

### Reports
- **Overdue Report**: See overdue items with calculated fines
- **Borrow History**: Complete transaction log with all statuses

## 🔐 Security Features

- Login required for all library operations
- Session-based authentication
- CSRF protection
- SQL injection prevention via Django ORM
- Protected status books cannot be edited or deleted

## 🎨 User Interface

- Clean, responsive design
- Color-coded status indicators
- Search bars for easy navigation
- Confirmation dialogs for destructive actions
- Flash messages for user feedback
- Genre-based analytics visualization

## 🔧 Configuration

### Important Settings (library_project/settings.py)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Configure allowed domains
- `SECRET_KEY`: Change before production deployment
- `DATABASES`: Configure database settings

### Fine Calculation
- Default: ₹2 per day overdue
- Located in `BorrowRecord.FINE_PER_DAY` in models.py

### Loan Period
- Default: 14 days
- Customizable during issue via `loan_days` form field

## 📝 API Endpoints

### Authentication
- `GET/POST /login/` - User login
- `GET /logout/` - User logout

### Dashboard
- `GET /` - Dashboard overview

### Books
- `GET /books/` - List all books
- `POST /books/add/` - Add new book
- `GET /books/<id>/` - Book details
- `POST /books/<id>/edit/` - Update book
- `POST /books/<id>/delete/` - Delete book

### Members
- `GET /members/` - List all members
- `POST /members/add/` - Register member
- `GET /members/<id>/` - Member details
- `POST /members/<id>/edit/` - Update member
- `POST /members/<id>/delete/` - Remove member

### Transactions
- `GET/POST /issue/` - Issue book to member
- `GET /issued/` - View all issued books
- `POST /return/<record_id>/` - Return book

### Reports
- `GET /reports/overdue/` - Overdue items report
- `GET /reports/history/` - Complete borrow history

## 🧪 Testing

Run tests with:
```bash
python manage.py test library
```

## 📄 License

This project is open source. Modify and use as needed.

## 👥 Contributing

Feel free to fork, modify, and submit pull requests to improve the system.

## 💡 Future Enhancements

- Email notifications for due dates
- Fine payment tracking
- Reservation system for unavailable books
- Advanced analytics and reports
- Book cover images
- Integration with ISBN database
- Mobile app
- Multi-language support

## 📞 Support

For issues or questions, please open an issue in the repository.

---

**Created**: 2024  
**Version**: 1.0
