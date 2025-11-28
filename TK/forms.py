from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import KhachHang, ThuCung, NhanVien, TichDiem

class DangKyForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng.")
        return email

class KhachHangForm(forms.ModelForm):
    class Meta:
        model = KhachHang
        fields = ['ho_ten', 'gioi_tinh', 'so_dien_thoai', 'ngay_sinh', 'dia_chi', 'email']
        widgets = {
            'ngay_sinh': forms.DateInput(attrs={'type': 'date'}),
        }
class NhanVienForm(forms.ModelForm):
   class Meta:
       model = NhanVien
       fields = ['ho_ten', 'email', 'so_dien_thoai', 'dia_chi', 'ngay_vao_lam']

class ThuCungForm(forms.ModelForm):
    class Meta:
        model = ThuCung
        fields = ['ten_thucung', 'loai', 'tuoi', 'can_nang', 'ghi_chu']
        widgets = {
            'ten_thucung': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Tên thú cưng'}),
            'loai': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Loài'}),
            'tuoi': forms.NumberInput(attrs={'class': 'form-control','placeholder': 'Tuổi'}),
            'can_nang': forms.NumberInput(attrs={'class': 'form-control','placeholder': 'Cân nặng (kg)'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control','rows': 3,'placeholder': 'Nhập ghi chú...'}),
        }


class CapNhatDiemForm(forms.ModelForm):
    class Meta:
        model = TichDiem
        fields = ['tong_diem']
        widgets = {
            'tong_diem': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập điểm mới...'
            })
        }
