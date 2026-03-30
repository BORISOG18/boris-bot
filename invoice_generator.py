import os
import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

dark_bg  = colors.HexColor('#0D1117')
card_bg  = colors.HexColor('#161B22')
border   = colors.HexColor('#30363D')
orange   = colors.HexColor('#E85D04')
gold     = colors.HexColor('#F9A825')
white    = colors.white
mid_gray = colors.HexColor('#8B949E')
lt_gray  = colors.HexColor('#CDD1D9')
green    = colors.HexColor('#238636')
yellow   = colors.HexColor('#E3B341')

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH  = os.path.join(BASE_DIR, "boris_logo.jpeg")
QR_GPAY    = os.path.join(BASE_DIR, "gpay_qr.jpg")
QR_PHONEPE = os.path.join(BASE_DIR, "phonepe_qr.png")
UPI_ID     = "boris185@fam"   # ← replace with your actual UPI ID

def ps(size=10, color=white, bold=False, align=TA_LEFT):
    return ParagraphStyle('x', fontSize=size, textColor=color,
        fontName='Helvetica-Bold' if bold else 'Helvetica',
        alignment=align, leading=size+4, spaceAfter=2)

def dark_canvas(c, doc):
    c.saveState()
    c.setFillColor(dark_bg)
    c.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    c.restoreState()

