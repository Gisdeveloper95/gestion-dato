# Generated manually for Operacion module
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalificacionInfoOperacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concepto', models.CharField(max_length=255, verbose_name='Concepto')),
                ('valor', models.DecimalField(
                    decimal_places=2,
                    max_digits=3,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(1)
                    ],
                    verbose_name='Valor'
                )),
            ],
            options={
                'verbose_name': 'Calificacion Info Operacion',
                'verbose_name_plural': 'Calificaciones Info Operacion',
                'db_table': 'calificacion_info_operacion',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='EvaluacionArchivosOperacion',
            fields=[
                ('id_evaluacion', models.AutoField(primary_key=True, serialize=False)),
                ('id_archivo', models.IntegerField(db_index=True)),
                ('nombre_archivo', models.CharField(max_length=255)),
                ('ruta_completa', models.TextField()),
                ('evaluacion_archivo', models.IntegerField(blank=True, default=1, null=True)),
                ('estado_archivo', models.CharField(
                    choices=[
                        ('PENDIENTE', 'Pendiente'),
                        ('EVALUADO', 'Evaluado'),
                        ('APROBADO', 'Aprobado')
                    ],
                    default='PENDIENTE',
                    max_length=50
                )),
                ('evaluado', models.BooleanField(default=False)),
                ('aprobado', models.BooleanField(default=False)),
                ('observaciones_evaluacion', models.TextField(blank=True, null=True)),
                ('usuario_evaluacion', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha_disposicion', models.DateTimeField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('lote_calificacion_masiva', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha_calificacion_masiva', models.DateTimeField(blank=True, null=True)),
                ('evaluacion_archivo_anterior', models.IntegerField(blank=True, null=True)),
                ('usuario_calificacion_masiva', models.CharField(blank=True, max_length=100, null=True)),
                ('usuario_windows', models.CharField(blank=True, max_length=100, null=True)),
                ('peso_memoria', models.CharField(blank=True, max_length=100, null=True)),
                ('observacion_original', models.TextField(blank=True, null=True)),
                ('hash_contenido', models.CharField(blank=True, max_length=256, null=True)),
                ('cod_dir_operacion', models.ForeignKey(
                    db_column='cod_dir_operacion',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='evaluaciones_operacion',
                    to='app.directoriosoperacion'
                )),
            ],
            options={
                'verbose_name': 'Evaluacion Archivo Operacion',
                'verbose_name_plural': 'Evaluaciones Archivos Operacion',
                'db_table': 'evaluacion_archivos_operacion',
                'ordering': ['nombre_archivo'],
            },
        ),
        migrations.AddIndex(
            model_name='evaluacionarchivosoperacion',
            index=models.Index(fields=['cod_dir_operacion'], name='eval_op_dir_idx'),
        ),
        migrations.AddIndex(
            model_name='evaluacionarchivosoperacion',
            index=models.Index(fields=['estado_archivo'], name='eval_op_estado_idx'),
        ),
        migrations.AddIndex(
            model_name='evaluacionarchivosoperacion',
            index=models.Index(fields=['lote_calificacion_masiva'], name='eval_op_lote_idx'),
        ),
    ]
