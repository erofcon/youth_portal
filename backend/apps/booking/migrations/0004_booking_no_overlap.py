from django.db import migrations
from django.contrib.postgres.operations import CreateExtension
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.db.models import F, Q


class Migration(migrations.Migration):
    dependencies = [
        ('booking', '0002_booking_applicant'),
    ]

    operations = [
        CreateExtension('btree_gist'),
        migrations.AddConstraint(
            model_name='booking',
            constraint=ExclusionConstraint(
                name='booking_no_overlap_if_approved',
                expressions=[
                    (F('room'), RangeOperators.EQUAL),
                    ('time_slot', RangeOperators.OVERLAPS),
                ],
                condition=Q(status='APPROVED'),
                index_type='GIST',
            ),
        ),
    ]
