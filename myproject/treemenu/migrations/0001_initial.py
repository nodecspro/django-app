# Generated by Django 5.2.1 on 2025-05-14 13:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Display Name')),
                ('menu_name', models.CharField(db_index=True, help_text="A unique name for the menu this item belongs to (e.g., 'main_menu').", max_length=50, verbose_name='Menu Name')),
                ('url', models.CharField(blank=True, help_text='Example: /about/ or https://example.com. Leave blank if using Named URL.', max_length=200, verbose_name='Explicit URL')),
                ('named_url', models.CharField(blank=True, help_text="Example: 'home_page'. Leave blank if using Explicit URL.", max_length=100, verbose_name='Named URL')),
                ('order', models.IntegerField(default=0, help_text='Order in which to display items at the same level.', verbose_name='Order')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='treemenu.menuitem', verbose_name='Parent Item')),
            ],
            options={
                'verbose_name': 'Menu Item',
                'verbose_name_plural': 'Menu Items',
                'ordering': ['menu_name', 'parent__id', 'order', 'name'],
            },
        ),
    ]
