from tortoise import migrations
from tortoise.migrations import operations as ops
from mirurain.enums.platform import Platform
from mirurain.enums.queue import QueueStatus
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0003_auto_20260519_1705')]

    initial = False

    operations = [
        ops.CreateModel(
            name='TrackedUser',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('platform', fields.CharEnumField(db_index=True, description='BLUESKY: bluesky\nMASTODON: mastodon\nNOSTR: nostr\nTUMBLR: tumblr\nTWITTER: twitter\nNONE: none', enum_type=Platform, max_length=32)),
                ('canonical', fields.TextField(unique=False)),
                ('display_as', fields.TextField(null=True, unique=False)),
                ('channel', fields.CharField(max_length=32)),
                ('server', fields.CharField(null=True, max_length=32)),
                ('created_at', fields.DatetimeField(db_index=True, auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'trackeduser', 'app': 'models', 'pk_attr': 'id', 'table_description': 'Tracked user record for outbound notifications.'},
            bases=['Model'],
        ),
        ops.AlterField(
            model_name='NotificationQueue',
            name='source',
            field=fields.CharEnumField(description='Notification source platform.', enum_type=Platform, max_length=32),
        ),
        ops.AlterField(
            model_name='NotificationQueue',
            name='status',
            field=fields.IntEnumField(description='Queued notification status.', enum_type=QueueStatus, generated=False),
        ),
    ]
