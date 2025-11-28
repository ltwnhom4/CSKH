from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from LichHen.models import LichHen
from .forms import DanhGiaForm, KhieuNaiForm
from .models import KhieuNai
from TB.models import ThongBao
from django.contrib.auth.models import User
from TK.models import KhachHang


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
            kn = form.save(commit=False)
            kn.lich_hen = lich_hen
            kn.nguoi_gui = request.user
            kn.trang_thai = "Chờ xử lý"
            kn.save()

            # 🔔 Gửi thông báo cho tất cả nhân viên
            nhan_viens = User.objects.filter(is_staff=True)

            for nv in nhan_viens:
                ThongBao.objects.create(
                    tieu_de="📣 Có khiếu nại mới",
                    noi_dung=f"Khách hàng {request.user.username} đã gửi khiếu nại.",
                    loai="khieu_nai",
                    nguoi_gui=request.user,
                    nguoi_nhan=nv,
                    doi_tuong_id=kn.id,
                    link=f"/khieu-nai/chi-tiet/{kn.id}/"
                )
            # 🔔 Gửi thông báo cho chính khách hàng sau khi gửi khiếu nại
            ThongBao.objects.create(
                tieu_de="📩 Bạn đã gửi một khiếu nại",
                noi_dung=f"Khiếu nại của bạn đang được xử lý. Mã khiếu nại: #{kn.id}",
                loai="khieu_nai",
                nguoi_gui=request.user,
                nguoi_nhan=request.user,  # gửi lại cho chính KH
                doi_tuong_id=kn.id,
                link=f"/khieu-nai/chi-tiet/{kn.id}/"
            )

            messages.success(request, "🎉 Gửi khiếu nại thành công!")
            return redirect('KhieunaiDanhgia:danh_sach_khieu_nai')

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
@login_required
def gui_khieu_nai(request):
    if request.method == 'POST':
        form = KhieuNaiForm(request.POST, request.FILES)
        if form.is_valid():
            kn = form.save(commit=False)
            kn.nguoi_gui = request.user
            kn.save()

            # 🔥 Gửi thông báo đến tất cả nhân viên
            nhan_viens = User.objects.filter(is_staff=True)

            for nv in nhan_viens:
                ThongBao.objects.create(
                    tieu_de="Khiếu nại mới",
                    noi_dung=f"Khách hàng {request.user.username} vừa gửi một khiếu nại mới.",
                    loai="khieu_nai",
                    nguoi_gui=request.user,
                    nguoi_nhan=nv,
                    doi_tuong_id=kn.id,
                    link=f"/khieu-nai/{kn.id}/chi-tiet/"
                )

            messages.success(request, "Bạn đã gửi khiếu nại thành công!")
            return redirect("TB:trang_thong_bao")

    else:
        form = KhieuNaiForm()

    return render(request, "KhieunaiDanhgia/gui_khieu_nai.html", {"form": form})

@login_required(login_url='/dangnhap/')
@user_passes_test(lambda u: u.is_staff)
def xu_ly_khieu_nai(request, id):
    kn = get_object_or_404(KhieuNai, id=id)

    kn.trang_thai = 'Đã phản hồi'
    kn.nhan_vien_phu_trach = request.user
    kn.save()

    # 🔔 Gửi thông báo CHO KHÁCH HÀNG
    ThongBao.objects.create(
        tieu_de="📬 Khiếu nại của bạn đã được phản hồi",
        noi_dung=f"Khiếu nại #{kn.id} của bạn đã được nhân viên {request.user.username} phản hồi.",
        loai="khieu_nai",
        nguoi_gui=request.user,
        nguoi_nhan=kn.nguoi_gui,
        doi_tuong_id=kn.id,
        link=f"/khieu-nai/chi-tiet/{kn.id}/"
    )

    messages.success(request, "Đã phản hồi khiếu nại.")
    return redirect('KhieunaiDanhgia:danh_sach_khieu_nai')

@login_required(login_url='/dangnhap/')
def chi_tiet_khieu_nai(request, id):
    khieunai = get_object_or_404(KhieuNai, id=id)

    # ⭐ Admin / nhân viên xem tất cả
    if request.user.is_staff:
        return render(request, 'TB/chi_tiet_khieu_nai.html', {
            'khieunai': khieunai
        })

    # ⭐ Khách hàng chỉ xem khiếu nại của chính họ
    if khieunai.nguoi_gui != request.user:
        messages.error(request, "Bạn không được xem khiếu nại của người khác.")
        return redirect('TB:trang_thong_bao')

    # ⭐ Hiển thị chi tiết khiếu nại cho khách hàng
    return render(request, 'TB/chi_tiet_khieu_nai.html', {
        'khieunai': khieunai
    })
