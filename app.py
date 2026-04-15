from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Datos en memoria (simples)
tareas = [
    {"nombre": "Hacer tarea de mate", "hecho": False},
    {"nombre": "Practicar baile", "hecho": False},
    {"nombre": "Estudiar programación", "hecho": False}
]

@app.route("/", methods=["GET", "POST"])
def index():
    global tareas

    if request.method == "POST":
        if "nueva_tarea" in request.form:
            nueva = request.form["nueva_tarea"]
            if nueva:
                tareas.append({"nombre": nueva, "hecho": False})

        elif "toggle" in request.form:
            i = int(request.form["toggle"])
            tareas[i]["hecho"] = not tareas[i]["hecho"]

        return redirect("/")

    return render_template("index.html", tareas=tareas)

if __name__ == "__main__":
    app.run(debug=True)