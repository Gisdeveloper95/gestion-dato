#!/usr/bin/env python3
"""
Comandos IA para el bot de Telegram
Estos métodos se agregan a la clase ServerBot
"""

async def cmd_pregunta(self, update, context):
    """Comando /pregunta - Consulta con IA"""
    user_id = update.effective_user.id

    if not self._puede_ejecutar_comando(user_id, 'pregunta'):
        rol = self._get_user_role(user_id)
        await update.message.reply_text(
            f"❌ No autorizado\nTu rol: `{rol}`\n"
            "Este comando requiere permisos de consulta.",
            parse_mode='Markdown'
        )
        return

    if not context.args:
        await update.message.reply_text(
            "💡 *Uso:* `/pregunta [tu consulta]`\n\n"
            "*Ejemplos:*\n"
            "• `/pregunta ¿Cuántos archivos tiene Ibagué?`\n"
            "• `/pregunta Busca shapefiles de cartografía en Neiva`\n"
            "• `/pregunta Estadísticas del Tolima`",
            parse_mode='Markdown'
        )
        return

    pregunta = ' '.join(context.args)
    processing_msg = await update.message.reply_text("🤖 Procesando consulta...")

    try:
        resultado = self.ai_system.procesar_consulta_completa(pregunta)

        message = "🤖 *Respuesta IA*\n\n"

        if resultado['municipios']:
            mun = resultado['municipios'][0]
            message += f"📍 *Municipio:* {mun['nombre']} ({mun['cod_dane']})\n\n"

        if resultado['archivos_encontrados']:
            total = len(resultado['archivos_encontrados'])
            message += f"🗂️ *Archivos relevantes:* {total}\n\n"

        message += f"💡 {resultado['respuesta_ia']}"

        await processing_msg.delete()
        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        self.logger.error(f"Error en /pregunta: {e}")
        await processing_msg.delete()
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def cmd_buscar(self, update, context):
    """Comando /buscar - Busca archivos por keywords"""
    user_id = update.effective_user.id

    if not self._puede_ejecutar_comando(user_id, 'buscar'):
        await update.message.reply_text("❌ No autorizado")
        return

    if not context.args:
        await update.message.reply_text(
            "💡 *Uso:* `/buscar [keywords]`\n\n"
            "*Ejemplos:*\n"
            "• `/buscar shp cartografia`\n"
            "• `/buscar excel poblacion`\n"
            "• `/buscar pdf estudio`",
            parse_mode='Markdown'
        )
        return

    keywords = context.args
    processing_msg = await update.message.reply_text("🔍 Buscando archivos...")

    try:
        archivos = self.ai_system.buscar_archivos_por_keywords(keywords)

        if not archivos:
            await processing_msg.delete()
            await update.message.reply_text(
                "❌ No se encontraron archivos\n\n"
                "💡 Intenta con otras palabras clave"
            )
            return

        message = f"🔍 *Resultados de Búsqueda*\n\n"
        message += f"Encontrados: *{len(archivos)}* archivos\n\n"

        for idx, archivo in enumerate(archivos[:5], 1):
            nombre_archivo = archivo['path'].split('/')[-1]
            message += f"📄 *{idx}. {nombre_archivo}*\n"
            message += f"   Origen: {archivo['origen']}\n"
            message += f"   Tamaño: {archivo['size_mb']:.2f} MB\n"
            message += f"   Fecha: {archivo['fecha']}\n"
            if archivo['cod_mpio']:
                message += f"   Municipio: {archivo['cod_mpio']}\n"
            message += "\n"

        if len(archivos) > 5:
            message += f"_... y {len(archivos) - 5} archivos más_\n\n"

        message += f"💡 Usa `/pregunta` para análisis detallado"

        await processing_msg.delete()
        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        self.logger.error(f"Error en /buscar: {e}")
        await processing_msg.delete()
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def cmd_municipio(self, update, context):
    """Comando /municipio - Info de un municipio"""
    user_id = update.effective_user.id

    if not self._puede_ejecutar_comando(user_id, 'municipio'):
        await update.message.reply_text("❌ No autorizado")
        return

    if not context.args:
        await update.message.reply_text(
            "💡 *Uso:* `/municipio [nombre]`\n\n"
            "*Ejemplos:*\n"
            "• `/municipio Ibagué`\n"
            "• `/municipio Neiva`\n"
            "• `/municipio Bogotá`",
            parse_mode='Markdown'
        )
        return

    nombre = ' '.join(context.args)
    processing_msg = await update.message.reply_text("🔍 Buscando municipio...")

    try:
        municipio = self.ai_system.buscar_municipio(nombre)

        if not municipio:
            await processing_msg.delete()
            await update.message.reply_text(
                f"❌ No se encontró: *{nombre}*\n\n"
                "💡 Verifica el nombre del municipio",
                parse_mode='Markdown'
            )
            return

        if 'multiples' in municipio:
            message = "📍 *Múltiples resultados encontrados:*\n\n"
            for idx, m in enumerate(municipio['multiples'], 1):
                message += f"{idx}. *{m['nombre']}* ({m['cod_dane']})\n"
                message += f"   Departamento: {m['nombre_depto']}\n\n"
            message += "💡 Especifica mejor el nombre"
            await processing_msg.delete()
            await update.message.reply_text(message, parse_mode='Markdown')
            return

        stats = self.ai_system.obtener_estadisticas_municipio(municipio['cod_dane'])

        message = f"📍 *{municipio['nombre']}*\n\n"
        message += f"🆔 Código DANE: `{municipio['cod_dane']}`\n"
        message += f"🏛️ Departamento: {municipio['nombre_depto']} ({municipio['cod_depto']})\n\n"

        if stats and stats.get('total_archivos', 0) > 0:
            message += f"📊 *Estadísticas PREOPERACION:*\n"
            message += f"• Total archivos: *{stats['total_archivos']:,}*\n"
            message += f"• Peso total: *{stats['peso_total_gb']:.2f} GB*\n\n"

            if stats['categorias']:
                message += "📁 *Top 5 categorías:*\n"
                for idx, cat in enumerate(stats['categorias'][:5], 1):
                    message += f"{idx}. {cat['categoria']}: {cat['archivos']:,} archivos ({cat['peso_mb']:.1f} MB)\n"
                message += f"\n⏰ Última actualización: {stats['categorias'][0]['ultima_modificacion']}"
        else:
            message += "⚠️ No hay datos disponibles para este municipio"

        await processing_msg.delete()
        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        self.logger.error(f"Error en /municipio: {e}")
        await processing_msg.delete()
        await update.message.reply_text(f"❌ Error: {str(e)}")
