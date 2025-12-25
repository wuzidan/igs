# notification/api/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification
from .serializers import NotificationSerializer, NotificationMarkReadSerializer
from .permissions import IsNotificationRecipient

class TeacherNotificationViewSet(viewsets.ModelViewSet):
    """
    教师通知视图集：
    - 列表：获取当前教师的所有通知（支持筛选已读/类型）
    - 详情：查看单个通知的完整信息
    - 更新：标记通知为已读（仅更新is_read字段）
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsNotificationRecipient]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_read', 'type']  # 支持筛选：已读/未读（is_read=true/false）、类型（type=exercise）
    ordering_fields = ['created_at']  # 支持按时间排序
    ordering = ['-created_at']  # 默认最新通知在前

    def get_queryset(self):
        """仅返回当前教师作为接收者的通知"""
        return Notification.objects.filter(recipient=self.request.user)

    def get_serializer_class(self):
        """根据动作选择序列化器：标记已读用专用序列化器"""
        if self.action == 'partial_update' or self.action == 'update':
            return NotificationMarkReadSerializer
        return NotificationSerializer

    def partial_update(self, request, *args, **kwargs):
        """重写部分更新：仅允许标记为已读"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={'is_read': True}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "通知已标记为已读"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # （可选）批量标记所有未读通知为已读
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """批量标记当前教师的所有未读通知为已读"""
        unread_notifications = self.get_queryset().filter(is_read=False)
        unread_notifications.update(is_read=True)
        return Response({
            "message": f"成功标记{unread_notifications.count()}条未读通知为已读"
        })