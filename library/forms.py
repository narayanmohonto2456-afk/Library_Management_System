from django import forms
from .models import Book, Member, BorrowRecord
from datetime import date, timedelta


class BookForm(forms.ModelForm):
    class Meta:
        model  = Book
        fields = ['book_id', 'title', 'author', 'genre', 'year', 'copies', 'status']
        widgets = {
            'book_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B001'}),
            'title':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book Title'}),
            'author':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author Name'}),
            'genre':   forms.Select(attrs={'class': 'form-select'}),
            'year':    forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2024'}),
            'copies':  forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status':  forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_year(self):
        y = self.cleaned_data.get('year')
        if y and (y < 1000 or y > date.today().year):
            raise forms.ValidationError(f"Year must be between 1000 and {date.today().year}.")
        return y


class BookUpdateForm(forms.ModelForm):
    """Same as BookForm but book_id is read-only after creation."""
    class Meta:
        model  = Book
        fields = ['title', 'author', 'genre', 'year', 'copies', 'status']
        widgets = {
            'title':  forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'genre':  forms.Select(attrs={'class': 'form-select'}),
            'year':   forms.NumberInput(attrs={'class': 'form-control'}),
            'copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class MemberForm(forms.ModelForm):
    class Meta:
        model  = Member
        fields = ['member_id', 'name', 'email', 'phone', 'membership']
        widgets = {
            'member_id':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. M001'}),
            'name':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9800000000'}),
            'membership': forms.Select(attrs={'class': 'form-select'}),
        }


class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model  = Member
        fields = ['name', 'email', 'phone', 'membership']
        widgets = {
            'name':       forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control'}),
            'membership': forms.Select(attrs={'class': 'form-select'}),
        }


class IssueBookForm(forms.Form):
    book_id   = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book ID e.g. B001'})
    )
    member_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Member ID e.g. M001'})
    )
    loan_days = forms.IntegerField(
        initial=14, min_value=1, max_value=60,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned = super().clean()
        book_id   = cleaned.get('book_id')
        member_id = cleaned.get('member_id')

        try:
            book = Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            raise forms.ValidationError(f"No book found with ID '{book_id}'.")

        try:
            member = Member.objects.get(member_id=member_id)
        except Member.DoesNotExist:
            raise forms.ValidationError(f"No member found with ID '{member_id}'.")

        if book.is_protected():
            raise forms.ValidationError(f"'{book.title}' is '{book.status}' and cannot be issued.")
        if not book.is_available():
            raise forms.ValidationError(f"'{book.title}' is currently '{book.status}'.")
        if not member.can_borrow():
            raise forms.ValidationError(f"{member.name} has reached the borrow limit (3 books).")

        cleaned['book']   = book
        cleaned['member'] = member
        return cleaned


class ReturnBookForm(forms.Form):
    record_id = forms.IntegerField(widget=forms.HiddenInput())


class SearchForm(forms.Form):
    SEARCH_CHOICES = [
        ('title',  'Title'),
        ('author', 'Author'),
        ('genre',  'Genre'),
    ]
    query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search books...'
        })
    )
    search_by = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