def generate_invoice(name, customer_id, item, amount, paid='pending',
                     delivery_date='Pending', delivery_time='Pending', image_path=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
        rightMargin=0.5*inch, leftMargin=0.5*inch,
        topMargin=0.5*inch, bottomMargin=0.5*inch)

    story = []
    invoice_date = datetime.date.today().strftime("%B %d, %Y")
    invoice_num  = f"INV-{datetime.date.today().strftime('%Y%m%d')}-{str(customer_id)[-4:]}"
    is_paid = (paid == 'paid')

    # ── HEADER ──
    try:
        logo = Image(LOGO_PATH, width=1.5*inch, height=1.5*inch)
    except:
        logo = Paragraph("BORIS OG STORE", ps(14, gold, True))

    logo_block = Table([
        [logo, Table([
            [Paragraph("BORIS OG STORE", ps(20, white, True))],
            [Paragraph("BGMI SHOP", ps(9, gold, True))],
            [Paragraph("In-Game Account & Item Sales", ps(8, mid_gray))],
        ], colWidths=[2.8*inch])],
    ], colWidths=[1.6*inch, 2.9*inch])
    logo_block.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BACKGROUND',(0,0),(-1,-1),dark_bg),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
    ]))

    status_text = "<font color='#238636'>● PAID IN FULL</font>" if is_paid else "<font color='#E3B341'>● PAYMENT PENDING</font>"
    invoice_block = Table([
        [Paragraph("INVOICE", ps(30, orange, True, TA_RIGHT))],
        [Paragraph(f"#{invoice_num}", ps(9, mid_gray, align=TA_RIGHT))],
        [Spacer(1,5)],
        [Paragraph(f"Date:  {invoice_date}", ps(9, lt_gray, align=TA_RIGHT))],
        [Paragraph(f"Status:  {status_text}", ps(9, lt_gray, align=TA_RIGHT))],
    ], colWidths=[3.3*inch])
    invoice_block.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),dark_bg),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
    ]))

    header = Table([[logo_block, invoice_block]], colWidths=[4.7*inch, 3.3*inch])
    header.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BACKGROUND',(0,0),(-1,-1),dark_bg),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
    ]))
    story.append(header)
    story.append(HRFlowable(width="100%", thickness=2.5, color=gold, spaceAfter=12))

    # ── CAR IMAGE ──
    if image_path:
        try:
            car = Image(image_path, width=7.4*inch, height=3.0*inch)
            car.hAlign = 'CENTER'
            ct = Table([[car]], colWidths=[7.5*inch])
            ct.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,-1),card_bg),
                ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
                ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
                ('BOX',(0,0),(-1,-1),1,border),
            ]))
            story.append(ct)
            story.append(Spacer(1, 12))
        except:
            pass

    # ── BILL TO / ITEM / PAYMENT ──
    del_color = '#238636' if is_paid else '#E3B341'
    balance_text = "RS 0" if is_paid else f"RS {amount}"
    balance_color = '#238636' if is_paid else '#DA3633'
    amount_label = "Amount Paid:" if is_paid else "Amount Due:"

    info = Table([
        [Paragraph("BILL TO", ps(8,gold,True)), Paragraph("ITEM DETAILS", ps(8,gold,True)), Paragraph("PAYMENT", ps(8,gold,True))],
        [Paragraph(str(name), ps(12,white,True)), Paragraph(str(item), ps(11,white,True)), Paragraph("Method: " + ("Full Payment" if is_paid else "Pending"), ps(10, white if is_paid else yellow))],
        [Paragraph("Customer ID:", ps(8,mid_gray)), Paragraph("Type: In-Game Account", ps(10,lt_gray)), Paragraph(amount_label, ps(8,mid_gray))],
        [Paragraph(str(customer_id), ps(10,white,True)), Paragraph("Platform: BGMI / Game Store", ps(10,lt_gray)), Paragraph(f"RS {amount}", ps(12,gold,True))],
        [Paragraph("", ps(8,mid_gray)), Paragraph(f"<font color='{del_color}'><b>Delivery Date:</b></font>  {delivery_date}", ps(10,white,True)), Paragraph(f"<font color='{balance_color}'>{'● PAID' if is_paid else '● NOT RECEIVED'}</font>", ps(10,white,True))],
        [Paragraph("", ps(8,mid_gray)), Paragraph(f"<font color='{del_color}'><b>Delivery Time:</b></font>  {delivery_time}", ps(10,white,True)), Paragraph(f"Balance: <font color='{balance_color}'>{balance_text}</font>", ps(10,white,True))],
    ], colWidths=[2.3*inch, 3.1*inch, 2.1*inch])
    info.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),card_bg),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('LINEAFTER',(0,0),(1,-1),0.5,border),
        ('BOX',(0,0),(-1,-1),1,border),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LINEBELOW',(0,0),(-1,0),1,gold),
    ]))
    story.append(info)
    story.append(Spacer(1, 12))

    # ── LINE ITEMS ──
    items_rows = [
        [Paragraph("DESCRIPTION", ps(8,gold,True)), Paragraph("QTY", ps(8,gold,True,TA_CENTER)), Paragraph("UNIT PRICE", ps(8,gold,True,TA_RIGHT)), Paragraph("TOTAL", ps(8,gold,True,TA_RIGHT))],
        [Paragraph(str(item), ps(10,white)), Paragraph("1", ps(10,lt_gray,align=TA_CENTER)), Paragraph(f"RS {amount}", ps(10,lt_gray,align=TA_RIGHT)), Paragraph(f"RS {amount}", ps(10,white,True,TA_RIGHT))],
    ]
    lt = Table(items_rows, colWidths=[3.8*inch, 0.6*inch, 1.5*inch, 1.5*inch])
    lt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),dark_bg),
        ('BACKGROUND',(0,1),(-1,-1),card_bg),
        ('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('LINEBELOW',(0,0),(-1,0),1.5,gold),
        ('LINEBELOW',(0,1),(-1,-1),0.5,border),
        ('BOX',(0,0),(-1,-1),1,border),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(lt)
    story.append(Spacer(1, 8))

    # ── TOTALS ──
    received = f"(RS {amount})" if is_paid else "RS 0"
    totals = Table([
        [Paragraph("Total", ps(10,mid_gray,align=TA_RIGHT)), Paragraph(f"RS {amount}", ps(10,white,True,TA_RIGHT))],
        [Paragraph("Amount Received", ps(10,mid_gray,align=TA_RIGHT)), Paragraph(received, ps(10,green,True,TA_RIGHT))],
        [Paragraph("BALANCE DUE", ps(13,white,True,TA_RIGHT)), Paragraph(balance_text, ps(13, green if is_paid else yellow, True, TA_RIGHT))],
    ], colWidths=[5.5*inch, 2*inch])
    totals.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),card_bg),
        ('BACKGROUND',(0,2),(-1,2), colors.HexColor('#0D2818') if is_paid else colors.HexColor('#1C1407')),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),14),
        ('LINEABOVE',(0,2),(-1,2),1,border),
        ('BOX',(0,0),(-1,-1),1,border),
    ]))
    story.append(totals)
    story.append(Spacer(1, 12))

    # ── PENDING NOTICE ──
    if not is_paid:
        notice = Table([[
            Paragraph(f"<font color='#E3B341'><b>⚠  PAYMENT PENDING</b></font>  —  RS {amount} not yet received. Delivery will be confirmed upon payment.", ps(9, lt_gray)),
        ]], colWidths=[7.5*inch])
        notice.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#1C1407')),
            ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
            ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),
            ('BOX',(0,0),(-1,-1),1,yellow),
        ]))
        story.append(notice)
        story.append(Spacer(1, 10))

    # ── QR CODE / SCAN TO PAY ──
    try:
        gpay    = Image(QR_GPAY,    width=1.6*inch, height=1.6*inch)
        phonepe = Image(QR_PHONEPE, width=1.6*inch, height=1.6*inch)

        qr_inner = Table(
            [[gpay, Spacer(0.3*inch, 1), phonepe]],
            colWidths=[1.7*inch, 0.3*inch, 1.7*inch]
        )
        qr_inner.setStyle(TableStyle([
            ('ALIGN',        (0,0),(-1,-1), 'CENTER'),
            ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
            ('BACKGROUND',   (0,0),(-1,-1), card_bg),
            ('TOPPADDING',   (0,0),(-1,-1), 0),('BOTTOMPADDING',(0,0),(-1,-1),0),
            ('LEFTPADDING',  (0,0),(-1,-1), 0),('RIGHTPADDING', (0,0),(-1,-1),0),
        ]))

        gpay_label    = Paragraph("GPay", ps(8, mid_gray, True, TA_CENTER))
        phonepe_label = Paragraph("PhonePe", ps(8, mid_gray, True, TA_CENTER))
        labels = Table(
            [[gpay_label, Spacer(0.3*inch, 1), phonepe_label]],
            colWidths=[1.7*inch, 0.3*inch, 1.7*inch]
        )
        labels.setStyle(TableStyle([
            ('BACKGROUND',    (0,0),(-1,-1), card_bg),
            ('TOPPADDING',    (0,0),(-1,-1), 0),('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('LEFTPADDING',   (0,0),(-1,-1), 0),('RIGHTPADDING', (0,0),(-1,-1),0),
        ]))

        qr_section = Table([
            [Paragraph("SCAN TO PAY (UPI)", ps(10, gold, True, TA_CENTER))],
            [qr_inner],
            [labels],
            [Paragraph(f"UPI ID:  {UPI_ID}", ps(9, lt_gray, True, TA_CENTER))],
        ], colWidths=[7.5*inch])
        qr_section.setStyle(TableStyle([
            ('BACKGROUND',    (0,0),(-1,-1), card_bg),
            ('ALIGN',         (0,0),(-1,-1), 'CENTER'),
            ('TOPPADDING',    (0,0),(-1,-1), 10),
            ('BOTTOMPADDING', (0,0),(-1,-1), 10),
            ('LEFTPADDING',   (0,0),(-1,-1), 14),
            ('RIGHTPADDING',  (0,0),(-1,-1), 14),
            ('BOX',           (0,0),(-1,-1), 1, border),
            ('LINEABOVE',     (0,0),(-1,0),  1.5, gold),
        ]))

        story.append(qr_section)
        story.append(Spacer(1, 12))
    except Exception as e:
        import traceback
        print(f"[QR ERROR] {e}")
        traceback.print_exc()

    # ── FOOTER ──
    ft = Table([[
        Paragraph("BORIS OG STORE — BGMI SHOP", ps(9,mid_gray,True)),
        Paragraph(f"Invoice issued on {invoice_date}  |  {'Payment received. Thank you!' if is_paid else 'Awaiting payment confirmation.'}", ps(9,mid_gray,align=TA_RIGHT)),
    ]], colWidths=[3.75*inch, 3.75*inch])
    ft.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),dark_bg),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('LINEABOVE',(0,0),(-1,0),1.5,gold),
    ]))
    story.append(ft)

    doc.build(story, onFirstPage=dark_canvas, onLaterPages=dark_canvas)
    buffer.seek(0)
    return buffer.read()