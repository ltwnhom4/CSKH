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
#  FORM KHIẾU NẠI DỊCH VỤ
# ============================================
class KhieuNaiForm(forms.ModelForm):
    class Meta:
        model = KhieuNai
        fields = ['noi_dung', 'minh_chung', 'yeu_cau', 'trang_thai', 'phan_hoi']
        labels = {
            'noi_dung': 'Nội dung khiếu nại',
            'minh_chung': 'Minh chứng (ảnh hoặc video)',
            'yeu_cau': 'Yêu cầu / mong muốn',
            'nhan_vien_phu_trach': 'Nhân viên phụ trách',
            'trang_thai': 'Trạng thái xử lý',
            'phan_hoi': 'Phản hồi từ nhân viên',
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
            'phan_hoi': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Nhân viên sẽ ghi phản hồi tại đây...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # File upload: chấp nhận ảnh và video
        self.fields['minh_chung'].widget.attrs.update({
            'accept': 'image/*,video/*'
        })

    # Hàm hỗ trợ khóa toàn bộ field (để dùng trong view)
    def disable_all_fields(self):
        for field in self.fields.values():
            field.disabled = True

    # Hàm hỗ trợ mở khóa đúng 2 trường cho nhân viên
    def allow_staff_edit(self):
        self.fields['trang_thai'].disabled = False
        self.fields['phan_hoi'].disabled = False

    # Hàm hỗ trợ admin CHỈ xem (không sửa)
    def allow_admin_assign_staff(self):
        # Khóa hết
        self.disable_all_fields()
        # Chỉ cho admin sửa nhân viên phụ trách
        self.fields['nhan_vien_phu_trach'].disabled = False
