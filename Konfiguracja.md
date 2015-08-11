# Dyrektywy #

  * rozmiar okna gry
  * wszelkie potrzebne ścieżki


# API #

```
class Config
```

```
  init(config_file = 'conf')
```

> Wczytuje konfigurację z pliku. Z konieczności nazwa pliku konfiguracyjnego musi być zawarta w kodzie.

```
  get(section, option)
```

> Zwraca treść pojedynczej dyrektywy (opcji).


# Implementacja #

Wykorzystuje wbudowany moduł `ConfigParser`.





