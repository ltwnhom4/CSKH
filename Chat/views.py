from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json, uuid
from django.http import HttpResponse
from .models import TinNhan
from TK.models import KhachHang, NhanVien
from django.contrib.auth.decorators import login_required


# ======================================================
# 📌 Tạo phiên chat cho khách chưa đăng nhập
# ======================================================
def get_or_create_session_chat(request):
    if "phien_chat" not in request.session:
        request.session["phien_chat"] = f"PHIEN-{uuid.uuid4().hex[:12]}"
    return request.session["phien_chat"]


# ======================================================
# 📌 HÀM BOT — TRẢ VỀ HTML + ĐƯỢC LƯU VÀO DB
# ======================================================
def bot_auto_reply(text_raw):
    text = text_raw.strip().lower()

    # ----- 1. MENU -----
    if text == "báo giá dịch vụ":
        return """
        <div class='options service-menu'>
            <div style='font-size:15px;margin-bottom:6px;'>Bạn muốn xem báo giá của dịch vụ nào? 🌸</div>
            <button onclick="sendOption('Tắm rửa')">🛁 Tắm rửa</button>
            <button onclick="sendOption('Cắt tỉa lông')">✂️ Cắt tỉa lông</button>
            <button onclick="sendOption('Nhuộm lông')">🌺 Nhuộm lông</button>
            <button onclick="sendOption('Tư vấn sức khỏe')">🩺 Tư vấn sức khỏe</button>
            <button onclick="sendOption('Tiêm phòng')">💉 Tiêm phòng</button>
            <button onclick="sendOption('Triệt sản')">🐾 Triệt sản</button>
        </div>
        """

    # ----- 2. Báo giá -----
    if "tắm" in text:
        return "🐱 <b>Tắm rửa</b> có giá khoảng 150,000 VND<br>👉 <a href='/dichvu/6/'>Xem chi tiết</a>"

    if "cắt" in text or "tỉa" in text or "tia" in text:
        return "✂️ <b>Cắt tỉa lông</b> khoảng 200,000 VND<br>👉 <a href='/dichvu/2/'>Xem chi tiết</a>"

    if "nhuộm" in text:
        return "🌸 <b>Nhuộm lông</b> khoảng 300,000 VND<br>👉 <a href='/dichvu/4/'>Xem chi tiết</a>"

    if "tư vấn sức khỏe" in text or "sức khỏe" in text:
        return "🩺 <b>Tư vấn sức khỏe</b> khoảng 100,000 VND<br>👉 <a href='/dichvu/5/'>Xem chi tiết</a>"

    if "tiêm" in text:
        return "💉 <b>Tiêm phòng</b> khoảng 250,000 VND<br>👉 <a href='/dichvu/3/'>Xem chi tiết</a>"

    if "triệt" in text:
        return "🐾 <b>Triệt sản</b> khoảng 700,000 VND<br>👉 <a href='/dichvu/1/'>Xem chi tiết</a>"

    # ----- 3. FAQ -----
    if text == "hỏi đáp nhanh (faq)":
        return """
        💬 Bạn có thể hỏi tôi:<br><br>
        🐶 “Punky Spa có nhận bé ngoài giờ không?”<br>
        🛁 “Sau khi tắm có sấy khô & chải lông không?”<br>
        🌿 “Có mang dầu gội riêng không?”<br><br>
        Hoặc chọn <b>Tư vấn trực tiếp</b> để gặp nhân viên 💕
        """

    if "ngoài giờ" in text:
        return "⏰ Spa mở 09h–21h. Ngoài giờ cần đặt trước nhé 💗"

    if "sấy" in text or "chải" in text:
        return "🛁 Sau khi tắm, bé sẽ được <b>sấy khô</b> & <b>chải lông mềm mượt</b> 💗"

    if "dầu gội" in text:
        return "🌿 Bạn có thể mang dầu gội riêng cho bé nha!"

    # ----- 4. Tư vấn -----
    if text == "tư vấn trực tiếp":
        return "📞 Gọi <b>1900 6750</b> để được hỗ trợ nhanh nhất 💕"

    # ----- 5. Default -----
    return ""   # để gui_tin_nhan xử lý



# ======================================================
# 📌 API TRẢ VỀ SỐ TIN NHẮN CHƯA ĐỌC
# ======================================================

from django.views.decorators.http import require_GET

