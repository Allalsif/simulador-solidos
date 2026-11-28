import hmac  # Sirve para comparar contraseñas de forma segura
import streamlit as st
import numpy as np
import sympy as sp
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Simulador 3D - Sólidos de Revolución", layout="wide")


# =====================================================================
# VALIDACIÓN DE USUARIO
# ---------------------------------------------------------------------
# Funcionamiento:
# 1. Los usuarios y contraseñas NO están escritos en este código (el
#    repositorio es público). Se guardan en "Secrets" de Streamlit.
# 2. Si la persona no ha iniciado sesión, solo se muestra el formulario
#    de acceso y la app se detiene (st.stop()) antes de mostrar nada más.
# 3. Si los datos son correctos, se recuerda la sesión mientras la
#    pestaña del navegador siga abierta.
# =====================================================================
def obtener_usuarios():
    """Lee el diccionario de usuarios guardado en Secrets."""
    try:
        return dict(st.secrets["usuarios"])
    except Exception:
        return None  # No hay secrets configurados


def pantalla_login():
    """Muestra el formulario de acceso y valida los datos."""
    st.title("🔒 Acceso al Simulador")
    st.write("Ingrese su usuario y contraseña para continuar.")

    usuarios = obtener_usuarios()
    if usuarios is None:
        st.error("No hay usuarios configurados. Revise la sección Secrets de la app.")
        return

    # Un formulario evita que la app se recargue con cada letra escrita
    with st.form("form_login"):
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        enviar = st.form_submit_button("Ingresar")

    if enviar:
        clave_correcta = usuarios.get(usuario)
        # compare_digest compara las claves de forma segura
        if clave_correcta is not None and hmac.compare_digest(str(clave), str(clave_correcta)):
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()  # Recarga la app ya con la sesión iniciada
        else:
            st.error("Usuario o contraseña incorrectos.")


# Si no hay sesión iniciada: se muestra el login y se detiene todo lo demás
if not st.session_state.get("autenticado", False):
    pantalla_login()
    st.stop()


# --- ENLACES DE GEOGEBRA (uno por método) ---
# La clave debe ser igual al texto de cada opción del selector.
LINKS_GEOGEBRA = {
    "1. Discos (Sistemas - Lente Óptico)": "https://www.geogebra.org/classic/g7ps99qd",
    "2. Arandelas (Electromecánica - Buje Hueco)": "https://www.geogebra.org/classic/m6yqaact",
    "3. Cascarones (Industrial - Molde Empaque)": "https://www.geogebra.org/classic/cxenvsvw",
}

# --- ENLACE DEL VIDEO EXPLICATIVO ---
# Reemplace el "#" por el link del video (entre las comillas).
LINK_VIDEO = "https://unidadestecno-my.sharepoint.com/:v:/g/personal/leandroaestupinan_uts_edu_co/IQCsTQX57Sc-T6Mb-j229o5RAZ59ITAO9IY6AG4s_zuyf3k?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=pMs9H1"

# --- INTERFAZ PRINCIPAL DEL SIMULADOR ---
st.sidebar.title("Panel de Control")

metodo = st.sidebar.selectbox(
    "Seleccione el Método / Caso de Ingeniería:",
    list(LINKS_GEOGEBRA.keys())
)

st.sidebar.markdown("---")
st.sidebar.subheader("Parámetros de Simulación")
n_particiones = st.sidebar.slider("Número de secciones (N):", min_value=5, max_value=60, value=20, step=1)
progreso = st.sidebar.slider("Construcción del sólido (%):", min_value=10, max_value=100, value=100, step=5)
mostrar_malla = st.sidebar.checkbox("Mostrar superficie continua de referencia", value=True)

# Botón que abre el sólido en GeoGebra (el enlace cambia según el método elegido)
st.sidebar.link_button("🌐 Ver en GeoGebra", LINKS_GEOGEBRA[metodo])

# Botón para cerrar sesión: borra la sesión y vuelve a pedir el login
st.sidebar.markdown("---")
st.sidebar.caption(f"Sesión: {st.session_state.get('usuario', '')}")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

# Variable simbólica
x = sp.Symbol('x', real=True)

