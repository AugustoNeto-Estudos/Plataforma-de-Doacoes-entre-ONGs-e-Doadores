from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response, current_app
from dao.pedidos import listar_pedidos, atualizar_status_pedido
from dao.itensPedido import exibir_pedidos_itens
from dao.itensLista import consultar_lista_item, atualizar_quantidade_item, deletar_lista_item
from dao.listas import exibir_listas
from dao.itens import exibir_itens
from dao.ong import listar_ongs
from dao.doador import listar_doadores
from dao.intencao_de_doacao import listar_intencoes
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import date
import locale, os

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

pedidos_ong_bp = Blueprint("pedidos_ong", __name__)

STATUS_MAP = {
    0: "Em andamento",
    1: "Finalizado",
    2: "Cancelado"
}

@pedidos_ong_bp.route("/PedidosONG", methods=["GET", "POST"])
def pedidos_ong():
    if "ong_logada" not in session:
        flash("Nenhuma ONG logada. Faça login para continuar.", "warning")
        return redirect(url_for("login_ong.login_ong"))

    status_selecionado = request.form.get("status", "Todos")
    busca = request.form.get("busca", "").strip().lower()

    mapa_itens = {i["ID_Item"]: i for i in exibir_itens()}
    mapa_listas = {l["ID_Lista"]: l for l in exibir_listas()}
    mapa_ongs = {o["CNPJ_ID"]: o for o in listar_ongs()}
    mapa_doadores = {d["CPF_ID"]: d for d in listar_doadores()}
    mapa_intencoes = {i["ID_Intencao"]: i for i in listar_intencoes()}

    pedidos = listar_pedidos()
    meus_pedidos = [p for p in pedidos if p.get("ID_ONG") == session["ong_logada"]["CNPJ_ID"]]

    # Injeta ID_Lista via intenção
    for pedido in meus_pedidos:
        intencao = mapa_intencoes.get(pedido.get("ID_Intencao"))
        if intencao:
            pedido["ID_Lista"] = intencao.get("ID_Lista")

    em_andamento = [p for p in meus_pedidos if p.get("status") == 0]
    finalizados = [p for p in meus_pedidos if p.get("status") == 1]
    cancelados = [p for p in meus_pedidos if p.get("status") == 2]

    def filtrar(lista):
        if not busca:
            return lista
        return [
            p for p in lista
            if busca in mapa_doadores.get(p.get("ID_Doador"), {}).get("nome", "").lower()
            or busca in mapa_listas.get(p.get("ID_Lista"), {}).get("titulo", "").lower()
        ]

    em_andamento, finalizados, cancelados = map(filtrar, [em_andamento, finalizados, cancelados])

    return render_template("pedidosONG.html",
        em_andamento=em_andamento,
        finalizados=finalizados,
        cancelados=cancelados,
        status_selecionado=status_selecionado,
        mapa_listas=mapa_listas,
        mapa_itens=mapa_itens,
        mapa_doadores=mapa_doadores,
        STATUS_MAP=STATUS_MAP,
        busca=busca,
        exibir_pedidos_itens=exibir_pedidos_itens
    )

# Finalizar pedido
@pedidos_ong_bp.route("/FinalizarPedido/<id>")
def finalizar_pedido(id):
    sucesso, msg = atualizar_status_pedido(id, 1)
    if not sucesso:
        flash(msg, "error")
        return redirect(url_for("pedidos_ong.pedidos_ong"))

    pedido = next((p for p in listar_pedidos() if p["ID_Pedido"] == id), None)
    if pedido:
        intencao = next((i for i in listar_intencoes() if i["ID_Intencao"] == pedido["ID_Intencao"]), None)
        if intencao:
            pedido["ID_Lista"] = intencao["ID_Lista"]

        if pedido.get("ID_Lista"):
            itens_pedido = exibir_pedidos_itens(id)
            mapa_itens = {i["ID_Item"]: i for i in exibir_itens()}

            for item in itens_pedido:
                id_lista = str(pedido["ID_Lista"]).strip()
                id_item = str(item["ID_Item"]).strip()
                qtd_pedido = int(item["quantidade"])

                lista_item = consultar_lista_item(id_lista, id_item)
                if lista_item:
                    qtd_atual = int(lista_item["quantidade_necessaria"].strip())
                    nova_qtd = max(qtd_atual - qtd_pedido, 0)

                    if nova_qtd == 0:
                        deletar_lista_item(id_lista, id_item)
                        nome_item = mapa_itens.get(id_item, {}).get("categoria", "Item")
                        flash(
                            f"Item '{nome_item}' foi removido da lista pois a quantidade necessária foi zerada.",
                            "info"
                        )
                    else:
                        atualizar_quantidade_item(id_lista, id_item, str(nova_qtd))

    flash("Pedido finalizado e estoque da lista atualizado.", "success")
    return redirect(url_for("pedidos_ong.pedidos_ong"))

