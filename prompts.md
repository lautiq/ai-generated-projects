# prompts.md

## Prompt 1 — Generación inicial de la calculadora maligna
Se generó la versión base de la calculadora con comportamientos frustrantes y UI caótica.

```text
Generar un index.html de una calculadora maligna.
Números desordenados aleatoriamente.
El igual tiene delay aleatorio.
Backspace agrega números.
Los botones cambian tamaño.
El resultado aparece invertido.
La calculadora tiene “confirmación” para cada operación.
Funcional, pero diseñado para frustrar al usuario.
```

---

## Prompt 2 — Cambio aleatorio de color en botones
Se agregó variación aleatoria de color a los botones numéricos durante las animaciones periódicas.

```text
En el setInterval que modifica tamaño/rotación de botones, agregar cambio aleatorio de btn.style.color para todos los botones numéricos.
```

---

## Prompt 3 — Resultado en rojo
Se modificó la pantalla para que el resultado final aparezca en rojo luego de presionar "=".

```text
Modificar updateScreen() para que el resultado mostrado tras presionar = aparezca en color rojo (screen.style.color = 'red'). Mantener color normal mientras se escribe la expresión.
```

---

## Conversación completa

https://chatgpt.com/share/69fbe663-7134-83e9-b035-7c9eef68756c