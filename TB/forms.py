from django import forms
from .models import ThongBao


class ThongBaoForm(forms.ModelForm):
    class Meta:
        model = ThongBao
        fields = ['nguoi_nhan', 'tieu_de', 'noi_dung']
        widgets = {
            'tieu_de': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tiêu đề...'}),
            'noi_dung': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Nhập nội dung...'}),
            'nguoi_nhan': forms.Select(attrs={'class': 'form-control'}),
        }
class KhuyenMaiForm(forms.ModelForm):
    class Meta:
        model = ThongBao
        fields = ['tieu_de', 'noi_dung', 'hinh_anh']
        labels = {
            'tieu_de': 'Tiêu đề khuyến mãi',
            'noi_dung': 'Nội dung khuyến mãi',
            'hinh_anh': 'Hình ảnh khuyến mãi',
        }


        widgets = {
            'tieu_de': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tiêu đề khuyến mãi...'
            }),
            'noi_dung': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Nhập nội dung chi tiết...'
            }),
            # Upload hình ảnh
            'hinh_anh': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }