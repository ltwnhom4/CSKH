from django import forms
from .models import DanhGia, KhieuNai


# ============================================
#  FORM ĐÁNH GIÁ DỊCH VỤ
# ============================================
class DanhGiaForm(forms.ModelForm):
    class Meta:
        model = DanhGia
        fields = ['diem', 'nhan_xet']
        labels = {
            'diem': 'Mức độ hài lòng',
            'nhan_xet': 'Nhận xét của bạn',
        }
        widgets = {
            'diem': forms.RadioSelect(
                choices=[(i, f'{i} ⭐') for i in range(1, 6)]
            ),
            'nhan_xet': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Chia sẻ cảm nhận của bạn...'
            }),
        }

    # Nếu muốn disable tất cả field (ví dụ cho admin/staff)
    def disable_all_fields(self):
        for field in self.fields.values():
            field.disabled = True


# ============================================
#  FORM KHIẾU NẠI (CHỈ KHÁCH HÀNG)
# ============================================
class KhieuNaiForm(forms.ModelForm):
    class Meta:
        model = KhieuNai
        fields = ['noi_dung', 'minh_chung', 'yeu_cau']
        labels = {
            'noi_dung': 'Nội dung khiếu nại',
            'minh_chung': 'Minh chứng (ảnh hoặc video)',
            'yeu_cau': 'Yêu cầu / mong muốn',
        }
        widgets = {
            'noi_dung': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Vui lòng mô tả chi tiết vấn đề bạn gặp phải...'
            }),
            'yeu_cau': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Bạn mong muốn được hỗ trợ ra sao?'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['minh_chung'].widget.attrs.update({
            'accept': 'image/*,video/*'
        })
