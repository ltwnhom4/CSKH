from .models import ThongBao

def thong_bao_moi(request):
    if request.user.is_authenticated:
        thong_baos = ThongBao.objects.filter(
            nguoi_nhan=request.user
        ).order_by('-ngay_tao')[:5]
        so_thong_bao_chua_doc = ThongBao.objects.filter(
            nguoi_nhan=request.user, da_doc=False
        ).count()
        return {
            'thong_baos_moi': thong_baos,
            'so_thong_bao_chua_doc': so_thong_bao_chua_doc
        }
    return {}
