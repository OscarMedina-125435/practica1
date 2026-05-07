from flask import Flask, render_template, request, redirect, url_for, session, flash
import gestortareas 

app = Flask(__name__)

app.secret_key = 'mi_llave_secreta_super_segura'


gestor_obj = gestortareas.GestorTareas("mongodb://127.0.0.1:27017/")




@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

  
    dias_calendario = []
    nombres_dias = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb']
    for i, num in enumerate(range(12, 32)):
        dias_calendario.append({
            "numero": num,
            "nombre": nombres_dias[i % 7],
            "id": f"2026-04-{num}"
        })

    dia_seleccionado = request.args.get('fecha', '2026-04-12')
    todas_mis_tareas = gestor_obj.obtener_tareas_usuario(session['user_id'])
    tareas_del_dia = [t for t in todas_mis_tareas if t.get('fecha_display') == dia_seleccionado]

    return render_template('index.html', 
                            dias=dias_calendario, 
                            seleccionado=dia_seleccionado, 
                            tareas=tareas_del_dia,
                            nombre_usuario=session.get('nombre'))


@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    fecha = request.form.get('fecha')
    tarea_texto = request.form.get('tarea')
    
    if tarea_texto:
        gestor_obj.crear_tarea(session['user_id'], tarea_texto, fecha)
        
    return redirect(url_for('index', fecha=fecha))

@app.route('/update_status/<tarea_id>/<fecha>', methods=['POST'])
def update_status(tarea_id, fecha):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    nuevo_estado = request.form.get('nuevo_estado')
    gestor_obj.actualizar_estado_tarea(tarea_id, nuevo_estado)
    return redirect(url_for('index', fecha=fecha))

@app.route('/delete/<tarea_id>/<fecha>')
def delete_task(tarea_id, fecha):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    gestor_obj.eliminar_tarea(tarea_id)
    return redirect(url_for('index', fecha=fecha))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        e = request.form.get('email')
        s = request.form.get('secreto')
        user_data = gestor_obj.obtener_usuario_por_email(e)
        
        if user_data and user_data['secreto'] == s:
            session['user_id'] = str(user_data['_id'])
            session['nombre'] = user_data['user']
            return redirect(url_for('index'))
        else:
            flash('Datos incorrectos.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST']) 
def register():
    if request.method == 'POST':
        u = request.form.get('username')
        e = request.form.get('email')
        s = request.form.get('secreto')
        if gestor_obj.crear_usuario(u, e, s):
            flash('¡Cuenta creada! Inicia sesión.')
            return redirect(url_for('login'))
        else:
            flash('El correo ya existe.')
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)