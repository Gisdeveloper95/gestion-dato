#!/usr/bin/env python3
"""
GENERADOR DE VOZ - SIMPLE
=========================
Genera audio con tu voz clonada de forma interactiva

Uso: python generar_voz.py

Requisitos:
- Haber ejecutado 'crear_modelo.py' primero
- Carpeta 'processed_audio' con archivos WAV
- Archivo 'transcripts.json' con transcripciones
"""

import os
import sys
from pathlib import Path
import json
from TTS.api import TTS

class SimpleVoiceGenerator:
    def __init__(self):
        self.processed_dir = Path("processed_audio")
        self.transcripts_file = "transcripts.json"
        self.tts = None
        self.reference_audio = None
        
        print("🎤 GENERADOR DE VOZ")
        print("=" * 30)
    
    def check_model_files(self):
        """Verifica que existan los archivos del modelo"""
        print("🔍 Verificando archivos del modelo...")
        
        # Verificar carpeta de audio procesado
        if not self.processed_dir.exists():
            print(f"❌ No existe la carpeta '{self.processed_dir}'")
            print("💡 Ejecuta primero 'crear_modelo.py'")
            return False
        
        # Verificar archivos WAV
        wav_files = list(self.processed_dir.glob("*.wav"))
        if not wav_files:
            print(f"❌ No hay archivos WAV en '{self.processed_dir}'")
            print("💡 Ejecuta primero 'crear_modelo.py'")
            return False
        
        # Verificar transcripciones
        if not os.path.exists(self.transcripts_file):
            print(f"❌ No existe '{self.transcripts_file}'")
            print("💡 Ejecuta primero 'crear_modelo.py'")
            return False
        
        print(f"✅ Encontrados {len(wav_files)} archivos de audio")
        print(f"✅ Transcripciones encontradas")
        
        return True
    
    def load_tts_model(self):
        """Carga el modelo TTS"""
        print("\n📥 Cargando modelo TTS...")
        print("⏳ Esto puede tomar unos minutos la primera vez...")
        
        try:
            # Cargar modelo XTTS v2
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            print("✅ Modelo TTS cargado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo TTS: {e}")
            print("💡 Asegúrate de tener instalado: pip install TTS")
            return False
    
    def select_reference_audio(self):
        """Selecciona un audio de referencia"""
        wav_files = list(self.processed_dir.glob("*.wav"))
        
        # Por simplicidad, usar el primer archivo
        self.reference_audio = wav_files[0]
        print(f"🎯 Usando audio de referencia: {self.reference_audio.name}")
        
        return True
    
    def get_user_input(self):
        """Obtiene entrada del usuario por chat"""
        print("\n" + "="*40)
        print("📝 CONFIGURACIÓN DE GENERACIÓN")
        print("="*40)
        
        # Solicitar texto
        while True:
            text = input("\n🔤 Escribe el texto a generar:\n> ").strip()
            if text:
                break
            print("❌ El texto no puede estar vacío")
        
        # Solicitar idioma
        while True:
            print("\n🌍 Selecciona el idioma:")
            print("  es - Español")
            print("  en - English")
            language = input("\n🔤 Idioma (es/en): ").strip().lower()
            
            if language in ['es', 'en']:
                break
            print("❌ Selecciona 'es' o 'en'")
        
        # Solicitar nombre de archivo
        while True:
            filename = input(f"\n📁 Nombre del archivo de salida (sin .wav):\n> ").strip()
            if filename:
                # Asegurar que termine en .wav
                if not filename.endswith('.wav'):
                    filename += '.wav'
                
                # Verificar que no exista (o preguntar si sobrescribir)
                if os.path.exists(filename):
                    overwrite = input(f"⚠️  El archivo '{filename}' ya existe. ¿Sobrescribir? (s/n): ")
                    if overwrite.lower() == 's':
                        break
                    else:
                        continue
                else:
                    break
            else:
                print("❌ El nombre de archivo no puede estar vacío")
        
        return text, language, filename
    
    def generate_audio(self, text, language, output_file):
        """Genera el audio con la configuración especificada"""
        print(f"\n🎙️ GENERANDO AUDIO")
        print("="*30)
        print(f"📝 Texto: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"🌍 Idioma: {'Español' if language == 'es' else 'English'}")
        print(f"📁 Archivo: {output_file}")
        print(f"🎯 Referencia: {self.reference_audio.name}")
        print("\n⏳ Generando... (esto puede tomar unos minutos)")
        
        try:
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
                    print(f"\n✅ ¡Audio generado exitosamente!")
                    print(f"📁 Archivo: {output_file}")
                    print(f"📊 Tamaño: {file_size:,} bytes")
                    return True
                else:
                    print(f"\n❌ El archivo generado es muy pequeño ({file_size} bytes)")
                    return False
            else:
                print(f"\n❌ No se pudo crear el archivo {output_file}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error generando audio: {e}")
            return False
    
    def run_interactive_mode(self):
        """Ejecuta el modo interactivo"""
        print("🎤 MODO INTERACTIVO")
        print("Genera audio con tu voz clonada")
        print("="*40)
        
        # Verificar archivos del modelo
        if not self.check_model_files():
            return False
        
        # Cargar modelo TTS
        if not self.load_tts_model():
            return False
        
        # Seleccionar audio de referencia
        if not self.select_reference_audio():
            return False
        
        print("\n✅ Todo listo para generar audio!")
        
        # Bucle principal de generación
        generation_count = 0
        
        while True:
            try:
                # Obtener configuración del usuario
                text, language, output_file = self.get_user_input()
                
                # Generar audio
                if self.generate_audio(text, language, output_file):
                    generation_count += 1
                    print(f"\n🎉 Audio #{generation_count} listo!")
                else:
                    print(f"\n❌ Error generando audio")
                
                # Preguntar si continuar
                print(f"\n❓ ¿Generar otro audio? (s/n): ", end="")
                continue_generating = input().strip().lower()
                
                if continue_generating != 's':
                    break
                    
            except KeyboardInterrupt:
                print(f"\n👋 Proceso interrumpido por el usuario")
                break
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                print("🔄 Intentando continuar...")
        
        print(f"\n👋 ¡Hasta luego!")
        print(f"📊 Total de audios generados: {generation_count}")
        return True

def show_help():
    """Muestra ayuda sobre el uso"""
    print("""
🎤 GENERADOR DE VOZ - AYUDA
==========================

ANTES DE USAR:
1. Ejecuta 'crear_modelo.py' para procesar tus audios
2. Asegúrate de tener la carpeta 'processed_audio' con archivos WAV
3. Asegúrate de tener el archivo 'transcripts.json'

IDIOMAS SOPORTADOS:
• es - Español
• en - English

CONSEJOS:
• Usa textos de longitud moderada (no muy largos)
• Para mejor calidad, usa frases completas
• El archivo de salida se guardará en la carpeta actual

EJEMPLO DE USO:
1. python generar_voz.py
2. Escribe tu texto: "Hola, esta es mi voz clonada"
3. Selecciona idioma: es
4. Nombre de archivo: mi_audio_1
5. ¡Listo!
""")

def main():
    # Verificar argumentos de ayuda
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    generator = SimpleVoiceGenerator()
    
    try:
        generator.run_interactive_mode()
    except KeyboardInterrupt:
        print(f"\n👋 Programa interrumpido")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        print("💡 Intenta ejecutar 'crear_modelo.py' primero")

if __name__ == "__main__":
    main()