# --- FUNCIONES DE GENERACIÓN 3D Y CÁLCULO ---
def crear_cilindro_horizontal(x0, x1, r_ext, r_int=0, color='royalblue', opacity=0.7):
    """Dibuja un disco (o arandela si r_int > 0) acostado sobre el eje X."""
    theta = np.linspace(0, 2 * np.pi, 35)
    t = np.array([x0, x1])
    THETA, X = np.meshgrid(theta, t)

    traces = []
    # Pared exterior
    Y_ext = r_ext * np.cos(THETA)
    Z_ext = r_ext * np.sin(THETA)
    traces.append(go.Surface(x=X, y=Y_ext, z=Z_ext, colorscale=[[0, color], [1, color]], showscale=False, opacity=opacity))

    # Pared interior (si es arandela)
    if r_int > 0:
        Y_int = r_int * np.cos(THETA)
        Z_int = r_int * np.sin(THETA)
        traces.append(go.Surface(x=X, y=Y_int, z=Z_int, colorscale=[[0, 'crimson'], [1, 'crimson']], showscale=False, opacity=opacity))

    # Tapas (anillos en x0 y x1)
    r_grid = np.linspace(r_int, r_ext, 2)
    THETA_cap, R_cap = np.meshgrid(theta, r_grid)
    Y_cap = R_cap * np.cos(THETA_cap)
    Z_cap = R_cap * np.sin(THETA_cap)
    for x_pos in [x0, x1]:
        X_cap = np.full_like(Y_cap, x_pos)
        traces.append(go.Surface(x=X_cap, y=Y_cap, z=Z_cap, colorscale=[[0, color], [1, color]], showscale=False, opacity=opacity))

    return traces

def crear_cascaron_vertical(r_int, r_ext, y0, y1, color='seagreen', opacity=0.65):
    """Dibuja un cascarón cilíndrico (tubo) de pared delgada sobre el eje Y."""
    theta = np.linspace(0, 2 * np.pi, 40)
    y_vals = np.array([y0, y1])
    THETA, Y = np.meshgrid(theta, y_vals)

    traces = []
    # Pared exterior e interior
    for r in [r_ext, r_int]:
        if r > 0:
            X = r * np.cos(THETA)
            Z = r * np.sin(THETA)
            traces.append(go.Surface(x=X, y=Y, z=Z, colorscale=[[0, color], [1, color]], showscale=False, opacity=opacity))

    # Tapas superior e inferior
    r_grid = np.linspace(r_int, r_ext, 2)
    THETA_cap, R_cap = np.meshgrid(theta, r_grid)
    X_cap = R_cap * np.cos(THETA_cap)
    Z_cap = R_cap * np.sin(THETA_cap)
    for y_pos in [y0, y1]:
        Y_cap = np.full_like(X_cap, y_pos)
        traces.append(go.Surface(x=X_cap, y=Y_cap, z=Z_cap, colorscale=[[0, color], [1, color]], showscale=False, opacity=opacity))

    return traces

# --- BOTÓN DE VIDEO EXPLICATIVO ---
st.link_button("Video explicativo", LINK_VIDEO)

# --- LÓGICA POR MÉTODO ---
# Cada método: 1) muestra el enunciado, 2) calcula el volumen exacto con SymPy,
# 3) suma las secciones (aproximación) y 4) dibuja cada sección en 3D.
fig = go.Figure()
limite_visible = int(n_particiones * (progreso / 100.0))  # Cuántas secciones se dibujan

