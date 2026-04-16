from flask import Flask, render_template, request, redirect

app = Flask(__name__)

dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

cuadros = []

tareas = [
    {"nombre": "Hacer tarea de mate", "hecho": False},
    {"nombre": "Practicar baile", "hecho": False},
    {"nombre": "Estudiar programación", "hecho": False}
]

@app.route("/", methods=["GET", "POST"])
def index():
    global cuadros

    if request.method == "POST":

        # Crear nuevo cuadro (materia)
        if "nuevo_cuadro" in request.form:
            titulo = request.form["nuevo_cuadro"]

            if titulo:
                cuadros.append({
                    "titulo": titulo,
                    "dias": [{"nombre": d, "hecho": False} for d in dias_semana]
                })

        # Marcar día
        elif "toggle" in request.form:
            c = int(request.form["cuadro"])
            d = int(request.form["toggle"])

            cuadros[c]["dias"][d]["hecho"] = not cuadros[c]["dias"][d]["hecho"]

        return redirect("/")

    return render_template("index.html", cuadros=cuadros)

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

if __name__ == "__main__":
    app.run(debug=True)