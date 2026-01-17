from rest_framework import serializers

from .models import GraphDomain, KnowledgeGraph


class GraphDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphDomain
        fields = ["id", "name"]


class TagsField(serializers.Field):
    def to_representation(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [x.strip() for x in value.split(",") if x.strip()]
        return []

    def to_internal_value(self, data):
        if data is None:
            return []
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()]
        if isinstance(data, str):
            return [x.strip() for x in data.split(",") if x.strip()]
        raise serializers.ValidationError("tags必须是字符串或数组")


class KnowledgeGraphListSerializer(serializers.ModelSerializer):
    domainId = serializers.IntegerField(source="domain_id", read_only=True)
    createTime = serializers.DateTimeField(source="created_at", read_only=True)
    updateTime = serializers.DateTimeField(source="updated_at", read_only=True)
    creator = serializers.SerializerMethodField(read_only=True)
    nodesCount = serializers.SerializerMethodField(read_only=True)
    relationshipsCount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = KnowledgeGraph
        fields = [
            "id",
            "name",
            "domainId",
            "type",
            "status",
            "nodesCount",
            "relationshipsCount",
            "creator",
            "createTime",
            "updateTime",
        ]

    def get_creator(self, obj):
        owner = getattr(obj, "owner", None)
        if owner is None:
            return ""
        return getattr(owner, "first_name", "") or getattr(owner, "name", "") or getattr(owner, "username", "") or ""

    def get_nodesCount(self, obj):
        content = getattr(obj, "content", None) or {}
        nodes = content.get("nodes") if isinstance(content, dict) else None
        return len(nodes) if isinstance(nodes, list) else 0

    def get_relationshipsCount(self, obj):
        content = getattr(obj, "content", None) or {}
        rels = content.get("relationships") if isinstance(content, dict) else None
        return len(rels) if isinstance(rels, list) else 0


class KnowledgeGraphDetailSerializer(serializers.ModelSerializer):
    domainId = serializers.IntegerField(source="domain_id", read_only=True)
    tags = TagsField(required=False)
    nodes = serializers.SerializerMethodField(read_only=True)
    relationships = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = KnowledgeGraph
        fields = [
            "id",
            "name",
            "domainId",
            "type",
            "status",
            "description",
            "tags",
            "nodes",
            "relationships",
        ]

    def get_nodes(self, obj):
        content = getattr(obj, "content", None) or {}
        nodes = content.get("nodes") if isinstance(content, dict) else None
        return nodes if isinstance(nodes, list) else []

    def get_relationships(self, obj):
        content = getattr(obj, "content", None) or {}
        rels = content.get("relationships") if isinstance(content, dict) else None
        return rels if isinstance(rels, list) else []


class KnowledgeGraphWriteSerializer(serializers.ModelSerializer):
    domainId = serializers.IntegerField(write_only=True)
    tags = TagsField(required=False)
    nodes = serializers.ListField(child=serializers.DictField(), required=False)
    relationships = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = KnowledgeGraph
        fields = [
            "name",
            "domainId",
            "type",
            "status",
            "description",
            "tags",
            "nodes",
            "relationships",
        ]

    def validate_domainId(self, value):
        if not GraphDomain.objects.filter(id=value).exists():
            raise serializers.ValidationError("domainId不存在")
        return value

    def create(self, validated_data):
        domain_id = validated_data.pop("domainId")
        nodes = validated_data.pop("nodes", [])
        relationships = validated_data.pop("relationships", [])

        validated_data["domain_id"] = domain_id
        validated_data["content"] = {
            "nodes": nodes if isinstance(nodes, list) else [],
            "relationships": relationships if isinstance(relationships, list) else [],
        }
        return super().create(validated_data)

    def update(self, instance, validated_data):
        domain_id = validated_data.pop("domainId", None)
        nodes = validated_data.pop("nodes", None)
        relationships = validated_data.pop("relationships", None)

        if domain_id is not None:
            instance.domain_id = domain_id

        content = getattr(instance, "content", None)
        if not isinstance(content, dict):
            content = {}

        if nodes is not None:
            content["nodes"] = nodes if isinstance(nodes, list) else []
        if relationships is not None:
            content["relationships"] = relationships if isinstance(relationships, list) else []

        instance.content = content

        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags is not None:
            instance.tags = tags

        instance.save()
        return instance
