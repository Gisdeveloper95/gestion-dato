# Generated migration for DirectorioPreoperacion and ArchivoPreoperacion
# Estas tablas almacenan la indexación de pre-operación EXCLUYENDO 07_insu

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('preoperacion', '0002_passwordresettoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectorioPreoperacion',
            fields=[
                ('cod_directorio', models.AutoField(primary_key=True, serialize=False)),
                ('nom_directorio', models.CharField(max_length=255)),
                ('ruta_directorio', models.TextField(unique=True)),
                ('nivel', models.IntegerField(default=0, help_text='Nivel de profundidad: 0=raíz de 01_preo')),
                ('fecha_creacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(blank=True, null=True)),
                ('propietario', models.CharField(blank=True, max_length=255, null=True)),
                ('fecha_indexacion', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(
                    blank=True,
                    db_column='parent_id',
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subdirectorios',
                    to='preoperacion.directoriopreoperacion'
                )),
                ('cod_mpio', models.ForeignKey(
                    db_column='cod_mpio',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='directorios_preoperacion',
                    to='preoperacion.municipios'
                )),
            ],
            options={
                'verbose_name': 'Directorio Pre-Operación',
                'verbose_name_plural': 'Directorios Pre-Operación',
                'db_table': 'directorios_preoperacion',
                'ordering': ['nivel', 'nom_directorio'],
            },
        ),
        migrations.CreateModel(
            name='ArchivoPreoperacion',
            fields=[
                ('cod_archivo', models.AutoField(primary_key=True, serialize=False)),
                ('nom_archivo', models.CharField(max_length=500)),
                ('ruta_archivo', models.TextField(unique=True)),
                ('extension', models.CharField(blank=True, max_length=50, null=True)),
                ('tamano_bytes', models.BigIntegerField(blank=True, null=True)),
                ('propietario', models.CharField(blank=True, max_length=255, null=True)),
                ('hash_contenido', models.CharField(blank=True, max_length=255, null=True)),
                ('fecha_creacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_modificacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_indexacion', models.DateTimeField(auto_now_add=True)),
                ('cod_directorio', models.ForeignKey(
                    db_column='cod_directorio',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='archivos',
                    to='preoperacion.directoriopreoperacion'
                )),
            ],
            options={
                'verbose_name': 'Archivo Pre-Operación',
                'verbose_name_plural': 'Archivos Pre-Operación',
                'db_table': 'archivos_preoperacion',
                'ordering': ['nom_archivo'],
            },
        ),
        # Índices para DirectorioPreoperacion
        migrations.AddIndex(
            model_name='directoriopreoperacion',
            index=models.Index(fields=['cod_mpio'], name='dir_preo_mpio_idx'),
        ),
        migrations.AddIndex(
            model_name='directoriopreoperacion',
            index=models.Index(fields=['parent'], name='dir_preo_parent_idx'),
        ),
        migrations.AddIndex(
            model_name='directoriopreoperacion',
            index=models.Index(fields=['nivel'], name='dir_preo_nivel_idx'),
        ),
        # Índices para ArchivoPreoperacion
        migrations.AddIndex(
            model_name='archivopreoperacion',
            index=models.Index(fields=['cod_directorio'], name='arch_preo_dir_idx'),
        ),
        migrations.AddIndex(
            model_name='archivopreoperacion',
            index=models.Index(fields=['extension'], name='arch_preo_ext_idx'),
        ),
        migrations.AddIndex(
            model_name='archivopreoperacion',
            index=models.Index(fields=['propietario'], name='arch_preo_prop_idx'),
        ),
    ]
