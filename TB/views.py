from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import ThongBao
from .forms import ThongBaoForm
from .forms import KhuyenMaiForm
from LichHen.models import LichHen, DV_LichHen
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Max
from TK.models import KhachHang


# Kiểm tra quyền nhân viên
def la_nhan_vien(user):
    return user.is_staff or user.is_superuser

# 2️⃣ Chi tiết thông báo
@login_required
def chi_tiet_thong_bao(request, id):
    # 🔒 Lấy thông báo đúng người nhận
    tb = get_object_or_404(
        ThongBao,
        id=id,
        nguoi_nhan=request.user
    )

    # ✅ ĐÁNH DẤU ĐÃ ĐỌC (SỬA LỖI CHÍNH Ở ĐÂY)
    if not tb.da_doc:
        tb.da_doc = True
        tb.save(update_fields=['da_doc'])

    # 🔥 1) THÔNG BÁO LỊCH HẸN
    if tb.loai == 'lich_hen' and tb.doi_tuong_id:
        try:
            lich_hen = LichHen.objects.get(id=tb.doi_tuong_id)
            dich_vu_list = DV_LichHen.objects.filter(lich_hen=lich_hen)
            return render(request, 'TB/chi_tiet_lich_hen.html', {
                'tb': tb,
                'lich_hen': lich_hen,
                'dich_vu_list': dich_vu_list
            })
        except LichHen.DoesNotExist:
            messages.error(request, "Lịch hẹn này không còn tồn tại.")
            return redirect('TB:trang_thong_bao')

    # 🔥 2) THÔNG BÁO KHIẾU NẠI
    if tb.loai == 'khieu_nai' and tb.doi_tuong_id:
        try:
            from KhieunaiDanhgia.models import KhieuNai
            kn = KhieuNai.objects.get(id=tb.doi_tuong_id)
            return render(request, 'TB/chi_tiet_khieu_nai.html', {
                'tb': tb,
                'khieunai': kn
            })
        except KhieuNai.DoesNotExist:
            messages.error(request, "Khiếu nại này không còn tồn tại.")
            return redirect('TB:trang_thong_bao')

    # 🔥 3) THÔNG BÁO KHUYẾN MÃI
    if tb.loai == 'khuyen_mai':
        return render(request, 'TB/chi_tiet_khuyen_mai.html', {
            'tb': tb
        })

    # 🔁 Fallback
    return render(request, 'TB/chi_tiet_thong_bao.html', {'tb': tb})

# 3️⃣ Nhân viên tạo thông báo
@login_required
@user_passes_test(la_nhan_vien)
def tao_thong_bao(request):
    if request.method == 'POST':
        form = ThongBaoForm(request.POST)
        if form.is_valid():
            tb = form.save(commit=False)
            tb.nguoi_gui = request.user
            tb.save()
            return redirect('trang_thong_bao')
    else:
        form = ThongBaoForm()
    return render(request, 'TB/tao_thong_bao.html', {'form': form})
@login_required(login_url='/dangnhap/')
def trang_thong_bao(request):
    thongbao_lichhen = ThongBao.objects.filter(
        nguoi_nhan=request.user,
        loai='lich_hen'
    ).order_by('-ngay_tao')

    thongbao_khieunai = ThongBao.objects.filter(
        nguoi_nhan=request.user,
        loai='khieu_nai'
    ).order_by('-ngay_tao')

    thongbao_khuyenmai = ThongBao.objects.filter(
        loai='khuyen_mai'
    ).order_by('-ngay_tao')

    if not request.user.is_staff:
        thongbao_khuyenmai = thongbao_khuyenmai.filter(nguoi_nhan=request.user)

    context = {
        'thongbao_lichhen': thongbao_lichhen,
        'thongbao_khieunai': thongbao_khieunai,
        'thongbao_khuyenmai': thongbao_khuyenmai,
    }

    return render(request, 'TB/trang_thong_bao.html', context)

