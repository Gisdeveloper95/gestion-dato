#!/usr/bin/env python3
"""
CREADOR DE MODELO DE VOZ - SIMPLE
=================================
Crea un modelo de voz a partir de archivos de audio MP3

Uso: python crear_modelo.py

Requisitos:
- Carpeta 'audio_personaje' con archivos MP3 de la voz
- Al menos 5-10 minutos de audio total
"""

import os
import librosa
import soundfile as sf
import whisper
from pathlib import Path
import json
from tqdm import tqdm

class SimpleVoiceTrainer:
    def __init__(self):
        self.audio_dir = Path("audio_personaje")
        self.processed_dir = Path("processed_audio")
        self.transcripts_file = "transcripts.json"
        
        # Crear directorio de salida
        self.processed_dir.mkdir(exist_ok=True)
        
        print("🎙️  CREADOR DE MODELO DE VOZ")
        print("=" * 40)
    
    def check_audio_files(self):
        """Verifica que existan archivos de audio"""
        print("🔍 Verificando archivos de audio...")
        
        if not self.audio_dir.exists():
            print(f"❌ ERROR: No existe la carpeta '{self.audio_dir}'")
            print(f"📁 Crea la carpeta y añade archivos MP3")
            return False
        
        mp3_files = list(self.audio_dir.glob("*.mp3"))
        if not mp3_files:
            print(f"❌ ERROR: No hay archivos MP3 en '{self.audio_dir}'")
            print(f"🎵 Añade archivos MP3 con la voz a clonar")
            return False
        
        # Calcular duración total
        total_duration = 0
        for mp3_file in mp3_files:
            try:
                duration = librosa.get_duration(path=mp3_file)
                total_duration += duration
            except:
                pass
        
        print(f"✅ Encontrados {len(mp3_files)} archivos MP3")
        print(f"⏱️  Duración total: {total_duration/60:.1f} minutos")
        
        if total_duration < 300:  # 5 minutos
            print("⚠️  ADVERTENCIA: Menos de 5 minutos de audio")
            print("💡 Recomendado: Al menos 5-10 minutos para buena calidad")
        
        return True
    
    def process_audio_files(self):
        """Convierte MP3 a WAV y segmenta si es necesario"""
        print("\n🔄 Procesando archivos de audio...")
        
        mp3_files = list(self.audio_dir.glob("*.mp3"))
        processed_count = 0
        
        for mp3_file in tqdm(mp3_files, desc="Convirtiendo a WAV"):
            try:
                # Cargar audio
                audio, sr = librosa.load(mp3_file, sr=22050)
                
                # Normalizar
                audio = librosa.util.normalize(audio)
                
                # Si es muy largo (más de 30 segundos), segmentar
                if len(audio) / sr > 30:
                    # Dividir en segmentos de 30 segundos
                    segment_length = 30 * sr
                    
                    for i in range(0, len(audio), segment_length):
                        segment = audio[i:i + segment_length]
                        
                        # Solo guardar si el segmento es mayor a 2 segundos
                        if len(segment) / sr >= 2:
                            output_file = self.processed_dir / f"{mp3_file.stem}_seg{i//segment_length:03d}.wav"
                            sf.write(output_file, segment, sr)
                            processed_count += 1
                else:
                    # Guardar archivo completo si es corto
                    if len(audio) / sr >= 2:
                        output_file = self.processed_dir / f"{mp3_file.stem}.wav"
                        sf.write(output_file, audio, sr)
                        processed_count += 1
                        
            except Exception as e:
                print(f"❌ Error procesando {mp3_file.name}: {e}")
        
        print(f"✅ Procesados {processed_count} archivos WAV")
        return processed_count > 0
    
    def transcribe_audio(self):
        """Transcribe los archivos de audio usando Whisper"""
        print("\n🔄 Transcribiendo archivos de audio...")
        print("⏳ Cargando Whisper (esto puede tomar un momento)...")
        
        try:
            model = whisper.load_model("base")
        except Exception as e:
            print(f"❌ Error cargando Whisper: {e}")
            print("💡 Asegúrate de tener instalado: pip install openai-whisper")
            return False
        
        wav_files = list(self.processed_dir.glob("*.wav"))
        if not wav_files:
            print("❌ No hay archivos WAV para transcribir")
            return False
        
        transcripts = {}
        successful_transcripts = 0
        
        for wav_file in tqdm(wav_files, desc="Transcribiendo"):
            try:
                # Transcribir archivo
                result = model.transcribe(str(wav_file))
                text = result["text"].strip()
                
                if text and len(text) > 5:
                    transcripts[wav_file.name] = {
                        "text": text,
                        "path": str(wav_file),
                        "language": result.get("language", "unknown")
                    }
                    successful_transcripts += 1
                    
            except Exception as e:
                print(f"❌ Error transcribiendo {wav_file.name}: {e}")
        
        # Guardar transcripciones
        if transcripts:
            with open(self.transcripts_file, 'w', encoding='utf-8') as f:
                json.dump(transcripts, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Transcribidos {successful_transcripts} archivos")
            
            # Mostrar ejemplos de transcripciones
            print("\n📝 Ejemplos de transcripciones:")
            for i, (filename, data) in enumerate(list(transcripts.items())[:3]):
                print(f"  • {filename}: '{data['text'][:60]}...'")
                print(f"    Idioma detectado: {data.get('language', 'unknown')}")
            
            return True
        else:
            print("❌ No se pudieron transcribir archivos")
            return False
    
    def create_model(self):
        """Ejecuta todo el proceso de creación del modelo"""
        print("🚀 INICIANDO CREACIÓN DEL MODELO")
        print("=" * 40)
        
        # Paso 1: Verificar archivos
        if not self.check_audio_files():
            return False
        
        # Paso 2: Procesar audio
        print(f"\n¿Procesar archivos de audio? (s/n): ", end="")
        if input().lower() != 's':
            print("❌ Proceso cancelado")
            return False
        
        if not self.process_audio_files():
            print("❌ Error procesando audio")
            return False
        
        # Paso 3: Transcribir
        print(f"\n¿Transcribir archivos? (s/n): ", end="")
        if input().lower() != 's':
            print("❌ Transcripción cancelada")
            return False
        
        if not self.transcribe_audio():
            print("❌ Error en transcripción")
            return False
        
        print("\n" + "="*50)
        print("✅ ¡MODELO CREADO EXITOSAMENTE!")
        print("="*50)
        print("\n📁 Archivos generados:")
        print(f"   • Carpeta: {self.processed_dir}")
        print(f"   • Transcripciones: {self.transcripts_file}")
        print("\n🎯 Ahora puedes usar 'generar_voz.py' para crear audio")
        print("="*50)
        
        return True

def main():
    print("🎙️  CREADOR DE MODELO DE VOZ")
    print("Este script procesa tus archivos MP3 y crea el modelo base")
    print("="*50)
    print("\nRequisitos:")
    print("• Carpeta 'audio_personaje' con archivos MP3")
    print("• Al menos 5-10 minutos de audio total")
    print("• Archivos de buena calidad y sin ruido de fondo")
    
    trainer = SimpleVoiceTrainer()
    
    if trainer.create_model():
        print("\n🎉 ¡Listo! Ya puedes generar voz con 'generar_voz.py'")
    else:
        print("\n❌ Error en la creación del modelo")
        print("💡 Revisa los mensajes de error arriba")

if __name__ == "__main__":
    main()