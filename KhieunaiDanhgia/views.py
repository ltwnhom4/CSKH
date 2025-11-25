from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from LichHen.models import LichHen
from .forms import DanhGiaForm, KhieuNaiForm
from .models import KhieuNai


# 🩵 Gửi ĐÁNH GIÁ
@login_required
def tao_danh_gia(request, lich_hen_id):
    lich_hen = get_object_or_404(LichHen, id=lich_hen_id)
    if request.method == 'POST':
        form = DanhGiaForm(request.POST)
        if form.is_valid():
            danh_gia = form.save(commit=False)
            danh_gia.lich_hen = lich_hen
            danh_gia.nguoi_dung = request.user
            danh_gia.save()
            messages.success(request, "🎉 Gửi đánh giá thành công!")
            return redirect('lich_su_lich_hen')
    else:
        form = DanhGiaForm()
    return render(request, 'KhieunaiDanhgia/danhgia.html', {'form': form, 'lich_hen': lich_hen})


# 💗 Gửi KHIẾU NẠI
@login_required
def tao_khieu_nai(request, lich_hen_id):
    lich_hen = get_object_or_404(LichHen, id=lich_hen_id)
    if request.method == 'POST':
        form = KhieuNaiForm(request.POST, request.FILES)
        if form.is_valid():
            khieu_nai = form.save(commit=False)
            khieu_nai.lich_hen = lich_hen
            khieu_nai.nguoi_gui = request.user
            khieu_nai.save()
            # ✅ Thông báo thành công
            messages.success(request, "🎉 Gửi khiếu nại thành công! Chúng tôi sẽ phản hồi sớm nhất.")
            # 🔁 Chuyển hướng đến trang lịch sử khiếu nại
            return redirect('danh_sach_khieu_nai')
    else:
        form = KhieuNaiForm()
    return render(request, 'KhieunaiDanhgia/khieunai.html', {'form': form, 'lich_hen': lich_hen})


# 🧾 DANH SÁCH KHIẾU NẠI
@login_required
def danh_sach_khieu_nai(request):
    # Nếu là admin hoặc nhân viên → xem toàn bộ
    if request.user.is_staff or request.user.is_superuser:
        khieu_nai_list = KhieuNai.objects.all().order_by('-id')
    else:
        # Nếu là khách hàng → chỉ xem của chính họ
        khieu_nai_list = KhieuNai.objects.filter(nguoi_gui=request.user).order_by('-id')

    return render(request, 'KhieunaiDanhgia/danhsachkhieunai.html', {'khieu_nai_list': khieu_nai_list})
