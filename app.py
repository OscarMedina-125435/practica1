from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


tareas_memoria = {}

@app.route('/')
def index():
    dias_calendario = []
    nombres_dias = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb']
    

    
    for i, num in enumerate(range(12, 32)):
        fecha_id = f"2026-04-{num}"
        dias_calendario.append({
            "numero": num,
            "nombre": nombres_dias[i % 7],
            "id": fecha_id
        })

    dia_seleccionado = request.args.get('fecha', '2026-04-12')
    tareas_del_dia = tareas_memoria.get(dia_seleccionado, [])

    return render_template('index.html', 
                            dias=dias_calendario, 
                            seleccionado=dia_seleccionado, 
                            tareas=tareas_del_dia)

@app.route('/add', methods=['POST'])
def add():
    fecha = request.form.get('fecha')
    tarea_texto = request.form.get('tarea')
    if tarea_texto:
        if fecha not in tareas_memoria:
            tareas_memoria[fecha] = []
        tareas_memoria[fecha].append({
            "nombre": tarea_texto,
            "status": "pendiente"
        })
    return redirect(url_for('index', fecha=fecha))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('email')
        password = request.form.get('password')
        print(f"Login: {correo}")
        return redirect(url_for('index')) 
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST']) 
def register():
    if request.method == 'POST':
        usuario = request.form.get('username')
        print(f"Registro exitoso: {usuario}")
       
        return redirect(url_for('index')) 
    return render_template('registro.html')


@app.route('/delete/<fecha>/<int:index>')
def delete_task(fecha, index):
    if fecha in tareas_memoria:
        tareas_memoria[fecha].pop(index)
    return redirect(url_for('index', fecha=fecha))





@app.route('/update_status/<fecha>/<int:index>', methods=['POST'])
def update_status(fecha, index):
    nuevo_estado = request.form.get('nuevo_estado')
    if fecha in tareas_memoria:
        tareas_memoria[fecha][index]['status'] = nuevo_estado
    return redirect(url_for('index', fecha=fecha))


if __name__ == '__main__':
    app.run(debug=True)