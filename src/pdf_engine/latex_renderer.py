import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader

TEMPLATE_NAME = "reporte_flexion.tex"

def render_report(title: str, data: Dict[str, Any], output_path: str = "reporte_diseño_flexion.pdf") -> str:
    """Renderiza una plantilla .tex y compila un PDF usando MiKTeX portátil."""

    # Ruta base segura al proyecto (sube 2 niveles desde /pdf_engine/)
    base_dir = Path(__file__).resolve().parents[2]
    # Intenta usar la versión portátil incluida solo en Windows
    pdflatex_path = base_dir / "latex_runtime" / "texmfs" / "install" / "miktex" / "bin" / "x64" / "pdflatex.exe"

    if not pdflatex_path.exists() or not pdflatex_path.is_file():
        # Si no existe, buscar pdflatex en el PATH del sistema
        system_pdflatex = shutil.which("pdflatex")
        if system_pdflatex:
            pdflatex_path = Path(system_pdflatex)
        else:
            raise FileNotFoundError(
                "No se encontró pdflatex. Instala una distribución LaTeX o coloca pdflatex en el PATH."
            )

    # Preparar entorno Jinja2
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
        autoescape=False,
    )
    template = env.get_template(TEMPLATE_NAME)
    context = dict(data)
    context.setdefault("formula_images", [])
    context["title"] = title.upper()

    # Convertir rutas de imagen con barra normal para compatibilidad con LaTeX
    for key in [
        "section_img", "peralte_img", "b1_img", "pbal_img",
        "rhobal_img", "pmax_img", "asmin_img", "asmax_img"
    ]:
        value = context.get(key)
        if value and isinstance(value, str) and value.strip():
            normalized = value.replace("\\", "/")
            context[key] = normalized
        else:
            context[key] = None

    # Renderizar contenido .tex con Jinja2
    tex_source = template.render(context)

    # Guardar .tex generado para depuración
    debug_tex = base_dir / "debug_report.tex"
    with open(debug_tex, "w", encoding="utf-8") as f_debug:
        f_debug.write(tex_source)

    # Compilar con pdflatex en carpeta temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = os.path.join(tmpdir, "report.tex")
        with open(tex_file, "w", encoding="utf-8") as fh:
            fh.write(tex_source)

        # Copiar imágenes necesarias a la carpeta temporal
        for key in [
            "section_img", "peralte_img", "b1_img", "pbal_img",
            "rhobal_img", "pmax_img", "asmin_img", "asmax_img"
        ]:
            src_path = context.get(key)
            if src_path and os.path.isfile(src_path):
                dst_path = os.path.join(tmpdir, os.path.basename(src_path))
                shutil.copy(src_path, dst_path)
                context[key] = os.path.basename(src_path)  # actualizar a nombre base para LaTeX

        # Volver a renderizar con las rutas corregidas
        tex_source = template.render(context)
        with open(tex_file, "w", encoding="utf-8") as fh:
            fh.write(tex_source)

        try:
            subprocess.run(
                [str(pdflatex_path), "-interaction=nonstopmode", tex_file],
                cwd=tmpdir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as exc:
            raise RuntimeError("La compilación del PDF falló. Revisa el contenido del archivo debug_report.tex.") from exc

        # Mover PDF al destino final
        pdf_src = os.path.join(tmpdir, "report.pdf")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        shutil.move(pdf_src, output_path)

    return output_path