# Cancelar pedido
@pedidos_ong_bp.route("/CancelarPedido/<id>")
def cancelar_pedido(id):
    sucesso, msg = atualizar_status_pedido(id, 2)
    flash("Pedido cancelado com sucesso.", "success") if sucesso else flash(msg, "error")
    return redirect(url_for("pedidos_ong.pedidos_ong"))

# Gerar recibo em PDF
@pedidos_ong_bp.route("/Recibo/<id_pedido>", methods=["POST"])
def gerar_recibo(id_pedido):
    pedido = next((p for p in listar_pedidos() if p["ID_Pedido"] == id_pedido), None)
    if not pedido:
        return "Pedido não encontrado", 404

    itens = exibir_pedidos_itens(id_pedido)
    mapa_itens = {i["ID_Item"]: i for i in exibir_itens()}
    doador = next((d for d in listar_doadores() if d["CPF_ID"] == pedido["ID_Doador"]), {})
    ong = next((o for o in listar_ongs() if o["CNPJ_ID"] == pedido["ID_ONG"]), {})

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    logo_path = os.path.join(current_app.root_path, "static", "img", "SolidariHub_logo.png")
    pdf.drawImage(logo_path, 50, y-10, width=60, height=60, mask='auto')

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, y, "RECIBO DE DOAÇÃO")
    y -= 10
    pdf.line(50, y, width - 50, y)
    y -= 30

    # Informações da ONG
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Informações da ONG:")
    y -= 20
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Nome: {ong.get('nome', 'ONG')}")
    y -= 20
    pdf.drawString(50, y, f"CNPJ: {ong.get('CNPJ_ID', '')}")
    y -= 20
    responsavel = request.form.get("responsavel", "Responsável")
    pdf.drawString(50, y, f"Responsável: {responsavel}")
    y -= 30

     # Informações do doador
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Informações do Doador:")
    y -= 20
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Nome: {doador.get('nome', 'Doador')}")
    y -= 30

    # Itens doados
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Itens Doado(s):")
    y -= 20
    pdf.setFont("Helvetica", 12)
    for item in itens:
        det = mapa_itens.get(item["ID_Item"], {})
        nome_item = f"{det.get('categoria', 'Item')} - {det.get('subcategoria', '')}".strip(" -")
        pdf.drawString(60, y, f"{item['quantidade']}x")
        pdf.drawString(100, y, nome_item)
        y -= 20

        if item.get("observacao"):
            pdf.setFont("Helvetica-Oblique", 10)
            pdf.drawString(80, y, f"Obs: {item['observacao']}")
            y -= 20
            pdf.setFont("Helvetica", 12)

        # Quebra de página se necessário
        if y < 100:
            pdf.showPage()
            y = height - 50

    # Mensagem de agradecimento
    y -= 30
    pdf.setFont("Helvetica-Oblique", 12)
    pdf.drawCentredString(width / 2, y, "Agradecemos imensamente a sua doação.")
    y -= 20
    pdf.drawCentredString(width / 2, y, "Sua contribuição é fundamental para continuarmos levando apoio e esperança.")
    y -= 40

    # Local, data e assinatura
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Local e Data: São Paulo, {date.today().strftime('%d de %B de %Y')}")
    y -= 60
    pdf.drawString(50, y, "__________________________")
    pdf.drawString(50, y - 15, "Assinatura da ONG")
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(50, y - 35, "[Espaço reservado para timbre institucional]")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=recibo.pdf'
    return response