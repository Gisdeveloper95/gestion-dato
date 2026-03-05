import os
import subprocess
import tempfile
from pathlib import Path
from tqdm import tqdm
import torch
import torchaudio
import numpy as np

class ProfessionalVocalSeparator:
    def __init__(self, input_dir, output_dir="voces_separadas"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Crear directorio de salida
        self.output_dir.mkdir(exist_ok=True)
        
        # Verificar si hay GPU disponible
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Usando dispositivo: {self.device}")
        
        # Cargar modelo preentrenado para separación
        self.setup_model()
    
    def setup_model(self):
        """Configura el modelo de separación de fuentes"""
        try:
            # Usar la API correcta de demucs
            print("Cargando modelo HTDEMUCS...")
            from demucs.pretrained import get_model
            from demucs.apply import apply_model
            
            self.model = get_model('htdemucs')
            self.apply_model = apply_model  # Función para aplicar el modelo
            print("✓ Modelo cargado exitosamente")
        except ImportError:
            print("ERROR: Instala demucs con: pip install demucs")
            raise
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            # Fallback a método alternativo
            self.use_alternative_method = True
            print("Usando método alternativo...")
    
    def extract_audio_from_mkv(self, mkv_file, output_wav):
        """Extrae audio de MKV con configuración optimizada"""
        try:
            cmd = [
                'ffmpeg', '-i', str(mkv_file),
                '-vn',  # Sin video
                '-acodec', 'pcm_s16le',  # WAV sin compresión
                '-ar', '44100',  # Sample rate alto para mejor calidad
                '-ac', '2',  # Estéreo (importante para separación)
                '-y',
                str(output_wav)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error extrayendo audio: {e}")
            return False
    
    def separate_vocals_with_demucs(self, audio_file):
        """Separa voces usando demucs correctamente"""
        try:
            print("Separando fuentes de audio con HTDEMUCS...")
            
            # Cargar audio
            waveform, sample_rate = torchaudio.load(audio_file)
            
            # Asegurar formato correcto
            if sample_rate != 44100:
                resampler = torchaudio.transforms.Resample(sample_rate, 44100)
                waveform = resampler(waveform)
                sample_rate = 44100
            
            # Asegurar que sea estéreo
            if waveform.shape[0] == 1:
                waveform = waveform.repeat(2, 1)
            
            # Normalizar
            waveform = waveform.float()
            
            # Aplicar modelo usando la función correcta
            with torch.no_grad():
                # apply_model devuelve las fuentes separadas
                sources = self.apply_model(
                    self.model, 
                    waveform.unsqueeze(0),  # Agregar batch dimension
                    device=self.device,
                    progress=False
                )
                
                # sources shape: [batch, stems, channels, time]
                # stems: 0=drums, 1=bass, 2=other, 3=vocals
                vocals = sources[0, 3]  # Extraer voces
            
            # Convertir a numpy
            vocals = vocals.cpu().numpy()
            
            return vocals, sample_rate
            
        except Exception as e:
            print(f"Error en separación con demucs: {e}")
            return self.separate_vocals_alternative(audio_file)
    
    def separate_vocals_alternative(self, audio_file):
        """Método alternativo usando técnicas de procesamiento avanzadas"""
        try:
            print("Usando método alternativo para separación...")
            import librosa
            import scipy.signal
            
            # Cargar audio
            y, sr = librosa.load(audio_file, sr=44100, mono=False)
            
            # Si es mono, hacer estéreo
            if len(y.shape) == 1:
                y = np.stack([y, y])
            
            # Método 1: Separación por cancelación de centro (vocal isolation)
            # Esto funciona bien cuando las voces están centradas
            if y.shape[0] == 2:  # Estéreo
                # Vocal isolation: restar canal derecho del izquierdo
                vocals = y[0] - y[1]
                
                # Método 2: Combinado con filtrado de frecuencias
                # Filtro paso banda para voces humanas (80Hz - 8kHz)
                sos = scipy.signal.butter(6, [80, 8000], btype='band', fs=sr, output='sos')
                vocals_filtered = scipy.signal.sosfilt(sos, vocals)
                
                # Método 3: Espectral gating para mejorar
                stft = librosa.stft(vocals_filtered, n_fft=2048, hop_length=512)
                magnitude = np.abs(stft)
                phase = np.angle(stft)
                
                # Aplicar threshold espectral para limpiar
                threshold = np.percentile(magnitude, 60)
                magnitude_clean = np.where(magnitude > threshold, magnitude, magnitude * 0.3)
                
                # Reconstruir
                stft_clean = magnitude_clean * np.exp(1j * phase)
                vocals_final = librosa.istft(stft_clean, hop_length=512)
                
                # Convertir a estéreo para salida
                vocals_stereo = np.stack([vocals_final, vocals_final])
                
            else:
                vocals_stereo = y
            
            return vocals_stereo, sr
            
        except Exception as e:
            print(f"Error en método alternativo: {e}")
            return None, None
    
    def enhance_vocals(self, vocals, sample_rate):
        """Mejora la calidad de las voces separadas"""
        try:
            import librosa
            import noisereduce as nr
            
            # Trabajar con cada canal por separado si es estéreo
            if len(vocals.shape) == 2:
                enhanced_vocals = []
                for channel in vocals:
                    # Reducción de ruido
                    clean = nr.reduce_noise(
                        y=channel, 
                        sr=sample_rate,
                        stationary=False,
                        prop_decrease=0.5
                    )
                    
                    # Normalización
                    clean = librosa.util.normalize(clean, norm=np.inf)
                    
                    # Compresión dinámica suave
                    clean = np.tanh(clean * 0.9) / 0.9
                    
                    enhanced_vocals.append(clean)
                
                return np.array(enhanced_vocals)
            else:
                # Mono
                clean = nr.reduce_noise(y=vocals, sr=sample_rate, stationary=False, prop_decrease=0.5)
                clean = librosa.util.normalize(clean, norm=np.inf)
                clean = np.tanh(clean * 0.9) / 0.9
                return clean
            
        except Exception as e:
            print(f"Aplicando mejora básica: {e}")
            return vocals
    
    def save_as_mp3(self, audio_data, sample_rate, output_file):
        """Guarda audio como MP3 de alta calidad"""
        try:
            # Asegurar formato correcto
            if len(audio_data.shape) == 1:
                audio_data = np.stack([audio_data, audio_data])
            
            # Guardar como WAV temporal
            temp_wav = self.temp_dir / "vocals_temp.wav"
            torchaudio.save(
                temp_wav, 
                torch.from_numpy(audio_data), 
                sample_rate
            )
            
            # Convertir a MP3 con alta calidad
            cmd = [
                'ffmpeg', '-i', str(temp_wav),
                '-codec:a', 'libmp3lame',
                '-b:a', '320k',
                '-ar', '44100',
                '-af', 'volume=1.2',  # Aumentar volumen ligeramente
                '-y',
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            temp_wav.unlink(missing_ok=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error guardando MP3: {e}")
            return False
    
    def process_single_file(self, mkv_file):
        """Procesa un archivo MKV completo"""
        print(f"\n🎵 Procesando: {mkv_file.name}")
        
        # Extraer audio
        temp_audio = self.temp_dir / f"{mkv_file.stem}_audio.wav"
        print("  📤 Extrayendo audio...")
        
        if not self.extract_audio_from_mkv(mkv_file, temp_audio):
            print("  ❌ Error extrayendo audio")
            return False
        
        # Separar voces
        print("  🤖 Separando voces...")
        try:
            vocals, sr = self.separate_vocals_with_demucs(temp_audio)
        except:
            vocals, sr = self.separate_vocals_alternative(temp_audio)
        
        if vocals is None:
            print("  ❌ Error en separación")
            temp_audio.unlink(missing_ok=True)
            return False
        
        # Mejorar calidad
        print("  ✨ Mejorando calidad...")
        vocals_enhanced = self.enhance_vocals(vocals, sr)
        
        # Guardar resultado
        output_file = self.output_dir / f"{mkv_file.stem}_voces.mp3"
        print("  💾 Guardando resultado...")
        
        success = self.save_as_mp3(vocals_enhanced, sr, output_file)
        temp_audio.unlink(missing_ok=True)
        
        if success:
            print(f"  ✅ Completado: {output_file.name}")
            return True
        else:
            print("  ❌ Error guardando")
            return False
    
    def process_all_files(self):
        """Procesa todos los archivos MKV"""
        #mkv_files = list(self.input_dir.glob("*.mkv"))
        mkv_files = list(self.input_dir.glob("*.mp4"))
        if not mkv_files:
            print("❌ No se encontraron archivos MKV")
            return
        
        print(f"🎯 Encontrados {len(mkv_files)} archivos MKV")
        print(f"📁 Salida: {self.output_dir.absolute()}")
        print("=" * 60)
        
        successful = 0
        failed = 0
        
        for mkv_file in mkv_files:
            try:
                if self.process_single_file(mkv_file):
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Error procesando {mkv_file.name}: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL:")
        print(f"✅ Exitosos: {successful}")
        print(f"❌ Fallidos: {failed}")
        print(f"📁 Total: {len(mkv_files)}")
        
        if successful > 0:
            print(f"\n🎉 Archivos procesados guardados en:")
            print(f"   {self.output_dir.absolute()}")
    
    def cleanup(self):
        """Limpia archivos temporales"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

def check_dependencies():
    """Verifica dependencias con instalación automática opcional"""
    missing = []
    
    try:
        import torch
        import torchaudio
        print("✅ PyTorch instalado")
    except ImportError:
        missing.append("torch")
    
    try:
        import librosa
        import noisereduce
        import scipy
        print("✅ Librerías de audio instaladas")
    except ImportError:
        missing.append("audio_libs")
    
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg disponible")
    except:
        missing.append("ffmpeg")
    
    if missing:
        print("\n📦 INSTALAR DEPENDENCIAS FALTANTES:")
        if "torch" in missing:
            print("   pip install torch torchaudio")
        if "audio_libs" in missing:
            print("   pip install librosa noisereduce scipy soundfile")
        if "ffmpeg" in missing:
            print("   Descargar FFmpeg de: https://ffmpeg.org/download.html")
        
        print("\n💡 Instalar demucs (opcional, para mejor calidad):")
        print("   pip install demucs")
        
        return False
    
    return True

def main():
    print("🎵 SEPARADOR DE VOCES MEJORADO 🎵")
    print("=" * 60)
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n⚠️  Algunas dependencias faltan, pero el script intentará funcionar...")
        input("Presiona Enter para continuar o Ctrl+C para salir...")
    
    # Configuración
    input_directory = r"C:\Users\osori\Videos"
    output_directory = r"C:\Users\osori\Videos\voces_separadas"
    
    print(f"\n📂 Entrada: {input_directory}")
    print(f"📁 Salida: {output_directory}")
    
    # Procesar archivos
    separator = ProfessionalVocalSeparator(input_directory, output_directory)
    
    try:
        separator.process_all_files()
    finally:
        separator.cleanup()

if __name__ == "__main__":
    main()