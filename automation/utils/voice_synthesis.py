#!/usr/bin/env python3
"""
Módulo de Síntesis de Voz - Integración con VEGA TTS
Genera audio con la voz clonada de VEGA (DOOM) para respuestas del bot
"""

import os
import sys
from pathlib import Path
from typing import Optional
import tempfile
import logging
from datetime import datetime

# Importar TTS
try:
    from TTS.api import TTS
except ImportError:
    TTS = None


class VoiceSynthesizer:
    """Sintetizador de voz usando modelo VEGA (DOOM)"""

    def __init__(self, voz_model_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        # Directorio del modelo de voz
        if voz_model_dir:
            self.voz_model_dir = Path(voz_model_dir)
        else:
            # Por defecto, usar voz_model/ relativo a este archivo
            self.voz_model_dir = Path(__file__).parent.parent / "voz_model"

        self.processed_audio_dir = self.voz_model_dir / "processed_audio"
        self.reference_audio = None
        self.tts = None
        self._initialized = False

        # Verificar que TTS esté instalado
        if TTS is None:
            self.logger.warning("TTS no está instalado. Síntesis de voz deshabilitada.")

    def initialize(self) -> bool:
        """
        Inicializa el modelo TTS y selecciona audio de referencia
        Esta operación es costosa, se hace una sola vez
        """
        if self._initialized:
            return True

        if TTS is None:
            self.logger.error("TTS no está instalado")
            return False

        try:
            self.logger.info("Inicializando modelo TTS...")

            # Verificar que exista el directorio de audio procesado
            if not self.processed_audio_dir.exists():
                self.logger.error(f"No existe {self.processed_audio_dir}")
                return False

            # Buscar archivos de audio de referencia
            wav_files = list(self.processed_audio_dir.glob("*.wav"))
            if not wav_files:
                self.logger.error("No hay archivos WAV en processed_audio/")
                return False

            # Usar el primer archivo como referencia (todos son voz de VEGA)
            self.reference_audio = wav_files[0]
            self.logger.info(f"Audio de referencia: {self.reference_audio.name}")

            # Cargar modelo XTTS v2
            self.logger.info("Cargando modelo XTTS v2... (puede tomar unos minutos)")
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

            self._initialized = True
            self.logger.info("✅ Modelo TTS inicializado correctamente")
            return True

        except Exception as e:
            self.logger.error(f"Error inicializando TTS: {e}")
            return False

    def text_to_speech(
        self,
        text: str,
        language: str = 'es',
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Convierte texto a voz usando la voz clonada de VEGA

        Args:
            text: Texto a sintetizar
            language: Idioma ('es' o 'en')
            output_file: Ruta opcional del archivo de salida. Si no se especifica,
                        se crea un archivo temporal

        Returns:
            Ruta del archivo de audio generado, o None si hay error
        """
        # Inicializar si no se ha hecho
        if not self._initialized:
            if not self.initialize():
                self.logger.error("No se pudo inicializar el sintetizador")
                return None

        try:
            # Crear archivo de salida si no se especificó
            if output_file is None:
                # Usar archivo temporal
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_dir = Path(tempfile.gettempdir())
                output_file = str(temp_dir / f"vega_voice_{timestamp}.wav")

            self.logger.info(f"Generando audio: '{text[:50]}...'")

            # Generar audio
            self.tts.tts_to_file(
                text=text,
                speaker_wav=str(self.reference_audio),
                file_path=output_file,
                language=language
            )

            # Verificar que se creó el archivo
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 1000:  # Al menos 1KB
                    self.logger.info(f"✅ Audio generado: {output_file} ({file_size:,} bytes)")
                    return output_file
                else:
                    self.logger.error(f"Archivo generado muy pequeño: {file_size} bytes")
                    return None
            else:
                self.logger.error("No se pudo crear el archivo de audio")
                return None

        except Exception as e:
            self.logger.error(f"Error generando audio: {e}")
            return None

    def text_to_speech_bytes(self, text: str, language: str = 'es') -> Optional[bytes]:
        """
        Convierte texto a voz y retorna bytes (útil para enviar por Telegram)

        Args:
            text: Texto a sintetizar
            language: Idioma ('es' o 'en')

        Returns:
            Bytes del archivo de audio, o None si hay error
        """
        # Generar archivo temporal
        audio_file = self.text_to_speech(text, language)

        if audio_file is None:
            return None

        try:
            # Leer archivo como bytes
            with open(audio_file, 'rb') as f:
                audio_bytes = f.read()

            # Eliminar archivo temporal
            try:
                os.remove(audio_file)
            except:
                pass

            return audio_bytes

        except Exception as e:
            self.logger.error(f"Error leyendo archivo de audio: {e}")
            return None

    def is_available(self) -> bool:
        """Verifica si el sintetizador está disponible"""
        if TTS is None:
            return False

        if not self._initialized:
            return self.initialize()

        return True


# Instancia global (se inicializa bajo demanda)
_synthesizer = None


def get_synthesizer() -> VoiceSynthesizer:
    """Obtiene la instancia global del sintetizador"""
    global _synthesizer
    if _synthesizer is None:
        _synthesizer = VoiceSynthesizer()
    return _synthesizer


def text_to_speech(text: str, language: str = 'es') -> Optional[str]:
    """
    Función de conveniencia para generar audio

    Args:
        text: Texto a sintetizar
        language: Idioma ('es' o 'en')

    Returns:
        Ruta del archivo de audio generado
    """
    synth = get_synthesizer()
    return synth.text_to_speech(text, language)


def text_to_speech_bytes(text: str, language: str = 'es') -> Optional[bytes]:
    """
    Función de conveniencia para generar audio como bytes

    Args:
        text: Texto a sintetizar
        language: Idioma ('es' o 'en')

    Returns:
        Bytes del archivo de audio
    """
    synth = get_synthesizer()
    return synth.text_to_speech_bytes(text, language)


if __name__ == '__main__':
    # Test del módulo
    logging.basicConfig(level=logging.INFO)

    synth = VoiceSynthesizer()

    if not synth.is_available():
        print("❌ Sintetizador no disponible")
        sys.exit(1)

    print("✅ Sintetizador disponible")

    # Test de generación
    test_text = "Hola, soy VEGA. Sistema de inteligencia artificial completamente funcional."

    print(f"\n🎤 Generando audio de prueba...")
    audio_file = synth.text_to_speech(test_text, language='es')

    if audio_file:
        print(f"✅ Audio generado: {audio_file}")
    else:
        print("❌ Error generando audio")
