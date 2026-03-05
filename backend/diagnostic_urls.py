from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.conf import settings
import sys

def diagnose_urls():
    """Diagnostica las URLs disponibles en el proyecto"""
    
    print("🔍 DIAGNÓSTICO DE URLs DISPONIBLES")
    print("=" * 50)
    
    resolver = get_resolver()
    
    def extract_urls(urlpatterns, namespace='', prefix=''):
        urls = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                # Es un include() con namespace
                new_namespace = f"{namespace}:{pattern.namespace}" if pattern.namespace else namespace
                new_prefix = prefix + str(pattern.pattern)
                urls.extend(extract_urls(pattern.url_patterns, new_namespace, new_prefix))
            else:
                # Es una URL individual
                url_name = f"{namespace}:{pattern.name}" if pattern.name else "unnamed"
                full_pattern = prefix + str(pattern.pattern)
                urls.append((full_pattern, url_name))
        return urls
    
    all_urls = extract_urls(resolver.url_patterns)
    
    # Filtrar URLs relevantes
    relevant_urls = [url for url in all_urls if 'archivos' in url[0].lower()]
    
    print("\n📁 URLs RELACIONADAS CON ARCHIVOS:")
    print("-" * 40)
    for pattern, name in relevant_urls:
        print(f"  {pattern} → {name}")
    
    print("\n🔍 BUSCANDO ESPECÍFICAMENTE:")
    print("-" * 40)
    
    target_urls = [
        'preoperacion/archivos-pre/por-municipio',
        'postoperacion/archivos/por-municipio'
    ]
    
    for target in target_urls:
        found = any(target in url[0] for url in all_urls)
        status = "✅ ENCONTRADA" if found else "❌ NO ENCONTRADA"
        print(f"  {target}: {status}")
    
    # Verificar ViewSets registrados
    print("\n📊 INFORMACIÓN DE ViewSets:")
    print("-" * 40)
    
    try:
        from preoperacion.views import ListaArchivosPreViewSet
        methods = [method for method in dir(ListaArchivosPreViewSet) if not method.startswith('_')]
        print(f"  ListaArchivosPreViewSet métodos: {methods}")
        
        # Verificar si por_municipio existe
        has_por_municipio = hasattr(ListaArchivosPreViewSet, 'por_municipio')
        print(f"  ¿Tiene método por_municipio? {'✅ SÍ' if has_por_municipio else '❌ NO'}")
        
    except Exception as e:
        print(f"  Error importando ListaArchivosPreViewSet: {e}")
    
    try:
        from postoperacion.views import ArchivosPostViewSet
        methods = [method for method in dir(ArchivosPostViewSet) if not method.startswith('_')]
        print(f"  ArchivosPostViewSet métodos: {methods}")
        
        # Verificar si por_municipio existe
        has_por_municipio = hasattr(ArchivosPostViewSet, 'por_municipio')
        print(f"  ¿Tiene método por_municipio? {'✅ SÍ' if has_por_municipio else '❌ NO'}")
        
    except Exception as e:
        print(f"  Error importando ArchivosPostViewSet: {e}")

if __name__ == "__main__":
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    diagnose_urls()