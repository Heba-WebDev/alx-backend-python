from django_filters import rest_framework as filters  # type: ignore
from .models import Message, User

class MessageFilter(filters.FilterSet):
    sender = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='sender',
        label='Sender',
    )

    sent_at__gte = filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        label='Sent at (greater than or equal)',
    )

    sent_at__lte = filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        label='Sent at (less than or equal)',
    )

    class Meta:
        model = Message
        fields = ['sender', 'sent_at__gte', 'sent_at__lte']