# Generated by Django 2.1.7 on 2019-03-11 03:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommentInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=256)),
                ('create_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='EmotionInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=256)),
                ('create_time', models.DateTimeField()),
                ('address', models.CharField(max_length=50)),
                ('tools', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='LikeInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emotion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qqinfo.EmotionInfo')),
            ],
        ),
        migrations.CreateModel(
            name='QQInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qq', models.CharField(max_length=11, unique=True)),
                ('nick', models.CharField(max_length=20)),
                ('qqimg', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='likeinfo',
            name='from_qq',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_fromqq', to='qqinfo.QQInfo'),
        ),
        migrations.AddField(
            model_name='likeinfo',
            name='to_qq',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_toqq', to='qqinfo.QQInfo'),
        ),
        migrations.AddField(
            model_name='emotioninfo',
            name='publisher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qqinfo.QQInfo'),
        ),
        migrations.AddField(
            model_name='commentinfo',
            name='emotion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qqinfo.EmotionInfo'),
        ),
        migrations.AddField(
            model_name='commentinfo',
            name='from_qq',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_fromqq', to='qqinfo.QQInfo'),
        ),
        migrations.AddField(
            model_name='commentinfo',
            name='to_qq',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_toqq', to='qqinfo.QQInfo'),
        ),
    ]
