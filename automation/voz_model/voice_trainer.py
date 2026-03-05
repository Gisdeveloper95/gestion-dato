import os
import librosa
import soundfile as sf
import whisper
from pathlib import Path
import json
from tqdm import tqdm
import torch
from TTS.api import TTS
import numpy as np

class VoiceTrainer:
    def __init__(self, audio_dir="audio_personaje"):
        self.audio_dir = Path(audio_dir)
        self.processed_dir = Path("processed_audio")
        self.transcripts_file = "transcripts.json"
        self.model_dir = Path("trained_model")
        
        # Crear directorios necesarios
        self.processed_dir.mkdir(exist_ok=True)
        self.model_dir.mkdir(exist_ok=True)
        
        # Inicializar Whisper para transcripción automática
        print("Cargando modelo Whisper para transcripción...")
        self.whisper_model = whisper.load_model("base")
        
    def preprocess_audio(self, max_duration=30, min_duration=2):
        """
        Procesa todos los MP3 del directorio, los convierte a WAV y los segmenta
        """
        print(f"Procesando audios desde {self.audio_dir}...")
        
        mp3_files = list(self.audio_dir.glob("*.mp3"))
        if not mp3_files:
            print(f"❌ No se encontraron archivos MP3 en {self.audio_dir}")
            return False
            
        print(f"📁 Encontrados {len(mp3_files)} archivos MP3")
        
        processed_count = 0
        processed_files = []  # Lista para rastrear archivos creados
        
        for mp3_file in tqdm(mp3_files, desc="Procesando archivos"):
            try:
                # Cargar audio
                audio, sr = librosa.load(mp3_file, sr=22050)
                
                # Si el audio es muy largo, segmentarlo
                if len(audio) / sr > max_duration:
                    segments = self._segment_audio(audio, sr, max_duration)
                    
                    for i, segment in enumerate(segments):
                        if len(segment) / sr >= min_duration:  # Solo guardar segmentos suficientemente largos
                            output_file = self.processed_dir / f"{mp3_file.stem}_seg{i:03d}.wav"
                            sf.write(output_file, segment, sr)
                            processed_files.append(output_file)
                            processed_count += 1
                            print(f"  ✓ Creado: {output_file}")
                else:
                    # Audio corto, guardar directamente
                    if len(audio) / sr >= min_duration:
                        output_file = self.processed_dir / f"{mp3_file.stem}.wav"
                        sf.write(output_file, audio, sr)
                        processed_files.append(output_file)
                        processed_count += 1
                        print(f"  ✓ Creado: {output_file}")
                        
            except Exception as e:
                print(f"❌ Error procesando {mp3_file}: {e}")
        
        # Verificar que los archivos existen
        print(f"\n🔍 Verificando archivos creados:")
        for file_path in processed_files:
            if file_path.exists():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path} - NO EXISTE")
                
        print(f"✅ Procesados {processed_count} segmentos de audio")
        return processed_count > 0
    
    def _segment_audio(self, audio, sr, max_duration):
        """Segmenta audio largo en chunks más pequeños"""
        max_samples = int(max_duration * sr)
        segments = []
        
        for start in range(0, len(audio), max_samples):
            end = min(start + max_samples, len(audio))
            segments.append(audio[start:end])
            
        return segments
    
    def transcribe_audio(self):
        """
        Transcribe automáticamente todos los audios procesados usando Whisper
        """
        print("🎤 Iniciando transcripción automática...")
        
        wav_files = list(self.processed_dir.glob("*.wav"))
        if not wav_files:
            print("❌ No hay archivos WAV para transcribir")
            return False
        
        print(f"🔍 Archivos WAV encontrados:")
        for wav_file in wav_files:
            exists = "✅" if wav_file.exists() else "❌"
            size = wav_file.stat().st_size if wav_file.exists() else 0
            print(f"  {exists} {wav_file} ({size} bytes)")
            
        transcripts = {}
        
        for wav_file in tqdm(wav_files, desc="Transcribiendo"):
            try:
                # Verificar que el archivo existe y no está vacío
                if not wav_file.exists():
                    print(f"❌ Archivo no existe: {wav_file}")
                    continue
                    
                if wav_file.stat().st_size == 0:
                    print(f"❌ Archivo vacío: {wav_file}")
                    continue
                
                # Transcribir con Whisper usando ruta absoluta
                absolute_path = wav_file.resolve()
                print(f"🎯 Transcribiendo: {absolute_path}")
                
                result = self.whisper_model.transcribe(str(absolute_path))
                text = result["text"].strip()
                
                if text and len(text) > 5:  # Solo guardar transcripciones válidas
                    transcripts[wav_file.name] = {
                        "text": text,
                        "path": str(absolute_path),
                        "duration": librosa.get_duration(path=absolute_path)
                    }
                    print(f"  ✅ Transcrito: '{text[:50]}...'")
                else:
                    print(f"  ⚠️ Transcripción vacía o muy corta")
                    
            except Exception as e:
                print(f"❌ Error transcribiendo {wav_file}: {e}")
                import traceback
                traceback.print_exc()
        
        # Guardar transcripciones
        with open(self.transcripts_file, 'w', encoding='utf-8') as f:
            json.dump(transcripts, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Transcribidas {len(transcripts)} archivos")
        print(f"📝 Transcripciones guardadas en {self.transcripts_file}")
        
        # Mostrar algunas muestras
        if transcripts:
            print("\n📋 Muestra de transcripciones:")
            for i, (filename, data) in enumerate(list(transcripts.items())[:3]):
                print(f"  {filename}: '{data['text'][:100]}...'")
        
        return len(transcripts) > 0
    
    def setup_training_data(self):
        """
        Prepara los datos en el formato requerido por Coqui TTS
        """
        print("📊 Preparando datos para entrenamiento...")
        
        # Cargar transcripciones
        if not os.path.exists(self.transcripts_file):
            print(f"❌ No se encontró {self.transcripts_file}")
            return False
            
        with open(self.transcripts_file, 'r', encoding='utf-8') as f:
            transcripts = json.load(f)
            
        # Crear archivo de metadatos para TTS
        metadata_lines = []
        for filename, data in transcripts.items():
            # Formato: audio_path|text|speaker_name
            line = f"{data['path']}|{data['text']}|speaker_1"
            metadata_lines.append(line)
            
        # Guardar metadata
        metadata_file = "metadata.txt"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(metadata_lines))
            
        print(f"✅ Metadata creada: {len(metadata_lines)} muestras")
        print(f"📄 Archivo guardado como {metadata_file}")
        
        return True
    
    def start_training(self):
        """
        Inicia el entrenamiento del modelo de voz
        """
        print("🚀 Iniciando entrenamiento...")
        
        # Verificar que tenemos GPU disponible
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🖥️  Usando dispositivo: {device}")
        
        try:
            # Configurar TTS para entrenamiento
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            print("⚠️  NOTA: El entrenamiento completo puede tomar varias horas.")
            print("📚 Para entrenar tu modelo personalizado, ejecuta:")
            print(f"    python -m TTS.bin.train_tts --config_path config.json")
            print(f"📁 Los datos están listos en: metadata.txt")
            
        except Exception as e:
            print(f"❌ Error configurando entrenamiento: {e}")
            
    def quick_test(self, text="Hola, esta es una prueba de la voz clonada. Hi andrew, it is a text voice"):
        """
        Prueba rápida con el modelo base usando una muestra de tu voz
        """
        print("🧪 Realizando prueba rápida...")
        
        # Buscar un archivo de referencia
        wav_files = list(self.processed_dir.glob("*.wav"))
        if not wav_files:
            print("❌ No hay archivos de referencia disponibles")
            return
            
        reference_file = wav_files[0]
        print(f"🎯 Usando como referencia: {reference_file.name}")
        
        try:
            # Cargar modelo XTTS
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            # Generar audio con la voz clonada
            output_file = "test_output.wav"
            tts.tts_to_file(
                text=text,
                speaker_wav=str(reference_file),
                file_path=output_file,
                language="es"  # Cambia según el idioma
            )
            
            print(f"✅ Audio generado: {output_file}")
            print(f"🔊 Texto usado: '{text}'")
            
        except Exception as e:
            print(f"❌ Error en prueba: {e}")

