from rest_framework import serializers

from users.models import User, Payments


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'phone',
            'city',
            'avatar'
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(source='payments_set', many=True, read_only=True)

    def create(self, validated_data):
        payment = validated_data.pop('payments_set', [])
        user = User.objects.create(**validated_data)

        for pay in payment:
            Payments.objects.create(user=user, **pay)

        return user

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'phone',
            'city',
            'avatar',
            'payments',
        )