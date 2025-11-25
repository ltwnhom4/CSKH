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




# Kiểm tra quyền nhân viên
def la_nhan_vien(user):
    return user.is_staff or user.is_superuser

# 1️⃣ Khách hàng xem danh sách thông báo
@login_required
def danh_sach_thong_bao(request):
    loai = request.GET.get('loai', 'lich_hen')  # mặc định tab lịch hẹn
    thongbaos = ThongBao.objects.filter(nguoi_nhan=request.user, loai=loai).order_by('-ngay_tao')
    return render(request, 'TB/danh_sach_thong_bao.html', {'thongbaos': thongbaos, 'loai': loai})

# 2️⃣ Chi tiết thông báo
@login_required
def chi_tiet_thong_bao(request, id):
    # 👩‍💼 Nếu là nhân viên → có thể xem tất cả thông báo
    if request.user.is_staff:
        tb = get_object_or_404(ThongBao, id=id)
    else:
        # 👤 Nếu là khách hàng → chỉ được xem thông báo của chính họ
        tb = get_object_or_404(ThongBao, id=id, nguoi_nhan=request.user)

    # ✅ Đánh dấu đã đọc nếu chưa đọc
    if not tb.da_doc:
        tb.da_doc = True
        tb.save()

    # ✅ Hiển thị theo loại thông báo
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
            return render(request, 'TB/chi_tiet_thong_bao.html', {
                'tb': tb,
                'error': 'Lịch hẹn này không còn tồn tại.'
            })

    elif tb.loai == 'khuyen_mai':
        return render(request, 'TB/chi_tiet_khuyen_mai.html', {'tb': tb})

    elif tb.loai == 'he_thong':
        return render(request, 'TB/chi_tiet_he_thong.html', {'tb': tb})

    # fallback
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
            return redirect('danh_sach_thong_bao')
    else:
        form = ThongBaoForm()
    return render(request, 'TB/tao_thong_bao.html', {'form': form})
@login_required(login_url='/dangnhap/')
def trang_thong_bao(request):
    # 🎯 Lấy các loại thông báo khác như cũ
    thongbao_lichhen = ThongBao.objects.filter(
        nguoi_nhan=request.user, loai='lich_hen'
    ).order_by('-ngay_tao')

    thongbao_hethong = ThongBao.objects.filter(
        nguoi_nhan=request.user, loai='he_thong'
    ).order_by('-ngay_tao')

    # 🎁 Riêng khuyến mãi: lọc trùng bằng Python
    if request.user.is_staff:
        # Nếu là nhân viên: xem tất cả
        thongbaos_all = ThongBao.objects.filter(loai='khuyen_mai').order_by('-ngay_tao')
    else:
        # Nếu là khách hàng: chỉ xem khuyến mãi gửi cho mình
        thongbaos_all = ThongBao.objects.filter(
            nguoi_nhan=request.user, loai='khuyen_mai'
        ).order_by('-ngay_tao')

    thongbao_khuyenmai = []
    seen = set()

    for tb in thongbaos_all:
        key = (tb.tieu_de.strip(), tb.noi_dung.strip())
        if key not in seen:
            thongbao_khuyenmai.append(tb)
            seen.add(key)

    context = {
        'thongbao_lichhen': thongbao_lichhen,
        'thongbao_khuyenmai': thongbao_khuyenmai,
        'thongbao_hethong': thongbao_hethong,
    }

    return render(request, 'TB/trang_thong_bao.html', context)

@login_required
def danh_dau_da_doc_tat_ca(request):
    ThongBao.objects.filter(nguoi_nhan=request.user, da_doc=False).update(da_doc=True)
    return redirect('danh_sach_thong_bao')

@login_required
def xem_thong_bao(request, tb_id):
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
        return redirect('chi_tiet_lich_hen', id=tb.doi_tuong_id)
    elif tb.loai == 'khuyen_mai' and tb.doi_tuong_id:
        return redirect('chi_tiet_khuyen_mai', id=tb.doi_tuong_id)
    elif tb.loai == 'he_thong':
        return render(request, 'TB/chi_tiet_thong_bao.html', {'tb': tb})

    # ✅ Nếu không có loại cụ thể → quay lại danh sách
    return redirect('TB:trang_thong_bao')
@login_required
@user_passes_test(la_nhan_vien)
def tao_khuyen_mai(request):
    if request.method == 'POST':
        form = KhuyenMaiForm(request.POST)
        if form.is_valid():
            tieu_de = form.cleaned_data['tieu_de']
            noi_dung = form.cleaned_data['noi_dung']
            nguoi_gui = request.user

            # ✅ Gửi thông báo đến tất cả khách hàng (is_staff=False)
            khach_hangs = User.objects.filter(is_staff=False)
            so_nguoi = 0

            for kh in khach_hangs:
                ThongBao.objects.create(
                    tieu_de=tieu_de,
                    noi_dung=noi_dung,
                    loai='khuyen_mai',
                    nguoi_gui=nguoi_gui,
                    nguoi_nhan=kh
                )
                so_nguoi += 1

            messages.success(request, f"🎉 Đã gửi khuyến mãi đến {so_nguoi} khách hàng.")
            return redirect('TB:trang_thong_bao')
    else:
        form = KhuyenMaiForm()

    return render(request, 'TB/tao_khuyen_mai.html', {'form': form})
@login_required
def danh_sach_khuyen_mai(request):
    # Lấy mỗi tiêu đề khuyến mãi một bản ghi mới nhất
    latest_ids = (
        ThongBao.objects.filter(loai='khuyen_mai')
        .values('tieu_de')
        .annotate(max_id=Max('id'))
        .values_list('max_id', flat=True)
    )

    thongbao_khuyenmai = ThongBao.objects.filter(id__in=latest_ids).order_by('-ngay_tao')

    return render(request, 'TB/trang_khuyen_mai.html', {
        'thongbao_khuyenmai': thongbao_khuyenmai
    })