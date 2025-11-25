from django.shortcuts import render, get_object_or_404
from .models import DichVu

# 🌸 Hiển thị danh sách tất cả dịch vụ + Tìm kiếm theo tên
def danh_sach_dich_vu(request):
    query = request.GET.get('q')  # Lấy từ khóa tìm kiếm từ URL (?q=...)
    if query:
        # Lọc dịch vụ có tên chứa từ khóa (không phân biệt hoa thường)
        dich_vus = DichVu.objects.filter(ten_dich_vu__icontains=query).order_by('id')
    else:
        # Nếu không có từ khóa => hiển thị tất cả
        dich_vus = DichVu.objects.all().order_by('id')

    return render(request, 'DV/danhsachdichvu.html', {
        'dich_vu': dich_vus,
        'query': query,  # để hiển thị lại từ khóa nếu cần
    })


# 🌸 Hiển thị chi tiết từng dịch vụ
def chi_tiet_dich_vu(request, id):
    dich_vu = get_object_or_404(DichVu, pk=id)
    return render(request, 'DV/chitietdichvu.html', {
        'dich_vu': dich_vu
    })
