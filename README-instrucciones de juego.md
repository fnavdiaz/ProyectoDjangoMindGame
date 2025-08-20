# Juego de Deducción Web

## Disclaimer

Este desarrollo ha tenido como objetivo con Django. No esta probado en un entorno real y aún no tengo muy claro si es funcional o divertido. Esta basado en un capitulo de la serie de Netflix Alice in borderline.

## Como empezar a jugar

Para este juego se deben ser al menos 3 personas (Aunque, a falta de probarlo, se cree que a más mejor). Necesitaras:

- Un ordenador central, donde se verá la pantalla del master. (El usuario/contraseña es admin/admin)
- Un smarthpone o dispositivo capaz de conectarse a un navegador a traves del wifi por cada jugador.

Los jugadores se registrarán y aparecerán en la pantalla de master. Cuando esten todos, desde el ordenador master se pulsara iniciar juego y se determinara la duración de cada ronda.

## Objetivo del juego

En la pantalla de cada jugador aparecera su nombre en grande junto a una interrogación. También el nombre de los otros jugadores abajo, ordenados alfabéticamente. El sistema selecciona a cada uno de los jugadores un simbolo aleatorio de entre los cuatro palos de póker ['♠', '♥', '♦', '♣']. Todo el mundo sabe el símbolo asignado de todo el mundo, excepto el propio. 

El jugador debe pulsar en la interrogación junto a su nombre y elegir el símbolo que cree que tiene asignado, si al finalizar la ronda no ha elegido o lo ha hecho incorrectamente será eliminado. Para averiguarlo cualquier estrategia es válida excepto mirar los moviles de los otros jugadores. La idea es que exista una comunicación continua y se establezca una dinámica de confianza/traición.

## Normas del juego

- No se pueden ver las pantallas de otros jugadores.
- Cada vez que un jugador te de información sobre tu simbolo, deberás apuntarlo. Para esto, en tu pantalla de jugador cuentas con un bocadillo para cada uno de los otros jugadores, aquí deberás seleccionar el símbolo que el jugador en cuestión te haya dicho, independientemente de si crees que te esta mintiendo o diciendo la verdad. 
- Las verdades o mentiras se irán contabilizando según avance la ronda. Si una ronda has dicho mas verdades que mentiras aumentaras tu karma en 1. Si por el contreario has mentido mas veces que dicho la verdad, tu karma disminuira en 1. Si tu karma llega a 0 o a 6 **pierdes automaticamente**. 
- El karma de los jugadores no es información conocida excepto por el código de colores y no se puede revelar. Si un jugador tiene karma menor o igual que 3, verás una bolita verde al lado de su nombre, si tiene karma 4 o 5 veras una bolita roja. De esta manera puedes saber cual es la probabilidad aproximada de que la persona en cuestión te mienta o te diga la verdad. (Si es rojo, significa que esta a punto de llegar a los 6 puntos, probablemente te mienta, y viceversa.)

## Condiciones de victoria.

Para resolver el juego deben de quedar dos o menos personas vivas. Los posibles resultados son:

- Todos los jugadores eliminados: No gana nadie.
- Todos los jugadores eliminados menos uno: Gana el jugador que no ha sido eliminado.
- Todos los jugadores eliminados menos dos:
   - Ganará el jugador que más interacciones haya tenido a lo largo del juego. El número de interacciones es la suma de las mentiras y verdades contadas.
   - En caso de que tengan el mismo número de interacciones, ganará quien haya contado más mentiras.
   - En caso de que tengan el mismo número de interacciones y mentiras se declarará un empate.

