from rest_framework import serializers
from .models import JournalEntry, AccountJournal, JournalImage

class JournalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalImage
        fields = ['id', 'image_url', 'created_at']

class JournalEntrySerializer(serializers.ModelSerializer):
    images = JournalImageSerializer(many=True, read_only=True)
    new_images = JournalImageSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = JournalEntry
        fields = [
            'id', 'journal', 'images', 'new_images', 'pnl', 'direction', 'textarea', 
            'entry_price', 'lot_size', 'stop_loss_price', 'target_price', 'result', 
            'pair', 'date', 'created_at'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        new_images_data = validated_data.pop('new_images', [])
        journal_entry = JournalEntry.objects.create(**validated_data, user=user)
        for image_data in new_images_data:
            JournalImage.objects.create(entry=journal_entry, **image_data)
        return journal_entry

    def update(self, instance, validated_data):
        new_images_data = validated_data.pop('new_images', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Optional: Replace existing images if new ones are provided
        if new_images_data:
            instance.images.all().delete()
            for image_data in new_images_data:
                JournalImage.objects.create(entry=instance, **image_data)

        return instance

class AccountJournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountJournal
        fields = '__all__'