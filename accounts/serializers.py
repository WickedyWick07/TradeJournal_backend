from rest_framework import serializers
from .models import TradingAccount

class TradingAccountSerializers(serializers.ModelSerializer):
    class Meta: 
        model = TradingAccount
        # Explicitly define the fields to expose, excluding sensitive ones
        fields = ['id', 'account_number', 'account_balance', 'broker', 'created_at', 'updated_at', 'initial_balance']
        read_only_fields = [ 'id']  # Example of making some fields read-only

    def create(self, validated_data):
        # You can use this method to ensure 'user' is handled safely when creating
        user = self.context['request'].user
        validated_data.pop('user', None)
        return TradingAccount.objects.create(user=user, **validated_data)
