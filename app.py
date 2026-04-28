from flask import Flask, render_template, request, redirect, url_for, session, flash
import gestortareas  

app = Flask(__name__)

app.secret_key = 'mi_llave_secreta_super_segura'


gestor_obj = gestortareas.GestorTareas("mongodb://127.0.0.1:27017/")


tareas_memoria = {}

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

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
                            tareas=tareas_del_dia,
                            nombre_usuario=session.get('nombre'))

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
        e = request.form.get('email')
        s = request.form.get('secreto')
    
        user_data = gestor_obj.obtener_usuario_por_email(e)
        
        if user_data and user_data['secreto'] == s:
            # Iniciamos sesión
            session['user_id'] = str(user_data['_id'])
            session['nombre'] = user_data['user']
            return redirect(url_for('index'))
        else:
            flash('Datos incorrectos.')
            return render_template('login.html')
            
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST']) 
def register():
    if request.method == 'POST':
        u = request.form.get('username')
        e = request.form.get('email')
        s = request.form.get('secreto')
        
        if gestor_obj.crear_usuario(u, e, s):
            flash('¡Cuenta creada! Ahora inicia sesión.')
            return redirect(url_for('login'))
        else:
            flash('El correo ya existe.')
            return render_template('registro.html')
            
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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