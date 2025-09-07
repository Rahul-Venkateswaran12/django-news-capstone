from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model with journalist validation."""
    class Meta:
        model = Article
        fields = ['id', 'title', 'content',
                  'publisher', 'journalist', 'approved',
                  'date']
        read_only_fields = ['id', 'date', 'approved']

    def create(self, validated_data):
        """Creates an article, restricted to journalists."""
        journalist = self.context['request'].user
        if journalist.role != 'journalist':
            raise serializers.ValidationError(
                "Only journalists can create articles")
        validated_data['journalist'] = journalist
        return super().create(validated_data)


class ApproveArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'approved']
        read_only_fields = ['id']
