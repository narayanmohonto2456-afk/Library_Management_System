from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q
from datetime import date, timedelta

from .models import Book, Member, BorrowRecord
from .forms  import (BookForm, BookUpdateForm, MemberForm, MemberUpdateForm,
                     IssueBookForm, SearchForm)


# ══════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'Welcome back, {form.get_user().username}!')
        return redirect('dashboard')
    return render(request, 'library/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ══════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════
@login_required
def dashboard(request):
    overdue_recs = BorrowRecord.objects.filter(
        return_date__isnull=True, due_date__lt=date.today()
    )
    total_fine = sum(r.fine() for r in overdue_recs)

    genre_data = list(
        Book.objects.values('genre').annotate(count=Count('id')).order_by('-count')
    )
    genre_max = genre_data[0]['count'] if genre_data else 1

    stat_cards = [
        ('journals',           'Total Books',    Book.objects.count(),                   '#e3f2fd','#1565c0'),
        ('check-circle',       'Available',      Book.objects.filter(status='Available').count(), '#e8f5e9','#2e7d32'),
        ('arrow-up-circle',    'Issued',         Book.objects.filter(status='Issued').count(),    '#fff8e1','#f57f17'),
        ('people',             'Members',        Member.objects.count(),                 '#f3e5f5','#6a1b9a'),
        ('exclamation-triangle','Overdue',       overdue_recs.count(),                  '#ffebee','#c62828'),
        ('cash',               'Pending Fines',  f'₹{total_fine:.0f}',                  '#fce4ec','#ad1457'),
    ]

    recent_tx = BorrowRecord.objects.select_related('book', 'member').order_by('-id')[:8]

    return render(request, 'library/dashboard.html', {
        'stat_cards':   stat_cards,
        'genre_data':   genre_data,
        'genre_max':    genre_max,
        'recent_tx':    recent_tx,
        'overdue_count': overdue_recs.count(),
        'total_fine':   total_fine,
    })


# ══════════════════════════════════════════════════════════════
#  BOOK CRUD
# ══════════════════════════════════════════════════════════════
@login_required
def book_list(request):
    form  = SearchForm(request.GET or None)
    books = Book.objects.all()
    if form.is_valid():
        q, by = form.cleaned_data['query'], form.cleaned_data['search_by']
        if by == 'title':  books = books.filter(title__icontains=q)
        elif by == 'author': books = books.filter(author__icontains=q)
        elif by == 'genre':  books = books.filter(genre__icontains=q)
    return render(request, 'library/book_list.html', {'books': books, 'form': form})


@login_required
def book_add(request):
    form = BookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Book '{form.cleaned_data['title']}' added!")
        return redirect('book_list')
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Add New Book'})


@login_required
def book_detail(request, pk):
    book    = get_object_or_404(Book, pk=pk)
    history = book.borrowrecord_set.select_related('member').all()
    return render(request, 'library/book_detail.html', {'book': book, 'history': history})


@login_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.is_protected():
        messages.error(request, f"'{book.title}' is '{book.status}' – cannot be edited.")
        return redirect('book_list')
    form = BookUpdateForm(request.POST or None, instance=book)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Book '{book.title}' updated!")
        return redirect('book_list')
    return render(request, 'library/book_form.html',
                  {'form': form, 'action': f'Update: {book.title}'})


@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        if book.is_protected():
            messages.error(request, f"'{book.title}' is '{book.status}' – cannot be deleted.")
        elif book.status == 'Issued':
            messages.error(request, f"'{book.title}' is issued – return it first.")
        else:
            title = book.title
            book.delete()
            messages.success(request, f"Book '{title}' deleted.")
        return redirect('book_list')
    return render(request, 'library/confirm_delete.html',
                  {'object': book, 'type': 'Book', 'back_url': 'book_list'})


# ══════════════════════════════════════════════════════════════
#  MEMBER CRUD
# ══════════════════════════════════════════════════════════════
@login_required
def member_list(request):
    q       = request.GET.get('q', '')
    members = Member.objects.all()
    if q:
        members = members.filter(Q(name__icontains=q) | Q(email__icontains=q))
    return render(request, 'library/member_list.html', {'members': members, 'q': q})


@login_required
def member_add(request):
    form = MemberForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Member '{form.cleaned_data['name']}' registered!")
        return redirect('member_list')
    return render(request, 'library/member_form.html',
                  {'form': form, 'action': 'Register New Member'})


@login_required
def member_detail(request, pk):
    member  = get_object_or_404(Member, pk=pk)
    history = member.borrowrecord_set.select_related('book').all()
    active  = member.active_borrows()
    return render(request, 'library/member_detail.html',
                  {'member': member, 'history': history, 'active': active})


@login_required
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    form   = MemberUpdateForm(request.POST or None, instance=member)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Member '{member.name}' updated!")
        return redirect('member_list')
    return render(request, 'library/member_form.html',
                  {'form': form, 'action': f'Update: {member.name}'})


@login_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        if member.active_count() > 0:
            messages.error(request, f"'{member.name}' has {member.active_count()} unreturned book(s).")
        else:
            name = member.name
            member.delete()
            messages.success(request, f"Member '{name}' removed.")
        return redirect('member_list')
    return render(request, 'library/confirm_delete.html',
                  {'object': member, 'type': 'Member', 'back_url': 'member_list'})


# ══════════════════════════════════════════════════════════════
#  ISSUE & RETURN
# ══════════════════════════════════════════════════════════════
@login_required
def issue_book(request):
    form = IssueBookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        book      = form.cleaned_data['book']
        member    = form.cleaned_data['member']
        loan_days = form.cleaned_data['loan_days']
        due       = date.today() + timedelta(days=loan_days)
        BorrowRecord.objects.create(
            book=book, member=member,
            issue_date=date.today(), due_date=due
        )
        book.status = 'Issued'
        book.save()
        messages.success(request,
            f"'{book.title}' issued to {member.name}. Due: {due.strftime('%d %b %Y')}")
        return redirect('issue_book')
    return render(request, 'library/issue_book.html', {'form': form})


@login_required
def issued_books(request):
    records = (BorrowRecord.objects
               .filter(return_date__isnull=True)
               .select_related('book', 'member'))
    return render(request, 'library/issued_books.html', {'records': records})


@login_required
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, id=record_id, return_date__isnull=True)
    if request.method == 'POST':
        record.return_date = date.today()
        record.save()
        record.book.status = 'Available'
        record.book.save()
        fine_msg = f" | Fine: ₹{record.fine()}" if record.is_overdue() else ""
        messages.success(request,
            f"'{record.book.title}' returned by {record.member.name}.{fine_msg}")
        return redirect('issued_books')
    return render(request, 'library/return_confirm.html', {'record': record})


# ══════════════════════════════════════════════════════════════
#  REPORTS
# ══════════════════════════════════════════════════════════════
@login_required
def overdue_report(request):
    overdue    = (BorrowRecord.objects
                  .filter(return_date__isnull=True, due_date__lt=date.today())
                  .select_related('book', 'member'))
    total_fine = sum(r.fine() for r in overdue)
    return render(request, 'library/overdue_report.html',
                  {'overdue': overdue, 'total_fine': total_fine})


@login_required
def borrow_history(request):
    records = BorrowRecord.objects.select_related('book', 'member').order_by('-id')
    return render(request, 'library/borrow_history.html', {'records': records})
