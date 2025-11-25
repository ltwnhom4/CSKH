from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from LichHen.models import LichHen
from TB.models import ThongBao
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Tự động gửi thông báo nhắc lịch hẹn cho khách hàng có lịch trong 24 giờ tới"

    def handle(self, *args, **options):
        now = timezone.now()
        next_24h = now + timedelta(hours=24)

        # Tìm lịch hẹn sắp tới trong 24h chưa nhắc
        lich_hens = LichHen.objects.filter(
            thoi_gian__range=(now, next_24h),
            trang_thai='sap_toi',
            da_nhac=False
        ).select_related('khach_hang', 'thu_cung')

        admin_user = User.objects.filter(is_staff=True).first()

        count = 0
        for lich in lich_hens:
            khach_user = lich.khach_hang.user
            noi_dung = (
                f"Bạn có lịch hẹn cho bé {lich.thu_cung.ten_thucung} "
                f"vào {lich.thoi_gian.strftime('%H:%M %d/%m/%Y')}. "
                f"Hãy đến đúng giờ nhé 💖"
            )

            ThongBao.objects.create(
                tieu_de="⏰ Nhắc lịch hẹn Punky Spa",
                noi_dung=noi_dung,
                loai='lich_hen',
                nguoi_gui=admin_user,
                nguoi_nhan=khach_user,
                doi_tuong_id=lich.id,
                link=f"/lich-hen/chi-tiet/{lich.id}/"  # ✅ Thêm link xem chi tiết
            )

            lich.da_nhac = True
            lich.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Đã gửi {count} thông báo nhắc lịch."))
