from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


# ══════════════════════════════════════════
#  Book Model
# ══════════════════════════════════════════
class Book(models.Model):
    STATUS_CHOICES = [
        ('Available',      'Available'),
        ('Issued',         'Issued'),
        ('Rare',           'Rare'),
        ('Reference Only', 'Reference Only'),
        ('Lost',           'Lost'),
    ]
    GENRE_CHOICES = [
        ('Computer Science',        'Computer Science'),
        ('Software Engineering',    'Software Engineering'),
        ('Artificial Intelligence', 'Artificial Intelligence'),
        ('Data Science',            'Data Science'),
        ('Mathematics',             'Mathematics'),
        ('Physics',                 'Physics'),
        ('History',                 'History'),
        ('Literature',              'Literature'),
        ('Economics',               'Economics'),
        ('Reference',               'Reference'),
        ('Mythology',               'Mythology'),
        ('Other',                   'Other'),
    ]

    book_id  = models.CharField(max_length=20, unique=True)
    title    = models.CharField(max_length=200)
    author   = models.CharField(max_length=150)
    genre    = models.CharField(max_length=50, choices=GENRE_CHOICES, default='Other')
    year     = models.IntegerField()
    copies   = models.PositiveIntegerField(default=1)
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    added_on = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def is_protected(self):
        return self.status in ('Rare', 'Reference Only')

    def is_available(self):
        return self.status == 'Available'

    def total_borrows(self):
        return self.borrowrecord_set.count()

    def active_record(self):
        return self.borrowrecord_set.filter(return_date__isnull=True).first()

    def __str__(self):
        return f"[{self.book_id}] {self.title}"


# ══════════════════════════════════════════
#  Member Model
# ══════════════════════════════════════════
class Member(models.Model):
    MEMBERSHIP_CHOICES = [
        ('Standard', 'Standard'),
        ('Premium',  'Premium'),
        ('Student',  'Student'),
    ]
    MAX_BOOKS = 3

    member_id  = models.CharField(max_length=20, unique=True)
    name       = models.CharField(max_length=150)
    email      = models.EmailField(unique=True)
    phone      = models.CharField(max_length=15)
    membership = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='Standard')
    joined_on  = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def active_borrows(self):
        return self.borrowrecord_set.filter(return_date__isnull=True)

    def active_count(self):
        return self.active_borrows().count()

    def can_borrow(self):
        return self.active_count() < self.MAX_BOOKS

    def total_borrowed(self):
        return self.borrowrecord_set.count()

    def __str__(self):
        return f"[{self.member_id}] {self.name}"


# ══════════════════════════════════════════
#  BorrowRecord Model
# ══════════════════════════════════════════
class BorrowRecord(models.Model):
    FINE_PER_DAY = 2.0

    book        = models.ForeignKey(Book,   on_delete=models.CASCADE)
    member      = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date  = models.DateField(default=date.today)
    due_date    = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-issue_date']

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=14)
        super().save(*args, **kwargs)

    def is_returned(self):
        return self.return_date is not None

    def is_overdue(self):
        check = self.return_date or date.today()
        return check > self.due_date

    def overdue_days(self):
        if not self.is_overdue():
            return 0
        check = self.return_date or date.today()
        return (check - self.due_date).days

    def fine(self):
        return round(self.overdue_days() * self.FINE_PER_DAY, 2)

    def days_remaining(self):
        if self.is_returned():
            return 0
        return max((self.due_date - date.today()).days, 0)

    def status_label(self):
        if self.is_returned():
            if self.is_overdue():
                return f"Returned (Overdue {self.overdue_days()}d | Fine ₹{self.fine()})"
            return "Returned On Time"
        if self.is_overdue():
            return f"OVERDUE by {self.overdue_days()} day(s) | Fine ₹{self.fine()}"
        return f"Active – {self.days_remaining()} day(s) left"

    def __str__(self):
        return f"{self.book.title} → {self.member.name} ({self.issue_date})"
