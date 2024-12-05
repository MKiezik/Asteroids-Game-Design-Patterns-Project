# Użyte wzorce projektowe:


Singleton:
Wzorzec obejmuje klasy:
- Game (klasa zewnętrzna)
- __Game (klasa wewnętrzna – singleton właściwy)
Cel: Singleton użyty w celu ograniczenia tworzenia obiektów głównej klasy aplikacji. Tylko jedne okno gry będzie mogło być aktywne w danym momencie. Singleton jest wzorcem umożliwiającym proste wprowadzenie takiego ograniczenia. Wiecej o singletonie specyficznie dla pythona w punkcie 3. o rozwiązaniu specyficznym dla technologii.
Lokalizacja wzorca w kodzie:
Klasa “Game” 505
Klasa “__Game” 519
Linia definicji: 624
Linia użycia I sprawdzenie referencji: 627-631




Polecenie (Command): Wzorzec obejmuje klasy:

- Action (Command) 201
- MoveRight, MoveLeft, Shoot (ConcreteCommand) 209 - InputHandler (Invoker) 236
- CommandReceiver (Receiver) 257
- Player (Client) 113
Cel: Polecenie został użyty w celu zarządzania nad poleceniami wydawanymi przez użytkownika alipkacji. Polecenia te są dodawane do listy, aby zapewnić ich poprawne wykonanie w kolejności I żadnego nie pominąć.
Lokalizacja wzorca w kodzie:
Linia definicji:
- Action (Command) 201
- MoveRight, MoveLeft, Shoot (ConcreteCommand) 209 - InputHandler (Invoker) 235
- CommandReceiver (Receiver) 257
Linia użycia:
- Action (Command) 201
- MoveRightCommand 118 MoveLeftCommand 119 ShootCommand 120
- InputHandler (Invoker) 532, 150, - CommandReceiver 117
W ramach rozbudowy programu będzie można dodać nowe klawisze używane przez gracza I sprawdzanie poprawności ich wykonania


Dekorator (Decorator): Wzorzec obejmuje klasy:
Linia definicji:
- PowerupObject 385 - PowerupType 405
- Powerup 423
- RestoreShield 451
- UpgradeBullet 466 Linia użycia:
- PowerupObject 573 I 575 - PowerupType
- Powerup 423
- RestoreShield 451
- UpgradeBullet 466
Metody dekorowane:
- get_speedy
- get_center
- get_power_type Cel:
Dekorator został użyty w celu implementacji bonusów dla gracza. Na ten moment są dostępne tylko 2 bonusy, ale wraz z rozbudową aplikacji będzie można w wygodny sposób dodawać kolejne dzięki wzorcowi. Dekorowane metody użyte są, aby przekazać parametry w wywołaniu w instancji klasy „Game”. Metody get_center() i get_power_type ma za zadanie przekazać parametr podany w wywołaniu w instancji klasy Game, aby ostatni dekorowany obiekt był obiektem z klasy pygame.sprite.Sprite, Metoda get_speedy ma na celu w zależności który obiekt bonusu dekoruje wybrać prędkość z jaką ma się poruszać bonus.
W ramach rozbudowy programu będzie można dodawać z łatwością kolejne bonusy dodając tylko klasę I losując nowy power_type




Strategia (Strategy): Wzorzec obejmuje klasy:
Cel:
Kontekstem strategii jest Asteroida.
Celem użycia wzorca jest inny sposób poruszania/prędkości asteroidy w zależności od użytej strategii. Klasy wzorca są zaimplementowane, ale jedyne co robią to wypisują nazwę danej strategii bez wykonywania żadnej znaczącej dla aplikacji funkcjonalności
Lokalizacja wzorca w kodzie:
Linia definicji:
Strategy 345
XShiftStrategy 353 StraightAtPlayerStrategy 359 RotationStrategy 365
Linia użycia:
funkcja new_asteroid() 271 oraz 296 I 312
W ramach rozbudowy programu będzie można zmieniać poruszanie danych obiektów asteroid