@require_GET
def get_unread_count(request):
    user = request.user

    # KH chưa login → dùng phiên chat
    if not user.is_authenticated:
        phien = request.session.get("phien_chat")
        if not phien:
            return JsonResponse({"count": 0})

        unread = TinNhan.objects.filter(
            phien_chat=phien,
            nguoi_gui__in=["NV", "AD"],
            da_doc=False
        ).count()
        return JsonResponse({"count": unread})

    # KH đã login
    if hasattr(user, "khachhang"):
        kh = user.khachhang
        unread = TinNhan.objects.filter(
            id_khachhang=kh,
            nguoi_gui__in=["NV", "AD"],
            da_doc=False
        ).count()
        return JsonResponse({"count": unread})

    return JsonResponse({"count": 0})

def admin_unread_customers(request):
    # Chỉ cho admin + nhân viên
    if not request.user.is_authenticated:
        return JsonResponse({"count": 0})

    if not request.user.is_staff and not hasattr(request.user, "nhanvien"):
        return JsonResponse({"count": 0})

    # Lấy danh sách khách hàng có tài khoản & có tin chưa đọc
    unread_customers = TinNhan.objects.filter(
        nguoi_gui="KH",
        da_doc=False,
        id_khachhang__isnull=False  # CHỈ LẤY KHÁCH CÓ TÀI KHOẢN
    ).values_list("id_khachhang", flat=True).distinct()

    return JsonResponse({"count": len(unread_customers)})


# ======================================================
# 📌 API GỬI TIN NHẮN — LƯU CẢ MENU
# ======================================================
@csrf_exempt
def gui_tin_nhan(request):
    data = json.loads(request.body)
    text = data.get("text", "").strip()
    is_quick = data.get("quick", False)  # ⭐ phân biệt gợi ý và tự gõ
    if not text:
        return JsonResponse({"error": "Nội dung trống"}, status=400)
    user = request.user

    # ============================================================
    # 1️⃣ KHÁCH CHƯA ĐĂNG NHẬP
    # ============================================================
    if not user.is_authenticated:
        phien = get_or_create_session_chat(request)

        # LƯU TIN KHÁCH GỬI
        TinNhan.objects.create(
            phien_chat=phien,
            nguoi_gui="KH",
            noi_dung=text
        )

        # ⭐ TRƯỜNG HỢP 1: BẤM NÚT GỢI Ý (quick = true)
        if is_quick:
            reply = bot_auto_reply(text)
            if reply:
                TinNhan.objects.create(
                    phien_chat=phien,
                    nguoi_gui="HT",
                    noi_dung=reply
                )
            return JsonResponse({"reply": reply})

        # ⭐ TRƯỜNG HỢP 2: TỰ GÕ (quick = false)
        # → chỉ trả lời 1 lần duy nhất
        da_gui_default = TinNhan.objects.filter(
            phien_chat=phien,
            nguoi_gui="HT",
            noi_dung="💗 Cảm ơn bạn đã liên lạc, bạn vui lòng đăng nhập và nhắn tin để được hỗ trợ nhé!"
        ).exists()

        if not da_gui_default:
            TinNhan.objects.create(
                phien_chat=phien,
                nguoi_gui="HT",
                noi_dung="💗 Cảm ơn bạn đã liên lạc, bạn vui lòng đăng nhập và nhắn tin để được hỗ trợ nhé!"
            )
            return JsonResponse({
                "reply": "💗 Cảm ơn bạn đã liên lạc, bạn vui lòng đăng nhập và nhắn tin để được hỗ trợ nhé!"
            })

        return JsonResponse({"reply": ""})
    # ===============================================
    # 2. KHÁCH ĐĂNG NHẬP
    # ===============================================
    if hasattr(user, "khachhang"):
        kh = user.khachhang

        TinNhan.objects.create(
            id_khachhang=kh,
            nguoi_gui="KH",
            noi_dung=text
        )
        reply = bot_auto_reply(text)

        if reply != "":
            TinNhan.objects.create(
                id_khachhang=kh,
                nguoi_gui="HT",
                noi_dung=reply
            )
            return JsonResponse({"reply": reply})

        # ⭐ DEFAULT — 1 LẦN DUY NHẤT
        da_gui_default = TinNhan.objects.filter(
            id_khachhang=kh,
            nguoi_gui="HT",
            noi_dung="💗 Cảm ơn bạn đã liên hệ, bạn vui lòng chờ nhân viên hỗ trợ nhé"
        ).exists()

        if not da_gui_default:
            TinNhan.objects.create(
                id_khachhang=kh,
                nguoi_gui="HT",
                noi_dung="💗 Cảm ơn bạn đã liên hệ, bạn vui lòng chờ nhân viên hỗ trợ nhé"
            )
            return JsonResponse({"reply": "💗 Cảm ơn bạn đã liên hệ, bạn vui lòng chờ nhân viên hỗ trợ nhé"})

        return JsonResponse({"reply": ""})

    # ===============================================
    # 3. NHÂN VIÊN / ADMIN TRẢ LỜI
    # ===============================================
    mode = data.get("mode")
    target = data.get("to")

    if user.is_superuser:
        sender = "AD"
    elif hasattr(user, "nhanvien"):
        sender = "NV"
    else:
        sender = "AD"

    nv = user.nhanvien if hasattr(user, "nhanvien") else None

    if mode == "khach":
        TinNhan.objects.create(
            id_khachhang_id=target,
            nguoi_gui=sender,
            noi_dung=text,
            id_nhanvien=nv,
            id_admin=user if user.is_superuser else None
        )
        return JsonResponse({"reply": "Đã gửi"})

    if mode == "phien":
        TinNhan.objects.create(
            phien_chat=target,
            nguoi_gui=sender,
            noi_dung=text,
            id_nhanvien=nv,
            id_admin=user if user.is_superuser else None
        )
        return JsonResponse({"reply": "Đã gửi"})

    return JsonResponse({"error": "Thiếu mode hoặc target"}, status=400)


