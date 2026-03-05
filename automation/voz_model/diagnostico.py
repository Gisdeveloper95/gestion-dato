#!/usr/bin/env python3
"""
GENERADOR CON DIAGNÓSTICO COMPLETO
=================================
Este script diagnostica y fuerza el idioma correctamente
"""

import os
import sys
import argparse
from pathlib import Path
import json
from TTS.api import TTS
import torch
import locale

class DiagnosticVoiceGenerator:
    def __init__(self):
        self.model_dir = Path("mi_modelo_voz")
        self.processed_dir = Path("processed_audio")
        self.transcripts_file = "transcripts.json"
        self.config_file = "config_entrenamiento.json"
        self.tts = None
        self.model_loaded = False
        self.reference_audio = None
        self.model_language = None
        
        print("🔧 GENERADOR CON DIAGNÓSTICO COMPLETO")
        print("=" * 50)
    
    def system_diagnosis(self):
        """Diagnóstico completo del sistema"""
        print("\n🔍 DIAGNÓSTICO DEL SISTEMA")
        print("-" * 30)
        
        # Configuración regional del sistema
        try:
            system_locale = locale.getdefaultlocale()
            print(f"🌍 Locale del sistema: {system_locale}")
        except:
            print("⚠️ No se pudo obtener locale del sistema")
        
        # Variables de entorno relacionadas con idioma
        lang_vars = ['LANG', 'LANGUAGE', 'LC_ALL', 'LC_CTYPE']
        for var in lang_vars:
            value = os.environ.get(var, 'No configurado')
            print(f"🔧 {var}: {value}")
        
        # Información de PyTorch y CUDA
        print(f"🔥 PyTorch: {torch.__version__}")
        print(f"🎮 CUDA disponible: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        
        return True
    
    def model_diagnosis(self):
        """Diagnóstico del modelo y configuración"""
        print("\n🔍 DIAGNÓSTICO DEL MODELO")
        print("-" * 30)
        
        # Verificar archivos de configuración
        configs_found = []
        
        if os.path.exists(self.config_file):
            print(f"✅ Configuración de entrenamiento: {self.config_file}")
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Mostrar configuración relevante
                if 'target_language' in config:
                    print(f"🎯 Idioma configurado: {config['target_language']}")
                    configs_found.append(config['target_language'])
                
                if 'datasets' in config and config['datasets']:
                    dataset_lang = config['datasets'][0].get('language')
                    print(f"📊 Idioma del dataset: {dataset_lang}")
                    configs_found.append(dataset_lang)
                
                # Mostrar configuración de audio
                if 'audio' in config:
                    print(f"🔊 Sample rate: {config['audio'].get('sample_rate', 'No especificado')}")
                
            except Exception as e:
                print(f"❌ Error leyendo configuración: {e}")
        else:
            print(f"❌ No existe: {self.config_file}")
        
        # Verificar transcripciones
        if os.path.exists(self.transcripts_file):
            print(f"✅ Transcripciones: {self.transcripts_file}")
            try:
                with open(self.transcripts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'language' in data:
                    print(f"📝 Idioma de transcripciones: {data['language']}")
                    configs_found.append(data['language'])
                
                # Mostrar muestras de texto
                transcripts = data.get('transcripts', data)
                if transcripts:
                    sample_texts = []
                    for filename, transcript_data in list(transcripts.items())[:3]:
                        if isinstance(transcript_data, dict):
                            text = transcript_data.get('text', '')
                        else:
                            text = str(transcript_data)
                        sample_texts.append(text[:50])
                    
                    print("📋 Muestras de texto:")
                    for i, text in enumerate(sample_texts):
                        print(f"   {i+1}. '{text}...'")
                
            except Exception as e:
                print(f"❌ Error leyendo transcripciones: {e}")
        else:
            print(f"❌ No existe: {self.transcripts_file}")
        
        # Verificar modelo entrenado
        if self.model_dir.exists():
            checkpoint_dirs = [d for d in self.model_dir.iterdir() if d.is_dir()]
            print(f"📂 Directorios de modelo: {len(checkpoint_dirs)}")
            
            for checkpoint_dir in checkpoint_dirs:
                model_files = list(checkpoint_dir.glob("*.pth"))
                config_files = list(checkpoint_dir.glob("config.json"))
                print(f"   {checkpoint_dir.name}: {len(model_files)} modelos, {len(config_files)} configs")
        else:
            print(f"❌ No existe directorio de modelo: {self.model_dir}")
        
        # Verificar archivos de referencia
        if self.processed_dir.exists():
            wav_files = list(self.processed_dir.glob("*.wav"))
            print(f"🎵 Archivos de referencia: {len(wav_files)}")
            if wav_files:
                print(f"   Ejemplo: {wav_files[0].name}")
        else:
            print(f"❌ No existe: {self.processed_dir}")
        
        # Resumen de idiomas encontrados
        if configs_found:
            unique_langs = list(set(configs_found))
            print(f"\n🌍 Idiomas detectados en configuración: {unique_langs}")
            if len(unique_langs) > 1:
                print("⚠️  ADVERTENCIA: Idiomas inconsistentes detectados!")
            return unique_langs[0]
        else:
            print("\n❌ No se detectó configuración de idioma")
            return None
    
    def load_model_with_diagnosis(self):
        """Carga modelo con diagnóstico detallado"""
        print("\n🔍 CARGANDO MODELO CON DIAGNÓSTICO")
        print("-" * 40)
        
        # Intentar modelo personalizado primero
        if self.check_model_exists():
            print("🎯 Intentando cargar modelo personalizado...")
            if self.load_trained_model_debug():
                return True
        
        # Cargar modelo de referencia
        print("🎯 Cargando modelo de referencia...")
        return self.load_reference_model_debug()
    
    def check_model_exists(self):
        """Verifica modelo personalizado"""
        if not self.model_dir.exists():
            return False
            
        checkpoint_dirs = [d for d in self.model_dir.iterdir() if d.is_dir()]
        return any(
            list(checkpoint_dir.glob("*.pth")) and list(checkpoint_dir.glob("config.json"))
            for checkpoint_dir in checkpoint_dirs
        )
    
    def load_trained_model_debug(self):
        """Carga modelo personalizado con diagnóstico"""
        try:
            checkpoint_dirs = [d for d in self.model_dir.iterdir() if d.is_dir()]
            latest_dir = max(checkpoint_dirs, key=os.path.getctime)
            
            model_files = list(latest_dir.glob("*.pth"))
            config_files = list(latest_dir.glob("config.json"))
            
            latest_model = max(model_files, key=os.path.getctime)
            config_file = config_files[0]
            
            print(f"📂 Directorio: {latest_dir}")
            print(f"🎯 Modelo: {latest_model.name}")
            print(f"⚙️ Config: {config_file.name}")
            
            # Leer configuración del modelo
            with open(config_file, 'r', encoding='utf-8') as f:
                model_config = json.load(f)
            
            # Mostrar configuración relevante
            print("📋 Configuración del modelo:")
            relevant_keys = ['model_name', 'language', 'audio', 'characters', 'phonemes']
            for key in relevant_keys:
                if key in model_config:
                    print(f"   {key}: {model_config[key]}")
            
            # Cargar modelo
            print("⏳ Inicializando TTS...")
            self.tts = TTS(model_path=str(latest_model), config_path=str(config_file))
            
            print("✅ Modelo personalizado cargado exitosamente!")
            self.model_loaded = True
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo personalizado: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_reference_model_debug(self):
        """Carga modelo de referencia con diagnóstico"""
        if not self.processed_dir.exists():
            print(f"❌ No existe: {self.processed_dir}")
            return False
            
        wav_files = list(self.processed_dir.glob("*.wav"))
        if not wav_files:
            print("❌ No hay archivos WAV de referencia")
            return False
            
        self.reference_audio = wav_files[0]
        print(f"🎯 Archivo de referencia: {self.reference_audio.name}")
        
        # Analizar audio de referencia
        try:
            import librosa
            duration = librosa.get_duration(path=self.reference_audio)
            audio, sr = librosa.load(self.reference_audio, sr=None)
            print(f"⏱️ Duración: {duration:.2f}s")
            print(f"🔊 Sample rate: {sr}Hz")
            print(f"📊 Samples: {len(audio)}")
        except Exception as e:
            print(f"⚠️ Error analizando audio: {e}")
        
        try:
            print("⏳ Cargando XTTS v2...")
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            # Obtener información del modelo
            print("📋 Información del modelo XTTS:")
            if hasattr(self.tts, 'synthesizer') and hasattr(self.tts.synthesizer, 'tts_model'):
                model = self.tts.synthesizer.tts_model
                if hasattr(model, 'language_manager'):
                    langs = getattr(model.language_manager, 'language_names', [])
                    print(f"   Idiomas soportados: {langs}")
            
            print("✅ Modelo de referencia cargado!")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando XTTS: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_with_forced_language(self, text, output_file, target_language):
        """Genera audio forzando el idioma de múltiples maneras"""
        print(f"\n🎙️ GENERANDO CON IDIOMA FORZADO: {target_language}")
        print(f"📝 Texto: '{text}'")
        print(f"📁 Archivo: {output_file}")
        print("-" * 50)
        
        if not self.tts:
            print("❌ No hay modelo cargado")
            return False
        
        success = False
        
        try:
            if self.model_loaded:
                print("🎨 Usando modelo personalizado...")
                # Modelo personalizado - solo puede generar en el idioma entrenado
                self.tts.tts_to_file(text=text, file_path=output_file)
                print("✅ Generado con modelo personalizado")
                success = True
                
            else:
                print("🎯 Usando modelo de referencia...")
                
                # Método 1: Parámetro language explícito
                print(f"🔧 Método 1: Forzando language='{target_language}'")
                try:
                    self.tts.tts_to_file(
                        text=text,
                        speaker_wav=str(self.reference_audio),
                        file_path=output_file,
                        language=target_language
                    )
                    print("✅ Método 1 exitoso")
                    success = True
                except Exception as e:
                    print(f"❌ Método 1 falló: {e}")
                
                # Método 2: Si falló, intentar con configuración del synthesizer
                if not success:
                    print(f"🔧 Método 2: Configurando synthesizer directamente")
                    try:
                        if hasattr(self.tts, 'synthesizer'):
                            if hasattr(self.tts.synthesizer, 'tts_config'):
                                # Forzar idioma en la configuración
                                self.tts.synthesizer.tts_config.language = target_language
                            
                            if hasattr(self.tts.synthesizer, 'tts_model'):
                                # Configurar idioma en el modelo si es posible
                                model = self.tts.synthesizer.tts_model
                                if hasattr(model, 'language_manager'):
                                    print(f"🔧 Configurando language_manager para {target_language}")
                        
                        self.tts.tts_to_file(
                            text=text,
                            speaker_wav=str(self.reference_audio),
                            file_path=output_file,
                            language=target_language
                        )
                        print("✅ Método 2 exitoso")
                        success = True
                    except Exception as e:
                        print(f"❌ Método 2 falló: {e}")
                
                # Método 3: Recargar modelo con idioma específico
                if not success:
                    print(f"🔧 Método 3: Recargando modelo para {target_language}")
                    try:
                        # Recargar TTS especificando idioma
                        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                        
                        # Intentar configurar el idioma por defecto
                        if hasattr(self.tts, 'synthesizer'):
                            synthesizer = self.tts.synthesizer
                            if hasattr(synthesizer, 'tts_config'):
                                synthesizer.tts_config.language = target_language
                        
                        self.tts.tts_to_file(
                            text=text,
                            speaker_wav=str(self.reference_audio),
                            file_path=output_file,
                            language=target_language
                        )
                        print("✅ Método 3 exitoso")
                        success = True
                    except Exception as e:
                        print(f"❌ Método 3 falló: {e}")
        
        except Exception as e:
            print(f"❌ Error general: {e}")
            import traceback
            traceback.print_exc()
        
        if success:
            print(f"\n🎉 Audio generado exitosamente: {output_file}")
            
            # Verificar el archivo generado
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"📊 Tamaño del archivo: {file_size} bytes")
                
                try:
                    import librosa
                    duration = librosa.get_duration(path=output_file)
                    print(f"⏱️ Duración: {duration:.2f}s")
                except:
                    pass
            
            return True
        else:
            print(f"\n❌ No se pudo generar el audio")
            return False
    
    def run_comprehensive_test(self):
        """Ejecuta una prueba comprehensiva"""
        print("\n🧪 PRUEBA COMPREHENSIVA")
        print("=" * 50)
        
        # Diagnósticos
        self.system_diagnosis()
        detected_lang = self.model_diagnosis()
        
        # Cargar modelo
        if not self.load_model_with_diagnosis():
            print("❌ No se pudo cargar ningún modelo")
            return False
        
        # Textos de prueba
        test_cases = [
            ("en", "Hello, this is a test in English."),
            ("es", "Hola, esta es una prueba en español."),
        ]
        
        # Si se detectó un idioma específico, probarlo primero
        if detected_lang:
            target_text = {
                'en': "Hello, this is my English voice clone.",
                'es': "Hola, esta es mi clon de voz en español."
            }.get(detected_lang, "Test voice clone.")
            
            test_cases.insert(0, (detected_lang, target_text))
        
        # Ejecutar pruebas
        for lang, text in test_cases:
            print(f"\n{'='*20} PRUEBA {lang.upper()} {'='*20}")
            output_file = f"test_diagnostic_{lang}.wav"
            self.generate_with_forced_language(text, output_file, lang)
        
        print(f"\n🎉 Prueba comprehensiva completada!")
        print("🔊 Reproduce los archivos test_diagnostic_*.wav")
        print("📋 Revisa los diagnósticos arriba para identificar problemas")

def main():
    parser = argparse.ArgumentParser(description="Generador con diagnóstico completo")
    parser.add_argument('--test', action='store_true', help='Ejecutar prueba comprehensiva')
    parser.add_argument('--lang', default='en', help='Idioma objetivo (en, es, etc.)')
    parser.add_argument('text', nargs='?', help='Texto a generar')
    parser.add_argument('output', nargs='?', default='diagnostic_output.wav', help='Archivo de salida')
    
    args = parser.parse_args()
    
    generator = DiagnosticVoiceGenerator()
    
    if args.test:
        generator.run_comprehensive_test()
    elif args.text:
        # Diagnóstico rápido y generación
        generator.system_diagnosis()
        generator.model_diagnosis()
        
        if generator.load_model_with_diagnosis():
            generator.generate_with_forced_language(args.text, args.output, args.lang)
        else:
            print("❌ No se pudo cargar modelo")
    else:
        print("Uso:")
        print("  python diagnostic_generator.py --test")
        print("  python diagnostic_generator.py 'Hello world' output.wav --lang en")

if __name__ == "__main__":
    main()