from django import forms
from .models import DanhGia, KhieuNai

class DanhGiaForm(forms.ModelForm):
    class Meta:
        model = DanhGia
        fields = ['diem', 'nhan_xet']
        labels = {
            'diem': 'Mức độ hài lòng',
            'nhan_xet': 'Nhận xét',
        }
        widgets = {
            'diem': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'nhan_xet': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Chia sẻ cảm nhận của bạn...'}),
        }


class KhieuNaiForm(forms.ModelForm):
    class Meta:
        model = KhieuNai
        fields = ['noi_dung', 'minh_chung', 'yeu_cau']
        labels = {
            'noi_dung': 'Nội dung khiếu nại',
            'minh_chung': 'Hình ảnh (hoặc video) minh chứng',
            'yeu_cau': 'Yêu cầu/mong muốn',
        }
        widgets = {
            'noi_dung': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Vui lòng nêu rõ lý do'}),
            'yeu_cau': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Bạn muốn được giải quyết như thế nào?'}),
        }