@login_required
def danh_dau_da_doc_tat_ca(request):
    ThongBao.objects.filter(nguoi_nhan=request.user, da_doc=False).update(da_doc=True)
    return redirect('trang_thong_bao')

@login_required
def xem_thong_bao(request, tb_id):
    if request.user.is_staff or request.user.is_superuser:
        tb = get_object_or_404(ThongBao, id=tb_id)
    else:
        tb = get_object_or_404(ThongBao, id=tb_id, nguoi_nhan=request.user)

    # ✅ Đánh dấu đã đọc
    if not tb.da_doc:
        tb.da_doc = True
        tb.save()

    # ✅ Nếu có link → chuyển trực tiếp
    if tb.link:
        return redirect(tb.link)

    # ✅ Nếu không có link → fallback theo loại
    if tb.loai == 'lich_hen' and tb.doi_tuong_id:
        return redirect('TB:chi_tiet_lich_hen', id=tb.id)
    elif tb.loai == 'khuyen_mai':
        return redirect('TB:chi_tiet_khuyen_mai', id=tb.id)

    elif tb.loai == "khieu_nai" and tb.doi_tuong_id:
        return redirect("chi_tiet_khieu_nai", id=tb.id)
    # ✅ Nếu không có loại cụ thể → quay lại danh sách
    return redirect('TB:trang_thong_bao')

@login_required
@user_passes_test(la_nhan_vien)
def tao_khuyen_mai(request):
    if request.method == 'POST':
        form = KhuyenMaiForm(request.POST, request.FILES)   #  PHẢI CÓ request.FILES
        if form.is_valid():

            tieu_de = form.cleaned_data['tieu_de']
            noi_dung = form.cleaned_data['noi_dung']
            hinh_anh = form.cleaned_data.get('hinh_anh', None)
            nguoi_gui = request.user

            #  Lấy TẤT CẢ khách hàng thực tế
            khach_hangs = KhachHang.objects.all()

            so_nguoi = 0

            for kh in khach_hangs:
                ThongBao.objects.create(
                    tieu_de=tieu_de,
                    noi_dung=noi_dung,
                    loai='khuyen_mai',
                    hinh_anh=hinh_anh,             # 🔥 LƯU HÌNH ẢNH
                    nguoi_gui=nguoi_gui,
                    nguoi_nhan=kh.user             # 🔥 ĐÚNG NGƯỜI NHẬN
                )
                so_nguoi += 1

            messages.success(request, f"🎉 Đã gửi khuyến mãi đến {so_nguoi} khách hàng.")
            return redirect('TB:danh_sach_khuyen_mai')            # 🔥 redirect đúng trang KM
    else:
        form = KhuyenMaiForm()

    return render(request, 'TB/tao_khuyen_mai.html', {'form': form})
@login_required
def danh_sach_khuyen_mai(request):
    # Lấy mỗi tiêu đề khuyến mãi một bản ghi mới nhất
    latest_ids = (
        ThongBao.objects.filter(loai='khuyen_mai')
        .values('tieu_de', 'noi_dung')
        .annotate(max_id=Max('id'))
        .values_list('max_id', flat=True)
    )

    thongbao_khuyenmai = ThongBao.objects.filter(id__in=latest_ids).order_by('-ngay_tao')

    return render(request, 'TB/trang_khuyen_mai.html', {
        'thongbao_khuyenmai': thongbao_khuyenmai
    })

@login_required
@user_passes_test(la_nhan_vien)
def xoa_khuyen_mai(request,km_id):
    km = get_object_or_404(ThongBao, id=km_id, loai='khuyen_mai')

    # Xóa 1 bản ghi duy nhất
    km.delete()

    messages.success(request, "🗑️ Đã xóa khuyến mãi.")
    return redirect('TB:danh_sach_khuyen_mai')
@login_required
def chi_tiet_khuyen_mai(request, id):
    tb = get_object_or_404(ThongBao, id=id, loai='khuyen_mai')
    return render(request, 'TB/chi_tiet_khuyen_mai.html', {
        'tb': tb
    })



