from django import forms
from .models import LichHen
from DV.models import DichVu
from TK.models import ThuCung


class LichHenForm(forms.ModelForm):
    # 🐶 Chọn thú cưng hiện có
    thu_cung = forms.ModelChoiceField(
        queryset=ThuCung.objects.none(),
        label="Thú cưng",
        required=False
    )

    # 💅 Chọn dịch vụ (nhiều chọn)
    dich_vu = forms.ModelMultipleChoiceField(
        queryset=DichVu.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Dịch vụ",
        required=True
    )

    # 📞 Thêm số điện thoại bắt buộc 10 số
    so_dien_thoai = forms.CharField(
        label="Số điện thoại",
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nhập số điện thoại 10 số',
            'pattern': r'\d{10}',  # ✅ Regex HTML kiểm tra 10 chữ số
            'title': 'Số điện thoại phải gồm đúng 10 chữ số',
            'class': 'form-control'
        })
    )

    # 🐾 Nếu người dùng thêm thú cưng mới
    ten_thu_cung_moi = forms.CharField(max_length=100, required=False, label="Tên thú cưng mới")
    loai = forms.CharField(max_length=100, required=False, label="Loài")
    tuoi = forms.IntegerField(required=False, label="Tuổi")
    can_nang = forms.FloatField(required=False, label="Cân nặng (kg)")

    # ⏰ Thời gian và ghi chú
    thoi_gian = forms.DateTimeField(
        label="Thời gian hẹn",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    ghi_chu = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ghi chú thêm (nếu có)...'}),
        required=False,
        label="Ghi chú"
    )

    class Meta:
        model = LichHen
        fields = [
            'thu_cung',
            'ten_thu_cung_moi',
            'loai',
            'tuoi',
            'can_nang',
            'so_dien_thoai',
            'dich_vu',
            'thoi_gian',
            'ghi_chu'
        ]

    def __init__(self, *args, **kwargs):
        # ✅ Truyền tham số 'khach_hang' từ views
        khach_hang = kwargs.pop('khach_hang', None)
        super().__init__(*args, **kwargs)
        if khach_hang:
            self.fields['thu_cung'].queryset = ThuCung.objects.filter(khach_hang=khach_hang)

    def clean(self):
        cleaned_data = super().clean()

        thu_cung = cleaned_data.get('thu_cung')
        ten_moi = cleaned_data.get('ten_thu_cung_moi')
        tuoi = cleaned_data.get('tuoi')
        can_nang = cleaned_data.get('can_nang')

        # ❌ Không được vừa chọn thú cưng cũ vừa nhập thú cưng mới
        if thu_cung and ten_moi:
            raise forms.ValidationError(
                "Bạn chỉ được chọn thú cưng hiện có hoặc thêm mới, không được nhập cả hai."
            )

        # 🐾 Nếu thêm thú cưng mới → kiểm tra tuổi & cân nặng
        if ten_moi:
            # Tuổi phải > 0
            if tuoi is None:
                self.add_error('tuoi', "Vui lòng nhập tuổi.")
            elif tuoi <= 0:
                self.add_error('tuoi', "Tuổi phải lớn hơn 0.")

            # Cân nặng phải > 0
            if can_nang is None:
                self.add_error('can_nang', "Vui lòng nhập cân nặng.")
            elif can_nang <= 0:
                self.add_error('can_nang', "Cân nặng phải lớn hơn 0.")

        return cleaned_data


class LyDoHuyForm(forms.Form):
    ly_do_huy = forms.CharField(
        label="Lý do hủy lịch hẹn",
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Vui lòng nhập lý do hủy...'}),
        required=True
    )