# ======================================================
# 📌 VIEW HIỂN THỊ CHAT
# ======================================================
def chatbox_view(request):

    # =========================================================
    # 1. Nhân viên / admin KHÔNG được vào chatbox khách
    # =========================================================
    if hasattr(request.user, "nhanvien") or request.user.is_staff:
        return redirect("danh_sach_khach")
    user = request.user

    # =========================================================
    # 2. KHÁCH CHƯA ĐĂNG NHẬP
    # =========================================================
    if not user.is_authenticated:

        # lấy phiên chat
        phien = get_or_create_session_chat(request)

        # Lấy toàn bộ tin nhắn
        messages = TinNhan.objects.filter(
            phien_chat=phien
        ).order_by("thoi_gian_gui")

        # ĐÁNH DẤU TIN NV/AD ĐÃ ĐỌC
        TinNhan.objects.filter(
            phien_chat=phien,
            nguoi_gui__in=["NV", "AD"],
            da_doc=False
        ).update(da_doc=True)

        return render(request, "Chat/chatbox.html", {
            "messages": messages
        })

    # =========================================================
    # 3. KHÁCH ĐĂNG NHẬP
    # =========================================================
    if hasattr(user, "khachhang"):

        kh = user.khachhang

        messages = TinNhan.objects.filter(
            id_khachhang=kh
        ).order_by("thoi_gian_gui")

        # ĐÁNH DẤU TIN NV/AD ĐÃ ĐỌC
        TinNhan.objects.filter(
            id_khachhang=kh,
            nguoi_gui__in=["NV", "AD"],
            da_doc=False
        ).update(da_doc=True)

        return render(request, "Chat/chatbox.html", {
            "messages": messages
        })

    # =========================================================
    # 4. Trường hợp khác (không xác định quyền)
    # =========================================================
    return HttpResponse("Không xác định quyền")



# ======================================================
# ⭐ DANH SÁCH KHÁCH ĐÃ CHAT (NHÂN VIÊN / ADMIN)
# ======================================================
from django.db.models import Max

from django.db.models import Max, Count, Q

def danh_sach_khach(request):
    if not request.user.is_authenticated:
        return redirect("dangnhap")

    if not hasattr(request.user, "nhanvien") and not request.user.is_staff:
        return redirect("chatbox")

    khach_list = (
        KhachHang.objects
        .filter(id__in=TinNhan.objects.values("id_khachhang"))
        .annotate(
            last_time=Max("tinnhan__thoi_gian_gui"),
            unread=Count(
                "tinnhan",
                filter=Q(tinnhan__nguoi_gui="KH", tinnhan__da_doc=False)
            )
        )
        .distinct()
        .order_by( "-last_time")
    )

    return render(request, "Chat/danh_sach_khach.html", {
        "khach_list": khach_list
    })


def chat_admin(request, khach_id):
    if not request.user.is_authenticated:
        return redirect("dangnhap")

    if not hasattr(request.user, "nhanvien") and not request.user.is_staff:
        return redirect("chatbox")

    try:
        kh = KhachHang.objects.get(id=khach_id)
    except KhachHang.DoesNotExist:
        return HttpResponse("Không tìm thấy khách hàng")

    messages = TinNhan.objects.filter(
        id_khachhang=kh
    ).order_by("thoi_gian_gui")

    # Đánh dấu tin KH gửi là đã đọc
    TinNhan.objects.filter(
        id_khachhang=kh,
        nguoi_gui="KH",
        da_doc=False
    ).update(da_doc=True)
    target_name = kh.ho_ten or kh.user.username or "Khách hàng"
    return render(request, "Chat/chat_admin.html", {
        "target": target_name,
        "messages": messages,
        "mode": "khach",
        "send_to": kh.id
    })

