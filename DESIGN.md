# DESIGN.md — Sistema de diseño del portafolio

Fuente única de verdad estética. **Léelo antes de tocar CSS o plantillas.**
Su razón de ser: evitar que el sitio derive hacia la estética genérica que
produce por defecto cualquier generador — el llamado *AI slop*.

---

## 1. Dirección

**"Taller cálido"** — papel artesanal con alma de terminal.
Un ingeniero que trabaja en consola, pero cuyo espacio se siente habitado.

Cozy · minimalista · elegante. Nunca frío, nunca corporativo genérico.

---

## 2. Tokens (definidos en `static/css/portfolio.css`)

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--bg-main` | `#FAF8F5` | `#1A1614` | Fondo general |
| `--section-alt` | `#F5F1EB` | `#221D1A` | Secciones alternas |
| `--card-bg` | `#FFFFFF` | `#262019` | Tarjetas |
| `--primary` | `#8B4513` | `#D9A066` | Marca, títulos |
| `--accent` | `#CD853F` | `#E8B888` | Acentos, líneas |
| `--sage` | `#6B7D5A` | `#9DB088` | Éxito, "en formación" |
| `--ink-strong` | `#2E2A26` | `#F2EAE0` | Texto fuerte |

El modo oscuro es **noche cálida**, jamás negro puro.

### Tipografía
- **Display:** Fraunces (ejes `SOFT 40`, `WONK 1`)
- **Texto:** Karla
- **Técnico:** JetBrains Mono

Prohibidas: Inter, Roboto, Arial, Space Grotesk y fuentes de sistema.

---

## 3. Reglas innegociables

1. **Ningún color de marca ajena.** Nada de logos de Python, Docker, AWS o
   Anthropic: sus paletas destruyen la calidez. Las tecnologías se nombran
   en `--font-mono` con los colores propios del sitio.
2. **Puente con Bootstrap obligatorio.** El azul de fábrica se cuela por
   tres vías distintas, y cada una necesita su propio antídoto:

   | Vía | Ejemplo | Solución |
   |---|---|---|
   | Variables `--bs-*` | `.bg-primary` | Redefinir en `:root` |
   | Variables declaradas en la clase del componente | acordeón, miga de pan | Redefinir **sobre esa misma clase**: `:root` pierde por especificidad |
   | Color fijo dentro de un SVG incrustado | chevron del `.form-select`, checkbox | Reemplazar el `data:` URI entero; ninguna variable lo alcanza |
   | La variante `-rgb` de una variable ya mapeada | `<a>` sin clase usa `--bs-link-color-rgb` | Definir **también** la versión `-rgb`; mapear solo la base no basta |

   Antes de dar por bueno un componente de Bootstrap, míralo en **ambos
   temas**: el azul suele aparecer solo en un estado (activo, marcado,
   deshabilitado, con foco).

   Cuidado también con el orden entre reglas propias: una regla general
   escrita después pisa a una específica anterior con igual peso. Gana con
   un selector más específico, nunca con `!important`.
3. **Nunca `gsap.from({opacity:0})` sin red.** Deja el elemento invisible y
   lo revela con rAF; en una pestaña en segundo plano rAF se congela y el
   contenido no vuelve. Usar `clearProps` y esperar a `visibilitychange`.
4. **Honestidad del contenido.** Lo que está en formación se marca con
   `.badge-learning`. Nada de inflar experiencia.
5. **Solo métricas reales.** El panel de estado lee proceso, git y base de
   datos. Si un dato no se puede verificar, no se publica.

---

## 4. Antipatrones a evitar

Rasgos que delatan una web generada sin criterio, y su antídoto aquí:

| Antipatrón | Qué hacemos |
|---|---|
| Gradiente morado sobre blanco | Paleta terracota/crema cálida |
| Inter + tarjetas iguales en rejilla | Fraunces/Karla + jerarquía real |
| Secciones idénticas en cascada | Ritmo alterno: 6/6 · 7/5 · 8/4 · 4/4/4 · ancho completo |
| Todos los títulos centrados | Se alterna con `.section-head-left` |
| Todo clavado a la rejilla | `.marca-agua` y `.cifra-margen` se salen a propósito |
| Copy vago que vale para cualquiera | Cifras y hechos verificables del CV |
| Iconos de robot / cerebro / red neuronal | Ninguno |
| Imágenes generadas por IA | Foto real y diagramas propios |

### Ritmo vertical actual
```
Hero            6/6 asimétrico + terminal
Cinta           ancho completo, tipográfica
Pipeline        7/5 · centrado (el interactivo va arriba)
Construido      7/5 · encabezado a la izquierda · 1 destacado + 3
Trayectoria     4/8 · timeline
Stack           8/4 · 4/4/4 · ancho completo · 7/5
Credenciales    5/7
Contacto        centrado (contraste de cierre)
```

---

## 5. Movimiento

- `--ease-cozy: cubic-bezier(0.33, 1, 0.68, 1)` para todo lo que se mueve.
- Lenis **solo** con rueda de ratón; el trackpad usa el scroll nativo.
- Todo efecto respeta `prefers-reduced-motion` y degrada a contenido legible.
- Ante la duda: el contenido debe quedar visible aunque el script falle.

---

## 6. Al añadir una sección

1. ¿Qué ritmo tiene la anterior? Usa uno distinto.
2. ¿Todas las tarjetas miden lo mismo? Da jerarquía a una.
3. ¿El título va centrado como el previo? Alterna.
4. ¿El copy serviría para otra persona? Reescríbelo con datos tuyos.