if "1. Discos" in metodo:
    st.title("🔵 Método de Discos: Lente Óptico Parabólico")

    with st.container(border=True):
        st.subheader("Contexto y Enunciado del Problema (Ingeniería de Sistemas)")
        st.markdown("""
        **Planteamiento:** En el diseño de hardware para redes de telecomunicaciones de alta velocidad, se requiere fabricar un **concentrador óptico parabólico** encargado de focalizar haces de luz hacia el núcleo de una fibra óptica monomodo. El perfil transversal del lente está delimitado superiormente por la curva $f(x) = \\sqrt{4x}$, el eje $X$ ($y = 0$) y la recta vertical $x = 4$ (medidas en milímetros).

        **Requerimiento:** Determine el volumen exacto de material dieléctrico necesario para moldear la pieza al hacer girar dicha región alrededor del **eje $X$** utilizando el **Método de Discos**, dado que las secciones transversales perpendiculares al eje de giro son discos circulares macizos de radio $R(x) = f(x)$.
        """)

    a, b = 0.0, 4.0
    f_sym = sp.sqrt(4 * x)
    # Volumen exacto: V = π ∫ f(x)² dx
    vol_exacto_sym = sp.pi * sp.integrate(f_sym**2, (x, a, b))
    vol_exacto_num = float(vol_exacto_sym.evalf())

    dx = (b - a) / n_particiones
    vol_aprox = 0.0

    for i in range(n_particiones):
        x_mid = a + (i + 0.5) * dx          # Punto medio de la sección
        r = np.sqrt(4 * x_mid)              # Radio del disco
        vol_aprox += np.pi * (r**2) * dx    # Volumen del disco
        if i < limite_visible:
            fig.add_traces(crear_cilindro_horizontal(a + i*dx, a + (i+1)*dx, r, color='#1f77b4', opacity=0.75))

    if mostrar_malla:
        x_surf = np.linspace(a, b, 50)
        theta_surf = np.linspace(0, 2*np.pi, 40)
        X_s, THETA_s = np.meshgrid(x_surf, theta_surf)
        R_s = np.sqrt(4 * X_s)
        fig.add_trace(go.Surface(x=X_s, y=R_s*np.cos(THETA_s), z=R_s*np.sin(THETA_s), opacity=0.2, showscale=False, colorscale='Blues'))

    formula_latex = r"V = \pi \int_{0}^{4} (\sqrt{4x})^2 \, dx = 32\pi"
    unidades = "mm³"

elif "2. Arandelas" in metodo:
    st.title("🟠 Método de Arandelas: Buje Mecánico Hueco")

    with st.container(border=True):
        st.subheader("Contexto y Enunciado del Problema (Ingeniería Electromecánica)")
        st.markdown("""
        **Planteamiento:** En un sistema de transmisión industrial, se diseña un **buje de acoplamiento hueco** que permite el paso de un eje motriz central de radio constante mientras soporta cargas radiales externas con perfil curvo. La sección transversal del buje está acotada superiormente por $f(x) = \\sqrt{x} + 2$, inferiormente por $g(x) = 2$, y lateralmente por las rectas $x = 0$ y $x = 4$ (medidas en centímetros).

        **Requerimiento:** Calcule el volumen de aleación metálica requerida para mecanizar el buje al rotar la región descrita alrededor del **eje desplazado $y = 1$** mediante el **Método de Arandelas**, identificando el radio exterior $R(x) = f(x) - 1$ y el radio interior de perforación $r(x) = g(x) - 1$.
        """)

    a, b = 0.0, 4.0
    R_sym = (sp.sqrt(x) + 2) - 1   # Radio exterior
    r_sym = 2 - 1                  # Radio interior
    # Volumen exacto: V = π ∫ (R² - r²) dx
    vol_exacto_sym = sp.pi * sp.integrate(R_sym**2 - r_sym**2, (x, a, b))
    vol_exacto_num = float(vol_exacto_sym.evalf())

    dx = (b - a) / n_particiones
    vol_aprox = 0.0

    for i in range(n_particiones):
        x_mid = a + (i + 0.5) * dx
        R_ext = np.sqrt(x_mid) + 1
        r_int = 1.0
        vol_aprox += np.pi * (R_ext**2 - r_int**2) * dx   # Volumen de la arandela
        if i < limite_visible:
            fig.add_traces(crear_cilindro_horizontal(a + i*dx, a + (i+1)*dx, R_ext, r_int, color='#ff7f0e', opacity=0.75))

    if mostrar_malla:
        x_surf = np.linspace(a, b, 50)
        theta_surf = np.linspace(0, 2*np.pi, 40)
        X_s, THETA_s = np.meshgrid(x_surf, theta_surf)
        R_s = np.sqrt(X_s) + 1
        fig.add_trace(go.Surface(x=X_s, y=R_s*np.cos(THETA_s), z=R_s*np.sin(THETA_s), opacity=0.2, showscale=False, colorscale='Oranges'))

    formula_latex = r"V = \pi \int_{0}^{4} \left[ (\sqrt{x}+1)^2 - 1^2 \right] dx = \frac{56\pi}{3}"
    unidades = "cm³"

