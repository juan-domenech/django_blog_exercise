# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-11 10:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_stripe_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='subscription_end',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
