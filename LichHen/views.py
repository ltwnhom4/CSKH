from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.messages import get_messages

from .models import LichHen, DV_LichHen
from .forms import LichHenForm, LyDoHuyForm
from TK.models import KhachHang, ThuCung
from TB.models import ThongBao
from django.contrib.auth.models import User
from django.urls import reverse


# 🧾 Hiển thị lịch hẹn sắp tới
@login_required(login_url='/dangnhap/')
def lich_hen_sap_toi(request):
    khach_hang = KhachHang.objects.filter(user=request.user).first()
    if not khach_hang:
        messages.error(request, "Tài khoản này chưa có thông tin khách hàng.")
        return render(request, 'lichhen/lich_hen_sap_toi.html', {'lich_hens': []})

    # ✅ Chuyển lịch đã qua sang “hoàn thành”
    hien_tai = timezone.now()
    lich_qua_ngay = LichHen.objects.filter(khach_hang=khach_hang, trang_thai='sap_toi', thoi_gian__lt=hien_tai)
    from TK.models import TichDiem, LichSuTichDiem
    for lich in lich_qua_ngay:
        lich.trang_thai = 'hoan_thanh'
        lich.save()
        # ✅ Lấy tổng tiền (nếu có)
        tong_tien = getattr(lich, 'tong_tien', 0) or 0

        if tong_tien > 0:
            # Mỗi 20.000đ = 1 điểm
            diem_cong = int(tong_tien / 20000)

            # ✅ Lấy hoặc tạo bản ghi tích điểm
            tich_diem, _ = TichDiem.objects.get_or_create(khach_hang=khach_hang)
            tich_diem.tong_diem += diem_cong
            tich_diem.cap_nhat_cap_bac()
            tich_diem.save()

            # ✅ Ghi lịch sử (đúng field là `noi_dung`)
            LichSuTichDiem.objects.create(
                khach_hang=khach_hang,
                so_diem=diem_cong,
                noi_dung=f"Hoàn thành lịch hẹn cho bé {lich.thu_cung.ten_thucung} ({tong_tien:,}đ)."
            )
    lich_hens = LichHen.objects.filter(
        khach_hang_id=khach_hang.id,
        trang_thai='sap_toi'
    ).select_related('thu_cung', 'khach_hang','nhan_vien').order_by('thoi_gian')

    return render(request, 'lichhen/lich_hen_sap_toi.html', {'lich_hens': lich_hens})


