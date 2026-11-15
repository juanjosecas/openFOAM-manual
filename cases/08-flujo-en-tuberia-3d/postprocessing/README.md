# Sondas opcionales

Copiar el contenido de [probes.function](probes.function) dentro del bloque `functions { ... }` de system/controlDict de la corrida, antes de resolver. Registra U y p. Editar probeLocations para mover los puntos (metros).

Puntos sobre el eje x; permiten comparar la respuesta pulsátil a lo largo de la tubería. Los registros de simpleFoam son iteraciones; los de pimpleFoam, tiempos físicos. Las sondas no están activadas por defecto.