else:
    st.title("🟢 Método de Cascarones Cilíndricos: Molde de Empaque")

    with st.container(border=True):
        st.subheader("Contexto y Enunciado del Problema (Ingeniería Industrial)")
        st.markdown("""
        **Planteamiento:** En una línea de manufactura de envases termoformados, se diseña un **molde contenedor toroidal abierto** cuya cavidad interna está definida por la región bajo la curva parabólica $f(x) = 4x - x^2$ y el eje $X$ ($y = 0$) en el intervalo $x \\in [0, 4]$ (medidas en decímetros).

        **Requerimiento:** Determine la capacidad volumétrica del molde al hacer girar dicha región alrededor del **eje $Y$** utilizando el **Método de Cascarones Cilíndricos**. *Ventaja analítica:* Aplicar arandelas obligaría a despejar $x = 2 \\pm \\sqrt{4-y}$ en dos ramas; mediante cascarones paralelos al eje $Y$, se integra directamente en función de $x$ con radio $r(x) = x$ y altura $h(x) = 4x - x^2$.
        """)

    a, b = 0.0, 4.0
    f_sym = 4*x - x**2
    # Volumen exacto: V = 2π ∫ x · f(x) dx
    vol_exacto_sym = 2 * sp.pi * sp.integrate(x * f_sym, (x, a, b))
    vol_exacto_num = float(vol_exacto_sym.evalf())

    dx = (b - a) / n_particiones
    vol_aprox = 0.0

    for i in range(n_particiones):
        r_int = a + i * dx
        r_ext = a + (i + 1) * dx
        x_mid = (r_int + r_ext) / 2.0           # Radio medio del cascarón
        altura = 4 * x_mid - x_mid**2           # Altura del cascarón
        vol_aprox += 2 * np.pi * x_mid * altura * dx   # Volumen del cascarón
        if i < limite_visible and altura > 0.01:
            fig.add_traces(crear_cascaron_vertical(r_int, r_ext, 0, altura, color='#2ca02c', opacity=0.6))

    if mostrar_malla:
        x_surf = np.linspace(a, b, 50)
        theta_surf = np.linspace(0, 2*np.pi, 40)
        R_s, THETA_s = np.meshgrid(x_surf, theta_surf)
        Y_s = 4*R_s - R_s**2
        fig.add_trace(go.Surface(x=R_s*np.cos(THETA_s), y=Y_s, z=R_s*np.sin(THETA_s), opacity=0.2, showscale=False, colorscale='Greens'))

    formula_latex = r"V = 2\pi \int_{0}^{4} x(4x - x^2) \, dx = \frac{128\pi}{3}"
    unidades = "dm³"

# --- RENDERIZADO DE RESULTADOS Y GRÁFICO ---
col1, col2 = st.columns([2, 1])

with col1:
    # Gráfico 3D a la izquierda
    fig.update_layout(
        scene=dict(
            xaxis_title="Eje X",
            yaxis_title="Eje Y",
            zaxis_title="Eje Z",
            aspectmode="data"
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=550
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Resultados a la derecha: fórmula, volumen exacto y aproximado
    st.subheader("Cálculo Computacional")
    st.latex(formula_latex)

    st.metric(
        label="Volumen Exacto (Analítico - SymPy)",
        value=f"{vol_exacto_num:.4f} {unidades}",
        delta=f"Exacto: {sp.pretty(vol_exacto_sym)}"
    )

    error_rel = abs(vol_exacto_num - vol_aprox) / vol_exacto_num * 100
    st.metric(
        label=f"Aproximación Numérica (N = {n_particiones})",
        value=f"{vol_aprox:.4f} {unidades}",
        delta=f"Error: {error_rel:.2f}%",
        delta_color="inverse"
    )