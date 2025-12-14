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

    # 🔍 Nếu lịch hẹn đã có đánh giá → chỉ hiển thị form disabled
    da_danh_gia = hasattr(lich_hen, "danh_gia")
    danh_gia_instance = lich_hen.danh_gia if da_danh_gia else None

    if request.method == "POST":
        # Nếu đã đánh giá rồi → chặn
        if da_danh_gia:
            return redirect("tao_danh_gia", lich_hen_id=lich_hen.id)

        form = DanhGiaForm(request.POST)
        if form.is_valid():
            dg = form.save(commit=False)
            dg.lich_hen = lich_hen
            dg.nguoi_dung = request.user
            dg.save()
            return redirect("tao_danh_gia", lich_hen_id=lich_hen.id)
    else:
        form = DanhGiaForm(instance=danh_gia_instance)
    if request.user.is_staff:
        # Chặn admin chỉnh sửa các trường
        for field in form.fields.values():
            field.disabled = True

    return render(request, "KhieunaiDanhgia/danhgia.html", {
        "form": form,
        "lich_hen": lich_hen,
        "da_danh_gia": da_danh_gia,
    })


# 💗 Gửi KHIẾU NẠI
@login_required
def tao_khieu_nai(request, lich_hen_id):
    lich_hen = get_object_or_404(LichHen, id=lich_hen_id)
    kn = KhieuNai.objects.filter(lich_hen=lich_hen).first()
    da_khieu_nai = kn is not None

    # ---------------------------
    # 1) ĐÃ CÓ KHIẾU NẠI
    # ---------------------------
    if da_khieu_nai:

        is_admin = request.user.is_superuser
        is_responsible_staff = request.user.is_staff and request.user == kn.nhan_vien_phu_trach

        # --- POST cập nhật ---
        if request.method == "POST":

            # CHỈ Admin và nhân viên phụ trách mới được POST
            if not (is_admin or is_responsible_staff):
                return redirect("tao_khieu_nai", lich_hen_id=lich_hen.id)

            form = KhieuNaiForm(request.POST, request.FILES, instance=kn)

            if form.is_valid():
                updated = form.save(commit=False)

                # 🟣 Nhân viên chỉ được phép sửa 2 trường
                if is_responsible_staff and not is_admin:
                    original = KhieuNai.objects.get(id=kn.id)
                    updated.noi_dung = original.noi_dung
                    updated.yeu_cau = original.yeu_cau
                    updated.minh_chung = original.minh_chung

                # 🟣 Admin chỉ sửa nhân viên phụ trách → KHÔNG sửa các trường còn lại
                if is_admin:
                    original = KhieuNai.objects.get(id=kn.id)
                    updated.noi_dung = original.noi_dung
                    updated.yeu_cau = original.yeu_cau
                    updated.minh_chung = original.minh_chung
                    updated.phan_hoi = original.phan_hoi
                    updated.trang_thai = original.trang_thai

                updated.save()
                return redirect("tao_khieu_nai", lich_hen_id=lich_hen.id)

        # --- GET hiển thị form ---
        form = KhieuNaiForm(instance=kn)

        # Disable tất cả
        form.disable_all_fields()
        # 🟣 Nhân viên được phân công → chỉ mở 2 trường
        if is_responsible_staff:
            form.allow_staff_edit()
        if is_admin:
            form.lock_admin_fields()
        # Admin CHỈ sửa field “nhân viên phân công” → field này nằm ngoài form, ở admin site.

        return render(request, "KhieunaiDanhgia/khieunai.html", {
            "form": form,
            "lich_hen": lich_hen,
            "kn": kn,
            "da_khieu_nai": True,
        })


    # ---------------------------
    # 2) CHƯA CÓ KHIẾU NẠI → TẠO MỚI
    # ---------------------------
    if request.method == "POST":
        form = KhieuNaiForm(request.POST, request.FILES)
        if form.is_valid():
            new_kn = form.save(commit=False)
            new_kn.lich_hen = lich_hen
            new_kn.nguoi_gui = request.user
            new_kn.save()
            # === YOUR ADDED CODE — GỬI THÔNG BÁO ===
            # 🔔 Gửi thông báo cho nhân viên
            nhan_viens = User.objects.filter(is_staff=True)
            for nv in nhan_viens:
                ThongBao.objects.create(
                    tieu_de="📣 Có khiếu nại mới",
                    noi_dung=f"Khách hàng {request.user.username} đã gửi khiếu nại.",
                    loai="khieu_nai",
                    nguoi_gui=request.user,
                    nguoi_nhan=nv,
                    doi_tuong_id=new_kn.id,
                    link=f"/khieu-nai/chi-tiet/{new_kn.id}/"
                )

            # 🔔 Gửi thông báo cho khách hàng
            ThongBao.objects.create(
                tieu_de="📩 Bạn đã gửi một khiếu nại",
                noi_dung=f"Khiếu nại #{new_kn.id} của bạn đang được xử lý!",
                loai="khieu_nai",
                nguoi_gui=request.user,
                nguoi_nhan=request.user,
                doi_tuong_id=new_kn.id,
                link=f"/khieu-nai/chi-tiet/{new_kn.id}/"
            )

            lich_hen.refresh_from_db()
            return redirect("tao_khieu_nai", lich_hen_id=lich_hen.id)

    else:
        form = KhieuNaiForm()

    return render(request, "KhieunaiDanhgia/khieunai.html", {
        "form": form,
        "lich_hen": lich_hen,
        "kn": None,
        "da_khieu_nai": False,
    })

# -------------------------------
# 📝 Danh Sách Khiếu Nại
# -------------------------------
@login_required
def danh_sach_khieu_nai(request):
    if request.user.is_superuser:
        # Nếu là admin hoặc superuser, xem tất cả khiếu nại
        khieu_nai_list = KhieuNai.objects.all().order_by('-id')
    elif request.user.is_staff:
        khieu_nai_list = KhieuNai.objects.filter(
            nhan_vien_phu_trach=request.user
        ).order_by('-id')
    else:
        # Nếu là người dùng bình thường, chỉ xem khiếu nại của bản thân
        khieu_nai_list = KhieuNai.objects.filter(nguoi_gui=request.user).order_by('-id')

    return render(request, 'KhieunaiDanhgia/danhsachkhieunai.html', {
        'khieu_nai_list': khieu_nai_list,
    })

# 🟢 Chi tiết khiếu nại (view riêng của bạn)
@login_required
def chi_tiet_khieu_nai(request, id):
    khieunai = get_object_or_404(KhieuNai, id=id)

    # ADMIN → xem tất cả
    if request.user.is_superuser:
        pass

    # NHÂN VIÊN → chỉ xem khi được phân công
    elif request.user.is_staff:
        if khieunai.nhan_vien_phu_trach != request.user:
            return redirect('KhieunaiDanhgia:danh_sach_khieu_nai')

    # KHÁCH → chỉ xem khiếu nại mình gửi
    elif khieunai.nguoi_gui != request.user:
        return redirect('KhieunaiDanhgia:danh_sach_khieu_nai')


    # KHÁCH → chỉ xem khiếu nại mình gửi
    elif khieunai.nguoi_gui != request.user:
        return redirect('KhieunaiDanhgia:danh_sach_khieu_nai')

    return render(request, 'TB/chi_tiet_khieu_nai.html', {'khieunai': khieunai})
