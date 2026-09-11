from flask import Flask, render_template, request
from Embarque import conectar_base_datos, descontar_stock

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje = None
    tipo_alerta = None

    if request.method == 'POST':
        try:
            operador = request.form.get('operador', '').strip()
            id_modelo = request.form.get('id_modelo', '').strip()
            cantidad = request.form.get('cantidad', '').strip()

            if not operador or not id_modelo or not cantidad:
                return render_template('index.html', mensaje="Todos los campos son obligatorios", tipo_alerta="error")

            id_mod_int = int(id_modelo)
            cant_int = int(cantidad)

            if cant_int <= 0:
                return render_template('index.html', mensaje="La cantidad debe ser mayor a 0", tipo_alerta="error")

            conexion = conectar_base_datos()
            if not conexion:
                return render_template('index.html', mensaje="Error de conexión con MySQL", tipo_alerta="error")

            # Llama a tu función descontar_stock de Embarque.py
            exito = descontar_stock(conexion, id_mod_int, cant_int, operador)
            conexion.close()

            if exito:
                mensaje = f"Descuento exitoso: {cant_int} pzas del modelo {id_mod_int} despachadas por {operador}."
                tipo_alerta = "exito"
            else:
                mensaje = f"Falló el descuento: Stock insuficiente en patio para el modelo {id_mod_int}."
                tipo_alerta = "error"

        except ValueError:
            mensaje = "El modelo y la cantidad deben ser valores numéricos enteros."
            tipo_alerta = "error"
        except Exception as e:
            mensaje = f"Error: {e}"
            tipo_alerta = "error"

    return render_template('index.html', mensaje=mensaje, tipo_alerta=tipo_alerta)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)