def main():
    print("🎙️  CLONADOR DE VOZ PERSONALIZADO")
    print("=" * 50)
    
    trainer = VoiceTrainer()
    
    # Verificar que existe el directorio
    if not trainer.audio_dir.exists():
        print(f"❌ El directorio {trainer.audio_dir} no existe")
        print("📁 Crea la carpeta 'audio_personaje' y añade tus archivos MP3")
        return
    
    # Proceso paso a paso
    print("\n🔄 PASO 1: Procesando archivos MP3...")
    if not trainer.preprocess_audio():
        print("❌ Error en el procesamiento de audio")
        return
    
    print("\n🔄 PASO 2: Transcribiendo automáticamente...")
    if not trainer.transcribe_audio():
        print("❌ Error en la transcripción")
        return
    
    print("\n🔄 PASO 3: Preparando datos de entrenamiento...")
    if not trainer.setup_training_data():
        print("❌ Error preparando datos")
        return
    
    print("\n🔄 PASO 4: Prueba rápida...")
    trainer.quick_test()
    
    print("\n✅ ¡PROCESO COMPLETADO!")
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa las transcripciones en 'transcripts.json'")
    print("2. Corrige manualmente si es necesario")
    print("3. Ejecuta el entrenamiento completo")
    print("4. ¡Prueba tu voz clonada!")

if __name__ == "__main__":
    main()