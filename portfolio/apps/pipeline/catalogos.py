"""
Catálogos cerrados del pipeline colaborativo.

Se prefieren listas finitas y verificables sobre texto libre: así el muro de
deploys se mantiene limpio y los datos son agregables (por país, por tipo de
commit) sin tener que normalizar variantes escritas a mano.
"""

# Tipos de commit según Conventional Commits, con el subconjunto que de
# verdad usa la gente. El orden es el de frecuencia real de uso.
TIPOS_COMMIT = [
    ("feat", "feat", "Una funcionalidad nueva"),
    ("fix", "fix", "Corrección de un error"),
    ("docs", "docs", "Documentación"),
    ("refactor", "refactor", "Reescritura sin cambiar comportamiento"),
    ("test", "test", "Pruebas"),
    ("chore", "chore", "Mantenimiento o tareas varias"),
    ("perf", "perf", "Mejora de rendimiento"),
    ("style", "style", "Formato y estilo"),
]

TIPOS_VALIDOS = {clave for clave, _, _ in TIPOS_COMMIT}
TIPO_POR_DEFECTO = "feat"

# Países con bandera. Lista amplia pero cerrada: cubre América, Europa y los
# principales del resto del mundo, con una salida para el resto de casos.
PAISES = [
    ("", "— Prefiero no decirlo —"),
    ("Colombia", "🇨🇴 Colombia"),
    ("España", "🇪🇸 España"),
    ("México", "🇲🇽 México"),
    ("Argentina", "🇦🇷 Argentina"),
    ("Chile", "🇨🇱 Chile"),
    ("Perú", "🇵🇪 Perú"),
    ("Ecuador", "🇪🇨 Ecuador"),
    ("Venezuela", "🇻🇪 Venezuela"),
    ("Uruguay", "🇺🇾 Uruguay"),
    ("Paraguay", "🇵🇾 Paraguay"),
    ("Bolivia", "🇧🇴 Bolivia"),
    ("Costa Rica", "🇨🇷 Costa Rica"),
    ("Panamá", "🇵🇦 Panamá"),
    ("Guatemala", "🇬🇹 Guatemala"),
    ("Honduras", "🇭🇳 Honduras"),
    ("El Salvador", "🇸🇻 El Salvador"),
    ("Nicaragua", "🇳🇮 Nicaragua"),
    ("Cuba", "🇨🇺 Cuba"),
    ("República Dominicana", "🇩🇴 República Dominicana"),
    ("Puerto Rico", "🇵🇷 Puerto Rico"),
    ("Brasil", "🇧🇷 Brasil"),
    ("Estados Unidos", "🇺🇸 Estados Unidos"),
    ("Canadá", "🇨🇦 Canadá"),
    ("Portugal", "🇵🇹 Portugal"),
    ("Francia", "🇫🇷 Francia"),
    ("Italia", "🇮🇹 Italia"),
    ("Alemania", "🇩🇪 Alemania"),
    ("Reino Unido", "🇬🇧 Reino Unido"),
    ("Irlanda", "🇮🇪 Irlanda"),
    ("Países Bajos", "🇳🇱 Países Bajos"),
    ("Bélgica", "🇧🇪 Bélgica"),
    ("Suiza", "🇨🇭 Suiza"),
    ("Austria", "🇦🇹 Austria"),
    ("Polonia", "🇵🇱 Polonia"),
    ("Suecia", "🇸🇪 Suecia"),
    ("Noruega", "🇳🇴 Noruega"),
    ("Dinamarca", "🇩🇰 Dinamarca"),
    ("Finlandia", "🇫🇮 Finlandia"),
    ("Rumanía", "🇷🇴 Rumanía"),
    ("Grecia", "🇬🇷 Grecia"),
    ("Marruecos", "🇲🇦 Marruecos"),
    ("Sudáfrica", "🇿🇦 Sudáfrica"),
    ("Nigeria", "🇳🇬 Nigeria"),
    ("Egipto", "🇪🇬 Egipto"),
    ("India", "🇮🇳 India"),
    ("China", "🇨🇳 China"),
    ("Japón", "🇯🇵 Japón"),
    ("Corea del Sur", "🇰🇷 Corea del Sur"),
    ("Filipinas", "🇵🇭 Filipinas"),
    ("Indonesia", "🇮🇩 Indonesia"),
    ("Australia", "🇦🇺 Australia"),
    ("Nueva Zelanda", "🇳🇿 Nueva Zelanda"),
    ("Otro país", "🌍 Otro país"),
]

PAISES_VALIDOS = {valor for valor, _ in PAISES if valor}

# Bandera por país, para pintarla en el muro sin repetir la tabla
BANDERAS = {valor: etiqueta.split(" ", 1)[0] for valor, etiqueta in PAISES if valor}
