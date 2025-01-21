from flask import Flask, request, send_file
from flask_cors import CORS
from descompactador import descompactar 
from compactador import compactador


@app.route('/compactar', methods=['POST'])
def compactar_arquivo():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400

    arquivo = request.files['file']

    arquivo_path = "arquivo_temporario"
    arquivo.save(arquivo_path)
    arquivo_codificado = '/tmp/arquivo_codificado'

    compactar(arquivo_path)

    return send_file(arquivo_codificado, as_attachment=True, download_name="arquivo_compactado")

@app.route('/descompactar', methods=['POST'])
def descompactar_arquivo():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400

    arquivo = request.files['file']

    arquivo_path = "arquivo_restaurado"
    arquivo.save(arquivo_path)
    arquivo_restaurado = '/tmp/arquivo_restaurado'

    descompactar(arquivo_path, arquivo_restaurado)

    return send_file(arquivo_restaurado, as_attachment=True, download_name="arquivo_restaurado.txt")

if __name__ == '__main__':
    app.run(debug=True, port=3000)