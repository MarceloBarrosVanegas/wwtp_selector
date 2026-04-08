#!/usr/bin/env python3
import re

with open('latex_unidades/cloro.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar el método generar_esquema_matplotlib y reemplazarlo completamente
old_method = '''    def generar_esquema_matplotlib(self, output_dir=None):
        """Genera PNG de la camara de contacto con cloro en planta y seccion.
        
        Returns:
            str: Path del archivo generado, o None si falla.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print("[WARNING] PIL no disponible, figura no generada")
            return None

        def cargar_fuente(nombre, tamano):
            ruta = os.path.join(os.environ.get('WINDIR', r'C:\\Windows'), 'Fonts', nombre)
            try:
                return ImageFont.truetype(ruta, tamano)
            except OSError:
                return ImageFont.load_default()
        
        try:

        def texto_centrado(draw, xy, texto, fuente, fill=(35, 35, 35)):'''

# Buscar el inicio del método
start_idx = content.find('    def generar_esquema_matplotlib(self, output_dir=None):')
if start_idx == -1:
    print("No se encontró el método")
    exit(1)

# Buscar el final (inicio de generar_descripcion)
end_marker = '    def generar_descripcion(self) -> str:'
end_idx = content.find(end_marker, start_idx)
if end_idx == -1:
    print("No se encontró el final del método")
    exit(1)

# Extraer el método antiguo para verificar
old_method_full = content[start_idx:end_idx]
print(f"Método encontrado, longitud: {len(old_method_full)} chars")

# Nuevo método
new_method = '''    def generar_esquema_matplotlib(self, output_dir=None):
        """Genera PNG de la camara de contacto con cloro en planta y seccion.
        
        Returns:
            str: Path del archivo generado, o None si falla.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            c = self.datos
            if output_dir is None:
                output_dir = os.path.join(_base_dir, 'resultados', 'figuras')
            os.makedirs(output_dir, exist_ok=True)

            def cargar_fuente(nombre, tamano):
                ruta = os.path.join(os.environ.get('WINDIR', r'C:\\\\Windows'), 'Fonts', nombre)
                try:
                    return ImageFont.truetype(ruta, tamano)
                except OSError:
                    return ImageFont.load_default()
            
            def texto_centrado(draw, xy, texto, fuente, fill=(35, 35, 35)):
                bbox = draw.textbbox((0, 0), texto, font=fuente)
                ancho = bbox[2] - bbox[0]
                alto = bbox[3] - bbox[1]
                draw.text((xy[0] - ancho / 2, xy[1] - alto / 2), texto, font=fuente, fill=fill)

            def flecha(draw, p0, p1, fill, width=5):
                draw.line([p0, p1], fill=fill, width=width)
                dx = p1[0] - p0[0]
                dy = p1[1] - p0[1]
                longitud = max((dx * dx + dy * dy) ** 0.5, 1.0)
                ux = dx / longitud
                uy = dy / longitud
                px = -uy
                py = ux
                tam = 16
                punta = [
                    p1,
                    (p1[0] - ux * tam + px * tam * 0.55, p1[1] - uy * tam + py * tam * 0.55),
                    (p1[0] - ux * tam - px * tam * 0.55, p1[1] - uy * tam - py * tam * 0.55),
                ]
                draw.polygon(punta, fill=fill)
            
            # Dimensiones
            largo = c['largo_m']
            ancho_total = c['ancho_m']
            ancho_canal = c['ancho_canal_m']
            n = int(c['n_canales_serpentin'])
            espesor_bafle = c['espesor_bafle_m']
            h_util = c['h_tanque_m']
            h_total = c['h_total_m']
            h_bordo = h_total - h_util

            img = Image.new('RGB', (1800, 1120), 'white')
            draw = ImageDraw.Draw(img)
            f_titulo = cargar_fuente('arialbd.ttf', 36)
            f_subtitulo = cargar_fuente('arialbd.ttf', 28)
            f_texto = cargar_fuente('arial.ttf', 24)
            f_texto_bold = cargar_fuente('arialbd.ttf', 24)
            f_peq = cargar_fuente('arial.ttf', 21)

            c_muro = (85, 85, 85)
            c_concreto = (248, 248, 248)
            c_agua = (219, 238, 248)
            c_bafle = (144, 164, 174)
            c_bafle_borde = (96, 125, 139)
            c_entrada = (46, 125, 50)
            c_salida = (21, 101, 192)
            c_cloro = (249, 168, 37)
            c_texto = (35, 35, 35)

            draw.text((70, 35), 'Camara de contacto de cloracion tipo culebrin', font=f_titulo, fill=c_texto)
            draw.text((70, 82), f'{n} pasos | recorrido = {c["longitud_recorrido_m"]:.1f} m | relacion recorrido/ancho = {c["relacion_recorrido_ancho"]:.1f}:1',
                      font=f_texto, fill=(70, 70, 70))

            x0, y0, Lp, Wp, margen = 210, 180, 1120, 465, 28
            canal_h = (Wp - 2 * margen) / n

            draw.text((x0, y0 - 55), 'Vista en planta', font=f_subtitulo, fill=c_texto)
            draw.rounded_rectangle((x0, y0, x0 + Lp, y0 + Wp), radius=16,
                                   fill=c_concreto, outline=c_muro, width=5)
            draw.rounded_rectangle((x0 + margen, y0 + margen, x0 + Lp - margen, y0 + Wp - margen),
                                   radius=10, fill=c_agua, outline=(180, 205, 220), width=2)

            gap = 120
            baffle_h = max(12, int(espesor_bafle / max(ancho_canal, 0.01) * canal_h * 0.75))
            for i in range(1, n):
                y_b = int(y0 + margen + i * canal_h)
                if i % 2 == 1:
                    x_a, x_b = x0 + margen, x0 + Lp - margen - gap
                else:
                    x_a, x_b = x0 + margen + gap, x0 + Lp - margen
                draw.rectangle((x_a, y_b - baffle_h // 2, x_b, y_b + baffle_h // 2),
                               fill=c_bafle, outline=c_bafle_borde, width=2)

            puntos = []
            for i in range(n):
                y_c = int(y0 + margen + canal_h * (i + 0.5))
                if i % 2 == 0:
                    puntos.append((x0 + margen + 55, y_c))
                    puntos.append((x0 + Lp - margen - 55, y_c))
                else:
                    puntos.append((x0 + Lp - margen - 55, y_c))
                    puntos.append((x0 + margen + 55, y_c))
                if i < n - 1:
                    x_turn = x0 + Lp - margen - 55 if i % 2 == 0 else x0 + margen + 55
                    y_next = int(y0 + margen + canal_h * (i + 1.5))
                    puntos.append((x_turn, y_next))

            for i in range(len(puntos) - 1):
                draw.line((puntos[i], puntos[i + 1]), fill=c_salida, width=6)
            for i in range(1, len(puntos), 3):
                if i < len(puntos):
                    flecha(draw, puntos[i - 1], puntos[i], c_salida, width=6)

            y_in = int(y0 + margen + canal_h * 0.5)
            flecha(draw, (x0 - 140, y_in), (x0 + margen + 45, y_in), c_entrada, width=7)
            draw.text((x0 - 180, y_in - 68), 'Entrada\\nefluente tratado', font=f_peq, fill=c_entrada)
            draw.ellipse((x0 + margen + 65, y_in - 18, x0 + margen + 101, y_in + 18),
                         fill=c_cloro, outline=(120, 90, 0), width=3)
            x_dosis = x0 + margen + 115
            y_dosis = y_in - 86
            draw.rounded_rectangle((x_dosis - 8, y_dosis - 6, x_dosis + 285, y_dosis + 54),
                                   radius=8, fill=(255, 255, 255), outline=(238, 196, 93), width=1)
            draw.text((x_dosis, y_dosis),
                      f'Dosificacion NaOCl\\nDosis = {c["dosis_cloro_mg_L"]:.1f} mg/L',
                      font=f_peq, fill=(109, 76, 0))

            y_out = int(y0 + margen + canal_h * (n - 0.5))
            x_out = x0 + Lp - margen - 55 if (n - 1) % 2 == 0 else x0 + margen + 55
            flecha(draw, (x_out, y_out), (x_out + 150, y_out), c_salida, width=7)
            draw.text((x_out + 160, y_out - 55), 'Salida\\ndesinfectada', font=f_peq, fill=c_salida)

            texto_centrado(draw, (x0 + Lp / 2, y0 + Wp + 36), f'Largo = {largo:.1f} m', f_peq)
            draw.text((x0 - 105, y0 + Wp / 2 - 16), f'Ancho = {ancho_total:.1f} m',
                      font=f_peq, fill=c_texto)

            sx, sy, sw, sh_agua, sh_bordo = 210, 760, 850, 215, 42
            draw.text((sx, sy - 55), 'Seccion transversal', font=f_subtitulo, fill=c_texto)
            draw.rounded_rectangle((sx, sy, sx + sw, sy + sh_agua + sh_bordo), radius=12,
                                   fill=c_concreto, outline=c_muro, width=5)
            draw.rectangle((sx + 25, sy + sh_bordo, sx + sw - 25, sy + sh_bordo + sh_agua - 20),
                           fill=c_agua, outline=(180, 205, 220), width=2)
            draw.line((sx + 25, sy + sh_bordo, sx + sw - 25, sy + sh_bordo),
                      fill=c_salida, width=3)
            for k in range(1, n):
                x_b = int(sx + 25 + k * (sw - 50) / n)
                draw.rectangle((x_b - 5, sy + sh_bordo + 8, x_b + 5, sy + sh_bordo + sh_agua - 30),
                               fill=c_bafle, outline=c_bafle_borde)

            x_txt = sx + sw + 60
            draw.text((x_txt, sy + 35), f'Profundidad util = {h_util:.1f} m', font=f_texto_bold, fill=c_texto)
            draw.text((x_txt, sy + 80), f'Bordo libre = {h_bordo:.2f} m', font=f_texto, fill=c_texto)
            draw.text((x_txt, sy + 125), f'Volumen util = {c["V_contacto_m3"]:.1f} m3', font=f_texto, fill=c_texto)
            draw.text((x_txt, sy + 170), f'TRH adoptado = {c["TRH_adoptado_min"]:.1f} min', font=f_texto, fill=c_texto)
            draw.text((x_txt, sy + 215), f'CT = {c["CT_mg_min_L"]:.1f} mg min/L', font=f_texto, fill=(109, 76, 0))

            fig_path = os.path.join(output_dir, 'Esquema_Camara_Contacto_Cloro.png')
            img.save(fig_path, 'PNG', dpi=(200, 200))
            return fig_path
            
        except ImportError:
            print("[WARNING] PIL no disponible, figura de cloro no generada")
            return None
        except Exception as e:
            print(f"[WARNING] Error generando figura de cloro: {e}")
            return None

'''

# Reemplazar
new_content = content[:start_idx] + new_method + content[end_idx:]
with open('latex_unidades/cloro.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Archivo corregido exitosamente")
