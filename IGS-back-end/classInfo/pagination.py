# pagination.py
from rest_framework.pagination import PageNumberPagination

class ClassStudentPagination(PageNumberPagination):
    # 前端传"page"对应currentPage，"page_size"对应pageSize
    page_query_param = 'page'  # 页码参数名（前端currentPage）
    page_size_query_param = 'page_size'  # 每页条数参数名（前端pageSize）
    page_size = 10  # 默认每页10条（匹配前端默认值）
    max_page_size = 100  # 最大每页条数（防止恶意请求）