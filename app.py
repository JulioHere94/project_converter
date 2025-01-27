import os
import time
import pandas as pd
from flask import Flask, render_template, request, send_file, after_this_request

app = Flask(__name__)

# Função para garantir que um diretório exista
def garantir_diretorio(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Rota principal
@app.route("/")
def index():
    return render_template("index.html")

# Rota para conversão de arquivos
@app.route("/convert", methods=["POST"])
def upload():
    try:
        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']
        
        # Verificar se a chave conversionType está presente
        output_format = request.form.get('conversionType')
        if not output_format:
            return "Formato de conversão inválido", 400

        # Usar o nome do arquivo original
        original_filename = file.filename
        upload_dir = os.path.join('static', 'uploads')
        converted_dir = os.path.join('static', 'converted')

        # Garantir que os diretórios existam
        garantir_diretorio(upload_dir)
        garantir_diretorio(converted_dir)

        file_path = os.path.join(upload_dir, original_filename)

        # Salvar o arquivo temporário
        file.save(file_path)

        try:
            if output_format == 'excel_to_csv':
                # Verificar se o arquivo é Excel (extensão .xlsx)
                if not original_filename.endswith('.xlsx'):
                    return "Arquivo Excel inválido", 400
                
                # Converte de Excel para CSV
                df = pd.read_excel(file_path)
                output_file = os.path.join(converted_dir, original_filename.replace('.xlsx', '.csv'))
                df.to_csv(output_file, index=False)

            elif output_format == 'csv_to_excel':
                # Verificar se o arquivo é CSV (extensão .csv)
                if not original_filename.endswith('.csv'):
                    return "Arquivo CSV inválido", 400

                # Converte de CSV para Excel
                df = pd.read_csv(file_path)
                output_file = os.path.join(converted_dir, original_filename.replace('.csv', '.xlsx'))
                df.to_excel(output_file, index=False)

            else:
                return "Formato de conversão inválido", 400

            # Remove todos os arquivos temporários e convertidos após o download
            @after_this_request
            def remove_files(response):
                try:
                    time.sleep(1)  # Pequeno tempo de espera para garantir que o arquivo seja liberado
                    os.remove(file_path)
                    os.remove(output_file)
                except Exception as e:
                    print(f"Erro ao remover arquivos: {str(e)}")
                return response

            # Envia o arquivo convertido para o cliente
            return send_file(output_file, as_attachment=True)

        except Exception as e:
            return f"Erro na conversão: {str(e)}", 500

    except Exception as e:
        return f"Erro na requisição: {str(e)}", 400


if __name__ == "__main__":
    app.run(debug=True)
















