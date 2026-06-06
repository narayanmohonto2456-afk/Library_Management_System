from django.contrib import admin
from .models import Book, Member, BorrowRecord

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display  = ['book_id', 'title', 'author', 'genre', 'status', 'copies']
    list_filter   = ['status', 'genre']
    search_fields = ['title', 'author', 'book_id']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display  = ['member_id', 'name', 'email', 'membership', 'joined_on']
    search_fields = ['name', 'email', 'member_id']

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display  = ['book', 'member', 'issue_date', 'due_date', 'return_date']
    list_filter   = ['return_date']
