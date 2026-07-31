from django.contrib import admin

from .models import GraphDomain, KnowledgeGraph


@admin.register(GraphDomain)
class GraphDomainAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_by", "created_at")
    search_fields = ("name",)


@admin.register(KnowledgeGraph)
class KnowledgeGraphAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "domain", "type", "status", "owner", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("status", "type", "domain")
