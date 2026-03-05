```
frontend/
│
├── public/               # Archivos públicos estáticos
│   ├── index.html
│   ├── favicon.ico
│   └── assets/           # Imágenes, iconos, etc.
│
├── src/
│   ├── api/              # Servicios para comunicación con el backend
│   │   ├── config.ts     # Configuración de axios
│   │   ├── auth.ts       # Métodos de autenticación
│   │   ├── municipios.ts
│   │   ├──  
│   │   └── ...
│   │
│   ├── components/       # Componentes reutilizables
│   │   ├── common/       # Componentes genéricos (botones, inputs, etc.)
│   │   ├── layout/       # Componentes de estructura
│   │   ├── dashboard/    # Componentes de dashboard
│   │   ├── auth/         # Componentes de autenticación
│   │   └── ...
│   │
│   ├── models/           # Interfaces y tipos de TypeScript
│   │   ├── auth.ts
│   │   ├── municipio.ts
│   │   ├── notificacion.ts
│   │   └── ...
│   │
│   ├── services/         # Lógica de negocio
│   │   ├── auth.service.ts
│   │   ├── municipio.service.ts
│   │   └── ...
│   │
│   ├── store/            # Estado global (puede ser con Context API, Redux, etc.)
│   │   ├── auth/
│   │   ├── notifications/
│   │   └── ...
│   │
│   ├── utils/            # Utilidades y funciones auxiliares
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── ...
│   │
│   ├── pages/            # Páginas principales
│   │   ├── Home.ts
│   │   ├── Login.ts
│   │   ├── DisposicionInfo.ts
│   │   ├── EstadoProducto.ts
│   │   ├── Indicadores.ts
│   │   ├── Geoportal.ts
│   │   ├── MunicipioDetalle.ts
│   │   └── ...
│   │
│   ├── routes/           # Configuración de rutas
│   │   ├── index.ts
│   │   ├── PrivateRoute.ts
│   │   └── ...
│   │
│   ├── styles/           # Estilos globales
│   │   ├── main.css
│   │   ├── variables.css
│   │   └── ...
│   │
│   ├── App.ts            # Componente principal
│   ├── main.ts           # Punto de entrada
│   └── ...
│
├── tsconfig.json         # Configuración de TypeScript
├── package.json
├── vite.config.ts        # Configuración de Vite (o webpack si se prefiere)
├── README.md
└── .gitignore
```