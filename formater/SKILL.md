---
name: formater
description: >-
  Formats a Markdown relatório into the VERT Analytics Word template, with or
  without the cover page. Maps Markdown headings to the template heading
  styles (heading 1 through heading 9) and keeps the template header, footer,
  margins, and cover. Use only when the user explicitly invokes this skill
  by name.
argument-hint: "ruta.md con cover | sin cover"
disable-model-invocation: true
---

# Formatear un relatório en el templado

Este skill solo corre cuando la persona lo invoca por nombre. No lo uses porque haya un Markdown o un `.docx` cerca.

Toma un Markdown y lo vuelca en el templado de VERT Analytics. El script conserva la portada (si corresponde), el encabezado, el pie, los márgenes y los estilos. No armes el `.docx` a mano: el script ya resuelve la diferencia entre los dos archivos.

## Portada

Si no dijo con cover o sin cover, preguntá antes de generar.

- **Con cover.** `assets/template.docx`. La primera página queda solo con la imagen de portada. El texto empieza en la página siguiente, ya con el encabezado y el pie del templado. El color de los títulos es azul oscuro y no se lee sobre la portada, por eso el título no va encima de esa imagen.
- **Sin cover.** `assets/template_no_cover.docx`. El texto empieza en la primera página, con el mismo encabezado y pie. El archivo trae un salto de página vacío: el script lo quita.

## Títulos

El nivel del Markdown es el nivel del estilo. El nombre del estilo es `heading 1` … `heading 9`. No uses el styleId: en un templado es `Heading1` y en el otro `Ttulo1`, pero el nombre visible es el mismo.

| Markdown | Estilo |
| --- | --- |
| `#` | heading 1 |
| `##` | heading 2 |
| `###` | heading 3 |
| `####` | heading 4 |
| `#####` … `#########` | heading 5 … heading 9 |

Negrita, cursiva, código y enlaces que estén dentro de un título se conservan. Una línea `---` no genera nada: el corte ya lo dan los títulos.

## Procedimiento

1. Confirmá el `.md` y si va con cover o sin cover.
2. Ejecutá el script desde cualquier directorio. Las rutas de entrada y salida pueden ser absolutas.

```bash
python3 "<carpeta-de-este-skill>/scripts/format_relatorio.py" "<relatorio.md>" --cover -o "<salida.docx>"
python3 "<carpeta-de-este-skill>/scripts/format_relatorio.py" "<relatorio.md>" --no-cover -o "<salida.docx>"
```

3. Mostrá la ruta del `.docx`, cuántos títulos quedaron de cada nivel, y las imágenes que no se encontraron.
4. No cambies encabezados, pies, márgenes ni la imagen de portada.

## Qué más se convierte

- Párrafos, con el espaciado del templado.
- Listas numeradas y con viñeta. Cada lista reinicia en 1.
- Tablas. Si la fila de encabezado tiene texto, queda en el azul de los títulos, con letra blanca. Una fila de encabezado vacía no se imprime.
- Imágenes cuya ruta exista junto al Markdown. Si el archivo no está, queda el epígrafe en cursiva y la nota `imagem não encontrada`.
- Bloques de código.

Las imágenes `http` no se descargan.