# ➕ Thêm lịch hẹn mới
@login_required(login_url='/dangnhap/')
def tao_lich_hen(request):
    # ❌ Xóa sạch tất cả messages khi load trang GET
    if request.method == "GET":
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # duyệt qua để clear
    user = request.user

    try:
        khach_hang = KhachHang.objects.get(user=user)
    except KhachHang.DoesNotExist:
        messages.error(request, "Vui lòng đăng nhập bằng tài khoản khách hàng hợp lệ.")
        return redirect('dangnhap')

    if request.method == 'POST':
        form = LichHenForm(request.POST, khach_hang=khach_hang)
        if form.is_valid():
            thu_cung = form.cleaned_data.get('thu_cung')
            ten_moi = form.cleaned_data.get('ten_thu_cung_moi')
            thoi_gian = form.cleaned_data.get('thoi_gian')
            if thoi_gian < timezone.now():
                messages.error(request, "Không thể đặt lịch ở thời gian trong quá khứ.")
                return render(request, 'lichhen/tao_lich_hen.html', {'form': form})

            # 🐶 Nếu thêm thú cưng mới
            if not thu_cung and ten_moi:
                thu_cung = ThuCung.objects.create(
                    khach_hang=khach_hang,
                    ten_thucung=ten_moi,
                    loai=form.cleaned_data.get('loai'),
                    tuoi=form.cleaned_data.get('tuoi'),
                    can_nang=form.cleaned_data.get('can_nang')
                )

            if not thu_cung:
                messages.error(request, "Vui lòng chọn hoặc thêm thú cưng hợp lệ.")
                return render(request, 'lichhen/tao_lich_hen.html', {'form': form})

            # ✅ Lưu lịch hẹn
            lich_hen = form.save(commit=False)
            lich_hen.khach_hang = khach_hang
            lich_hen.thu_cung = thu_cung
            lich_hen.trang_thai = 'sap_toi'
            lich_hen.so_dien_thoai = form.cleaned_data.get('so_dien_thoai')
            lich_hen.save()

            # ✅ Thêm nhiều dịch vụ
            dich_vu_list = form.cleaned_data.get('dich_vu', [])
            tong_tien = 0
            for dv in dich_vu_list:
                DV_LichHen.objects.create(lich_hen=lich_hen, dich_vu=dv)
                # ✅ Lưu dịch vụ và tính tổng tiền
                if hasattr(dv, 'gia'):
                    tong_tien += dv.gia

            lich_hen.tong_tien = tong_tien
            lich_hen.save(update_fields=['tong_tien'])

            # 📨 Gửi thông báo
            ten_dv = ", ".join([dv.ten_dich_vu for dv in dich_vu_list]) or "(Không có dịch vụ)"
            ghi_chu = form.cleaned_data.get('ghi_chu', '').strip() or "(Không có ghi chú)"
            ThongBao.objects.create(
                tieu_de="Đặt lịch thành công 🎉",
                noi_dung=f"Bạn đã đặt lịch cho bé {thu_cung.ten_thucung} vào {timezone.localtime(lich_hen.thoi_gian).strftime('%H:%M %d/%m/%Y')}.",
                loai='lich_hen',
                dich_vu=ten_dv,
                ghi_chu=ghi_chu,
                nguoi_gui=request.user,
                nguoi_nhan=request.user,
                doi_tuong_id=lich_hen.id,
                link=f"/lich-hen/chi-tiet/{lich_hen.id}/"
            )

            # 📨 Gửi cho admin
            admin_user = User.objects.filter(is_staff=True).first()
            if admin_user:
                ThongBao.objects.create(
                    tieu_de="Khách hàng mới đặt lịch",
                    noi_dung=f"Khách hàng {request.user.username} vừa đặt lịch cho bé {thu_cung.ten_thucung} ({ten_dv}) lúc {timezone.localtime(lich_hen.thoi_gian).strftime('%H:%M %d/%m/%Y')}.",
                    loai='lich_hen',
                    nguoi_gui=request.user,
                    nguoi_nhan=admin_user,
                    doi_tuong_id=lich_hen.id,
                    link=reverse("chi_tiet_lich_hen", args=[lich_hen.id])

                )

            return redirect('lich_hen_sap_toi')
        else:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin hợp lệ.")
    else:
        so_dien_thoai_mac_dinh = getattr(khach_hang, 'so_dien_thoai', '')
        form = LichHenForm(khach_hang=khach_hang, initial={'so_dien_thoai': so_dien_thoai_mac_dinh})

    return render(request, 'lichhen/tao_lich_hen.html', {'form': form})


# 📘 API trả về thông tin thú cưng
def thong_tin_thu_cung(request, pk):
    try:
        thu_cung = ThuCung.objects.get(pk=pk)
        data = {'loai': thu_cung.loai, 'tuoi': thu_cung.tuoi, 'can_nang': thu_cung.can_nang}
        return JsonResponse(data)
    except ThuCung.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy thú cưng.'}, status=404)

