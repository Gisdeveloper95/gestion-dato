#!/usr/bin/env python3
"""
Módulo de Síntesis de Voz - Ejecuta el generador como script externo
NO importa TTS - ejecuta el script que YA FUNCIONA
"""

import os
import sys
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime


class VoiceSynthesizer:
    """Wrapper que ejecuta el generador de voz como script externo"""

    def __init__(self, voz_model_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self._available = False

        if voz_model_dir:
            self.voz_model_dir = Path(voz_model_dir)
        else:
            self.voz_model_dir = Path(__file__).parent.parent / "voz_model"

        self.generator_script = self.voz_model_dir / "2_voz_generator.py"

    def initialize(self) -> bool:
        """Verifica que el generador esté disponible"""
        if self._initialized:
            return self._available

        try:
            # Verificar que existe el script
            if not self.generator_script.exists():
                self.logger.error(f"No existe {self.generator_script}")
                self._initialized = True
                self._available = False
                return False

            # Verificar audio procesado
            processed_audio = self.voz_model_dir / "processed_audio"
            if not processed_audio.exists() or not list(processed_audio.glob("*.wav")):
                self.logger.error("No hay archivos de audio procesados")
                self._initialized = True
                self._available = False
                return False

            # Verificar transcripts.json
            transcripts_file = self.voz_model_dir / "transcripts.json"
            if not transcripts_file.exists():
                self.logger.error("No existe transcripts.json")
                self._initialized = True
                self._available = False
                return False

            self._initialized = True
            self._available = True
            self.logger.info("✅ Generador de voz disponible")
            return True

        except Exception as e:
            self.logger.error(f"Error verificando generador: {e}")
            self._initialized = True
            self._available = False
            return False

    def text_to_speech(
        self,
        text: str,
        language: str = 'es',
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Genera audio ejecutando el generador como script externo

        Args:
            text: Texto a sintetizar
            language: Idioma ('es' o 'en')
            output_file: Ruta del archivo de salida

        Returns:
            Ruta del archivo generado o None
        """
        if not self.is_available():
            return None

        try:
            # Crear archivo de salida si no se especificó
            if output_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_dir = Path(tempfile.gettempdir())
                output_file = str(temp_dir / f"vega_voice_{timestamp}.wav")

            # Crear script Python temporal que usa el generador
            script_content = f'''#!/usr/bin/env python3
import sys
from pathlib import Path

# Cambiar al directorio del modelo
import os
os.chdir(r"{self.voz_model_dir}")

# Importar el generador
from TTS.api import TTS

class SimpleGenerator:
    def __init__(self):
        self.processed_dir = Path("processed_audio")
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        wav_files = list(self.processed_dir.glob("*.wav"))
        self.reference_audio = wav_files[0]

    def generate(self, text, language, output_file):
        self.tts.tts_to_file(
            text=text,
            speaker_wav=str(self.reference_audio),
            file_path=output_file,
            language=language
        )
        return output_file

gen = SimpleGenerator()
result = gen.generate(
    text=r"""{text}""",
    language="{language}",
    output_file=r"{output_file}"
)

print(f"✅ Audio generado: {{result}}")
'''

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False,
                dir='/tmp'
            ) as f:
                temp_script = f.name
                f.write(script_content)

            self.logger.info(f"Generando audio: {text[:50]}...")

            # Ejecutar script
            result = subprocess.run(
                ['python3', temp_script],
                cwd=str(self.voz_model_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes para textos largos
            )

            # Limpiar script temporal
            try:
                os.unlink(temp_script)
            except:
                pass

            if result.returncode == 0 and os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 1000:
                    self.logger.info(f"✅ Audio generado: {output_file} ({file_size:,} bytes)")
                    return output_file
                else:
                    self.logger.error(f"Archivo muy pequeño: {file_size} bytes")
                    return None
            else:
                self.logger.error(f"Error generando audio: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            self.logger.error("Timeout generando audio")
            return None
        except Exception as e:
            self.logger.error(f"Error en text_to_speech: {e}")
            return None

    def text_to_speech_bytes(self, text: str, language: str = 'es') -> Optional[bytes]:
        """
        Genera audio y retorna bytes

        Args:
            text: Texto a sintetizar
            language: Idioma ('es' o 'en')

        Returns:
            Bytes del archivo de audio o None
        """
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
                self.logger.info(f"🗑️ Archivo temporal limpiado: {audio_file}")
            except Exception as e:
                self.logger.warning(f"No se pudo limpiar archivo temporal: {e}")

            return audio_bytes

        except Exception as e:
            self.logger.error(f"Error leyendo audio: {e}")
            return None

    def is_available(self) -> bool:
        """Verifica si el sintetizador está disponible"""
        if not self._initialized:
            return self.initialize()
        return self._available


# Instancia global
_synthesizer = None


def get_synthesizer() -> VoiceSynthesizer:
    """Obtiene la instancia global del sintetizador"""
    global _synthesizer
    if _synthesizer is None:
        _synthesizer = VoiceSynthesizer()
    return _synthesizer


def text_to_speech(text: str, language: str = 'es') -> Optional[str]:
    """Genera audio y retorna ruta del archivo"""
    synth = get_synthesizer()
    return synth.text_to_speech(text, language)


def text_to_speech_bytes(text: str, language: str = 'es') -> Optional[bytes]:
    """Genera audio y retorna bytes"""
    synth = get_synthesizer()
    return synth.text_to_speech_bytes(text, language)


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO)

    synth = VoiceSynthesizer()

    if not synth.is_available():
        print("❌ Sintetizador no disponible")
        exit(1)

    print("✅ Sintetizador disponible")

    # Test de generación
    test_text = "Hola, soy VEGA. Sistema completamente funcional."
    print(f"\n🎤 Generando audio de prueba...")

    audio_file = synth.text_to_speech(test_text)

    if audio_file:
        print(f"✅ Audio generado: {audio_file}")
    else:
        print("❌ Error generando audio")
