from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DangKyForm, KhachHangForm, NhanVienForm
from .models import KhachHang, NhanVien, TichDiem, LichSuTichDiem
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

def dangky(request):
    if request.method == 'POST':  #Nếu người dùng gửi form (POST)
        form = DangKyForm(request.POST)  #Lấy dữ liệu từ form đăng ký
        if form.is_valid():
            user = form.save()  # Tạo tài khoản user
            user.is_active=True
            # Gán vào nhóm Khách hàng
            khach_group, _ = Group.objects.get_or_create(name='Khách hàng')
            user.groups.add(khach_group)
            # 👉 Tự động tạo bản ghi KhachHang
            KhachHang.objects.create(user=user, email=user.email,)
            messages.success(request, "Đăng ký thành công! Hãy đăng nhập.")
            return redirect('dangnhap')
        else:
            messages.error(request, "Đăng ký thất bại, vui lòng kiểm tra lại.")
    else:
        form = DangKyForm()
    return render(request, 'TK/dang_ky.html', {'form': form})

def dangnhap(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu!")

    return render(request, 'TK/dang_nhap.html')


def quenmatkhau(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Mật khẩu đã được cập nhật thành công! Vui lòng đăng nhập lại.")
            return redirect('dangnhap')
        except User.DoesNotExist:
            messages.error(request, "Không tìm thấy tài khoản với email này.")

    return render(request, 'TK/quenmatkhau.html')

def dangxuat(request):
    logout(request)
    return redirect('home')

@login_required
def thongtintaikhoan(request):
    khach= KhachHang.objects.get(user=request.user)
    if not khach.ho_ten:
        khach.ho_ten = request.user.username
        khach.save()
    if request.method == 'POST':
        form = KhachHangForm(request.POST, instance=khach)
        if form.is_valid():
            kh = form.save(commit=False)
            # Nếu người dùng sửa email → cập nhật cả User.email luôn
            request.user.email = kh.email
            request.user.save()
            kh.save()
            messages.success(request, "Thông tin đã được cập nhật thành công!")
            return redirect('thongtintaikhoan')
    else:
        form = KhachHangForm(instance=khach)

    return render(request, 'TK/thongtintaikhoan.html', {
        'form': form,
        'user': request.user,
    })

@login_required
def xoa_tai_khoan(request):
    if request.method == 'POST':
        ly_do = request.POST.get('ly_do')
        user = request.user
        user.is_active = False
        user.save()
        messages.success(request, "Tài khoản của bạn đã được khóa! Vui lòng liên hệ quản trị viên ")
        return redirect('dangxuat')  # đăng xuất sau khi khóa

    return render(request, 'TK/xoa_tai_khoan.html', {'user': request.user})

@login_required
def thong_tin_nhanvien(request):
   nhanvien = NhanVien.objects.get(user=request.user)
   if request.method == 'POST':
       form = NhanVienForm(request.POST, instance=nhanvien)
       if form.is_valid():
           nv = form.save(commit=False)
           # Nếu người dùng sửa email → cập nhật cả User.email luôn
           request.user.email = nv.email
           request.user.save()
           nv.save()
           messages.success(request, "Cập nhật thông tin thành công!")
           return redirect('thong_tin_nhanvien')
   else:
       form = NhanVienForm(instance=nhanvien)


   return render(request, 'TK/thong_tin_nhanvien.html', {'form': form})

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def quan_ly_tich_diem(request):
    query = request.GET.get('sdt', '')
    khach_hang_list = KhachHang.objects.filter(lichhen__isnull=False).distinct().order_by('-ngay_tham_gia')
    # Nếu có nhập số điện thoại thì lọc ra
    if query:
        khach_hang_list = khach_hang_list.filter(so_dien_thoai__icontains=query)

    # Cập nhật điểm khi nhấn nút
    if request.method == "POST":
        sdt = request.POST.get("sdt")
        diem_moi = request.POST.get("diem_moi")
        try:
            kh = KhachHang.objects.get(so_dien_thoai=sdt)
            tich_diem, created = TichDiem.objects.get_or_create(khach_hang=kh)
            diem_moi = int(diem_moi)

            # 🔹 Cộng điểm
            tich_diem.tong_diem += diem_moi
            tich_diem.cap_nhat_cap_bac()
            tich_diem.save()

            # 🔹 Ghi lại lịch sử tích điểm
            LichSuTichDiem.objects.create(
                khach_hang=kh,
                so_diem=diem_moi,
                noi_dung=f"Cộng {diem_moi} điểm bởi {request.user.username}"
            )

            messages.success(request, f"Cập nhật {diem_moi} điểm cho {kh.ho_ten} thành công!")

        except Exception as e:
            messages.error(request, f"❌ Lỗi: {e}")

        return redirect("quan_ly_tich_diem")

    return render(request, "TK/quan_ly_tich_diem.html", {
        "khach_hang_list": khach_hang_list,
        "query": query
    })

@login_required
def xem_tich_diem(request):
    try:
        # Lấy thông tin khách hàng
        khach = KhachHang.objects.get(user=request.user)
        tich_diem, created = TichDiem.objects.get_or_create(khach_hang=khach)

        # 🔹 Lấy lịch sử giao dịch điểm (mới nhất lên đầu)
        lich_su = LichSuTichDiem.objects.filter(
            khach_hang=khach
        ).order_by('-ngay_cap_nhat')

    except KhachHang.DoesNotExist:
        khach = None
        tich_diem = None
        lich_su = None

    return render(request, 'TK/xem_tich_diem.html', {
        'khach': khach,
        'tich_diem': tich_diem,
        'lich_su': lich_su
    })