# 🗑️ Hủy lịch hẹn
@login_required(login_url='/dangnhap/')
def xoa_lich_hen(request, id):
    lich_hen = get_object_or_404(LichHen, id=id)
    form = LyDoHuyForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        ly_do = form.cleaned_data['ly_do_huy']
        lich_hen.trang_thai = 'huy'
        lich_hen.ly_do_huy = ly_do
        lich_hen.save()

        admin_user = User.objects.filter(is_staff=True).first()

        if request.user.is_staff:
            ThongBao.objects.create(
                tieu_de="🚫 Lịch hẹn đã bị nhân viên hủy",
                noi_dung=f"Lịch hẹn của bé {lich_hen.thu_cung.ten_thucung} đã bị nhân viên hủy. Lý do: {ly_do}.",
                loai='lich_hen',
                nguoi_gui=request.user,
                nguoi_nhan=lich_hen.khach_hang.user,
                doi_tuong_id=lich_hen.id,
                link=f"/lich-hen/chi-tiet/{lich_hen.id}/"
            )
        else:
            ThongBao.objects.create(
                tieu_de="❌ Xác nhận hủy lịch hẹn",
                noi_dung=f"Bạn đã hủy lịch hẹn cho bé {lich_hen.thu_cung.ten_thucung} vào {timezone.localtime(lich_hen.thoi_gian).strftime('%H:%M %d/%m/%Y')}.",
                loai='lich_hen',
                nguoi_gui=request.user,
                nguoi_nhan=request.user,
                doi_tuong_id=lich_hen.id,
                link=f"/lich-hen/chi-tiet/{lich_hen.id}/"
            )
            if admin_user:
                ThongBao.objects.create(
                    tieu_de="🚫 Khách hàng đã hủy lịch hẹn",
                    noi_dung=f"Khách hàng {lich_hen.khach_hang.user.username} đã hủy lịch của bé {lich_hen.thu_cung.ten_thucung}.",
                    loai='lich_hen',
                    nguoi_gui=request.user,
                    nguoi_nhan=admin_user,
                    doi_tuong_id=lich_hen.id,
                    link=f"/lich-hen/chi-tiet/{lich_hen.id}/"
                )

        messages.success(request, "Lịch hẹn đã được hủy thành công!")
        return redirect('lich_da_huy')

    return render(request, 'lichhen/xoa_lich_hen.html', {'lich_hen': lich_hen, 'form': form})


# 📋 Danh sách lịch đã hủy
@login_required(login_url='/dangnhap/')
def lich_da_huy(request):
    khach_hang = KhachHang.objects.filter(user=request.user).first()
    lich_hens = LichHen.objects.filter(
        khach_hang=khach_hang,
        trang_thai='huy'
    ).select_related('thu_cung', 'khach_hang', 'nhan_vien') \
        .prefetch_related('dv_lichhen_set__dich_vu') \
        .order_by('-thoi_gian')

    return render(request, 'lichhen/lich_da_huy.html', {'lich_hens': lich_hens})


# 📘 Xem lịch sử lịch hẹn (hoàn thành)
@login_required(login_url='/dangnhap/')
def lich_su_lich_hen(request):
    khach_hang = KhachHang.objects.filter(user=request.user).first()
    lich_hens = LichHen.objects.filter(
        khach_hang=khach_hang,
        trang_thai='hoan_thanh'
    ).select_related('thu_cung', 'khach_hang', 'nhan_vien') \
        .prefetch_related('dv_lichhen_set__dich_vu') \
        .order_by('-thoi_gian')
    return render(request, 'lichhen/lich_su_lich_hen.html', {'lich_hens': lich_hens})


# 📄 Chi tiết lịch hẹn
@login_required(login_url='/dangnhap/')
def chi_tiet_lich_hen(request, id):
    lich_hen = get_object_or_404(LichHen, id=id)

    # ⭐ ADMIN / NHÂN VIÊN → xem được tất cả lịch hẹn
    if request.user.is_staff:
        dich_vu_list = DV_LichHen.objects.filter(lich_hen=lich_hen)
        return render(request, 'TB/chi_tiet_lich_hen.html', {
            'lich_hen': lich_hen,
            'dich_vu_list': dich_vu_list
        })

    # ⭐ KHÁCH HÀNG → chỉ xem lịch của mình
    kh = KhachHang.objects.filter(user=request.user).first()
    if not kh or lich_hen.khach_hang != kh:
        return redirect('TB:trang_thong_bao')

    dich_vu_list = DV_LichHen.objects.filter(lich_hen=lich_hen)

    return render(request, 'TB/chi_tiet_lich_hen.html', {
        'lich_hen': lich_hen,
        'dich_vu_list': dich_vu_list
    })