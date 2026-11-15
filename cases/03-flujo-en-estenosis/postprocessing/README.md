# Sondas opcionales

Copiar el contenido de [probes.function](probes.function) dentro del bloque `functions { ... }` de system/controlDict de la corrida, antes de resolver. Registra U y p. Editar probeLocations para mover los puntos (metros).

Puntos en x=20, 50 y 80 µm, y=5 µm, z=0.5 µm. Las diferencias de presión son puntuales, no promedios de sección. Los registros de simpleFoam son iteraciones; los de pimpleFoam, tiempos físicos. Las sondas no están activadas por defecto.
