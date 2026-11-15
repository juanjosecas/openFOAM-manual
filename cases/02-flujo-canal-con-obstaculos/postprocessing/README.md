# Sondas opcionales

Copiar el contenido de [probes.function](probes.function) dentro del bloque `functions { ... }` de system/controlDict de la corrida, antes de resolver. Registra U y p. Editar probeLocations para mover los puntos (metros).

Puntos en x=50, 120 y 180 mm, y=10 mm, z=0.5 mm. Comprobar que no intersecten el obstáculo. Los registros de simpleFoam son iteraciones; los de pimpleFoam, tiempos físicos. Las sondas no están activadas por defecto.
